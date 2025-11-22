import base64
import io
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from pynput import keyboard, mouse
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(
        "Missing dependency 'pynput'. Install it with `pip install pynput`."
    ) from exc

try:
    import pygetwindow as gw
    WINDOW_TRACKING_AVAILABLE = True
except ImportError:
    WINDOW_TRACKING_AVAILABLE = False

try:
    from PIL import Image, ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


Event = Dict[str, object]


class Recorder:
    """Capture mouse and keyboard activity with rich context until stopped."""

    def __init__(
        self,
        capture_screenshots: bool = True,
        capture_ocr: bool = True,
        screenshot_region_size: int = 200,
    ) -> None:
        """
        Initialize the recorder.
        
        Args:
            capture_screenshots: Whether to capture screenshots at key moments
            capture_ocr: Whether to extract text from screenshots (requires OCR)
            screenshot_region_size: Size of region around click to capture (pixels)
        """
        self.events: List[Event] = []
        self.start_time: Optional[float] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()
        self._should_stop = False
        
        # Context capture settings
        self.capture_screenshots = capture_screenshots and SCREENSHOT_AVAILABLE
        self.capture_ocr = capture_ocr and OCR_AVAILABLE and self.capture_screenshots
        self.screenshot_region_size = screenshot_region_size
        
        # Track current window context
        self._last_window_context: Optional[Dict[str, str]] = None
        self._last_context_check: float = 0.0
        self._context_check_interval: float = 0.5  # Check window every 0.5s

    # --------------------------------------------------------------------- API
    def start(self) -> None:
        """Start recording events."""
        if self.start_time is not None:
            raise RuntimeError("Recorder already running.")

        self.events = []
        self.start_time = time.time()
        self._last_window_context = None
        self._last_context_check = 0.0
        self._should_stop = False

        # Record initial context
        self._record_context_event("recording_start")

        self._mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
            suppress=False,  # Don't suppress keys so ESC can be detected
        )

        self._mouse_listener.start()
        self._keyboard_listener.start()

    def should_stop(self) -> bool:
        """Check if recording should stop (e.g., ESC was pressed)."""
        with self._lock:
            return self._should_stop
    
    def stop(self) -> List[Event]:
        """Stop recording and return the captured events."""
        if self.start_time is None:
            raise RuntimeError("Recorder not running.")

        # Record final context
        self._record_context_event("recording_stop")

        for listener in (self._mouse_listener, self._keyboard_listener):
            if listener is not None:
                listener.stop()
                listener.join()

        self._mouse_listener = None
        self._keyboard_listener = None

        events = list(self.events)
        self.events = []
        self.start_time = None
        self._should_stop = False
        return events

    # ----------------------------------------------------------------- Helpers
    def _elapsed(self) -> float:
        assert self.start_time is not None
        return time.time() - self.start_time

    def _record(self, event: Event) -> None:
        """Record an event with timestamp and current context."""
        with self._lock:
            event["t"] = round(float(event.get("t", self._elapsed())), 6)
            
            # Add window context if available and changed
            context = self._get_window_context()
            if context:
                event["window"] = context
            
            self.events.append(event)

    def _get_window_context(self) -> Optional[Dict[str, str]]:
        """Get current active window context."""
        if not WINDOW_TRACKING_AVAILABLE:
            return None
        
        # Throttle window checks
        now = time.time()
        if now - self._last_context_check < self._context_check_interval:
            return self._last_window_context
        
        self._last_context_check = now
        
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                context = {
                    "title": active_window.title or "",
                    "app": active_window.app or "",
                }
                
                # Only update if changed
                if context != self._last_window_context:
                    self._last_window_context = context
                
                return context
        except Exception:
            pass
        
        return self._last_window_context

    def _record_context_event(self, event_type: str) -> None:
        """Record a context event (window change, recording start/stop)."""
        context = self._get_window_context()
        event: Event = {
            "type": event_type,
        }
        if context:
            event["window"] = context
        self._record(event)

    def _capture_screenshot_region(
        self, x: int, y: int, width: int, height: int
    ) -> Optional[str]:
        """Capture a region of the screen and return as base64 encoded image."""
        if not self.capture_screenshots:
            return None
        
        try:
            # Calculate region bounds
            left = max(0, x - width // 2)
            top = max(0, y - height // 2)
            right = x + width // 2
            bottom = y + height // 2
            
            # Capture screenshot
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            
            return img_base64
        except Exception as e:
            # Silently fail - screenshots are optional
            return None

    def _extract_text_from_image(self, img_base64: str) -> Optional[str]:
        """Extract text from a base64 encoded image using OCR."""
        if not self.capture_ocr:
            return None
        
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(img_base64)
            img = Image.open(io.BytesIO(img_bytes))
            
            # Extract text
            text = pytesseract.image_to_string(img).strip()
            return text if text else None
        except Exception:
            return None

    # --------------------------------------------------------------- Listeners
    def _on_move(self, x: int, y: int) -> None:
        try:
            # Don't record every mouse move - too noisy
            # Only record if window context changed
            context = self._get_window_context()
            if context != self._last_window_context:
                self._record_context_event("window_change")
            # Optionally record significant moves (if needed later)
        except Exception:
            # Don't let exceptions stop the listener
            pass

    def _on_click(
        self, x: int, y: int, button: mouse.Button, pressed: bool
    ) -> None:
        try:
            button_name = button.name if hasattr(button, 'name') else str(button)
            event: Event = {
                "type": "mouse_click",
                "x": x,
                "y": y,
                "button": button_name,
                "pressed": pressed,
            }
            
            # Capture screenshot and OCR on click release (when action completes)
            if not pressed:  # On button release
                screenshot = self._capture_screenshot_region(
                    x, y, self.screenshot_region_size, self.screenshot_region_size
                )
                if screenshot:
                    event["screenshot"] = screenshot
                    
                    # Extract text from screenshot
                    if self.capture_ocr:
                        text = self._extract_text_from_image(screenshot)
                        if text:
                            event["ocr_text"] = text
            
            self._record(event)
        except Exception:
            # Don't let exceptions stop the listener
            # Silently continue recording other events
            pass

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        try:
            event: Event = {
                "type": "mouse_scroll",
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
            }
            self._record(event)
        except Exception:
            # Don't let exceptions stop the listener
            pass

    def _on_key_press(self, key: keyboard.KeyCode | keyboard.Key) -> None:
        # Check for ESC key FIRST, before any other processing
        # This ensures ESC detection works even if other code fails
        try:
            is_esc = False
            if isinstance(key, keyboard.Key) and key == keyboard.Key.esc:
                is_esc = True
            elif str(key) == "Key.esc" or str(key).startswith("<Key.esc"):
                is_esc = True
            
            if is_esc:
                with self._lock:
                    self._should_stop = True
                print("\n[ESC detected - stopping recording...]", flush=True)
                return  # Don't record ESC key press
        except Exception:
            # If ESC detection fails, try to continue anyway
            pass
        
        # Process other key presses
        try:
            
            # Normalize key for recording
            key_str = self._normalize_key(key)
            event: Event = {
                "type": "key_press",
                "key": key_str,
            }
            
            # Capture screenshot for important keys (Enter, Tab, etc.)
            if key_str in ["Key.enter", "Key.tab", "Key.space"]:
                try:
                    import pyautogui
                    x, y = pyautogui.position()
                    screenshot = self._capture_screenshot_region(
                        x, y, self.screenshot_region_size, self.screenshot_region_size
                    )
                    if screenshot:
                        event["screenshot"] = screenshot
                        if self.capture_ocr:
                            text = self._extract_text_from_image(screenshot)
                            if text:
                                event["ocr_text"] = text
                except Exception:
                    pass
            
            self._record(event)
        except Exception:
            # Don't let exceptions stop the listener
            pass

    def _on_key_release(self, key: keyboard.KeyCode | keyboard.Key) -> None:
        try:
            self._record(
                {
                    "type": "key_release",
                    "key": self._normalize_key(key),
                }
            )
        except Exception:
            # Don't let exceptions stop the listener
            pass

    @staticmethod
    def _normalize_key(key: keyboard.KeyCode | keyboard.Key) -> str:
        try:
            return key.char  # type: ignore[return-value]
        except AttributeError:
            return str(key)
