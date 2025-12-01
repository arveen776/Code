"""Screen understanding capabilities: OCR, window detection, and element identification."""

import time
from typing import Dict, List, Optional, Tuple

try:
    import pyautogui
    from PIL import Image
except ImportError as exc:
    raise SystemExit(
        "Missing dependencies. Install with: pip install pyautogui pillow"
    ) from exc

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    # Don't print warning here - it will be printed when needed

try:
    import win32gui
    import win32con
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False
    # Don't print warning here - it will be handled gracefully

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_active_window() -> Dict[str, str]:
    """Get information about the currently active window."""
    if not WINDOWS_API_AVAILABLE:
        return {"app": "unknown", "title": "unknown"}
    
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        
        # Try to get process name
        _, pid = win32gui.GetWindowThreadProcessId(hwnd)
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process(pid)
                app = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                app = "unknown"
        else:
            app = "unknown"
        
        return {"app": app, "title": title, "hwnd": str(hwnd)}
    except Exception:
        return {"app": "unknown", "title": "unknown"}


def capture_screen_region(x: int, y: int, width: int = 200, height: int = 50) -> Optional[Image.Image]:
    """Capture a region around a point on the screen."""
    try:
        # Capture region around the point
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)
        right = left + width
        bottom = top + height
        
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        return screenshot
    except Exception:
        return None


def extract_text_near_point(x: int, y: int, region_width: int = 200, region_height: int = 50) -> str:
    """Extract text from screen region near a point using OCR."""
    if not TESSERACT_AVAILABLE:
        return ""
    
    try:
        image = capture_screen_region(x, y, region_width, region_height)
        if image is None:
            return ""
        
        # Use OCR to extract text
        text = pytesseract.image_to_string(image, config='--psm 7')
        return text.strip()
    except Exception as e:
        # Silently fail - OCR is optional
        return ""


def find_text_on_screen(text: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
    """Find text on screen using OCR and return its approximate location."""
    if not TESSERACT_AVAILABLE:
        return None
    
    try:
        # Take full screenshot
        screenshot = pyautogui.screenshot()
        
        # Use OCR to find text location
        # This is a simplified approach - in production, you'd want more sophisticated text matching
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        
        # Search for the text
        for i, word in enumerate(data.get('text', [])):
            if text.lower() in word.lower() and float(data.get('conf', [0])[i]) > confidence * 100:
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                return (x, y)
        
        return None
    except Exception:
        return None


def find_element_by_semantic_description(description: str, context: Optional[Dict] = None) -> Optional[Tuple[int, int]]:
    """
    Find a UI element by semantic description.
    
    This uses OCR and heuristics to find elements based on what they are,
    not just coordinates.
    """
    if not TESSERACT_AVAILABLE:
        return None
    
    try:
        # Extract key terms from description
        # Simple keyword extraction - could be enhanced with NLP
        keywords = description.lower().split()
        
        # Common UI element keywords
        action_words = ['click', 'button', 'field', 'input', 'text', 'menu', 'option']
        keywords = [k for k in keywords if k not in action_words and len(k) > 2]
        
        if not keywords:
            return None
        
        # Try to find the most distinctive keyword on screen
        for keyword in keywords[:3]:  # Try top 3 keywords
            location = find_text_on_screen(keyword, confidence=0.7)
            if location:
                return location
        
        return None
    except Exception:
        return None


def get_screen_context(x: int, y: int) -> Dict[str, object]:
    """Get rich context about a point on the screen."""
    context = {
        "window": get_active_window(),
        "timestamp": time.time(),
    }
    
    # Extract text near the point
    ocr_text = extract_text_near_point(x, y)
    if ocr_text:
        context["ocr_text"] = ocr_text
    
    # Capture a small screenshot for visual reference
    try:
        image = capture_screen_region(x, y, 100, 30)
        if image:
            # Store image dimensions for reference
            context["region"] = {
                "x": max(0, x - 50),
                "y": max(0, y - 15),
                "width": 100,
                "height": 30
            }
    except Exception:
        pass
    
    return context

