import time
from typing import Dict, Iterable, List, Optional, Tuple

try:
    import pyautogui
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(
        "Missing dependency 'pyautogui'. Install it with `pip install pyautogui`."
    ) from exc

from screen_understanding import (
    find_text_on_screen,
    find_element_by_semantic_description,
    get_active_window,
)
from action_analyzer import ActionAnalyzer

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

Event = Dict[str, object]


KEY_ALIASES = {
    "Key.space": "space",
    "Key.enter": "enter",
    "Key.backspace": "backspace",
    "Key.tab": "tab",
    "Key.shift": "shift",
    "Key.ctrl_l": "ctrlleft",
    "Key.ctrl_r": "ctrlright",
    "Key.alt_l": "altleft",
    "Key.alt_r": "altright",
}


def replay(events: Iterable[Event], intelligent: bool = True) -> None:
    """
    Replay a list of recorded events sequentially.
    
    If intelligent=True, uses semantic understanding to find elements
    instead of fixed coordinates.
    """
    events_list: List[Event] = list(events)
    if not events_list:
        print("No events to replay.")
        return

    analyzer = ActionAnalyzer(use_llm=intelligent) if intelligent else None
    
    # Analyze events first to understand the workflow
    if intelligent and analyzer:
        try:
            print("Analyzing workflow...")
            understanding = analyzer.understand_workflow(events_list)
            print(f"Workflow: {understanding.get('summary', 'Unknown workflow')}")
            apps = understanding.get('applications_used', [])
            if apps:
                print(f"Applications: {', '.join(apps)}")
            print()
        except Exception as e:
            print(f"Warning: Workflow analysis failed: {e}")
            print("Continuing with basic replay...\n")

    previous_time = 0.0
    for event in events_list:
        event_time = float(event.get("t", previous_time))
        delay = max(0.0, event_time - previous_time)
        if delay:
            time.sleep(delay)
        previous_time = event_time

        event_type = event.get("type")
        if event_type == "mouse_move":
            _move_mouse(event, intelligent)
        elif event_type == "mouse_click":
            _handle_click(event, intelligent, analyzer if intelligent else None)
        elif event_type == "mouse_scroll":
            _handle_scroll(event)
        elif event_type == "key_press":
            _handle_key(event, press=True)
        elif event_type == "key_release":
            _handle_key(event, press=False)
        elif event_type == "window_change":
            # Note window changes but don't try to switch windows
            window = event.get("window", {})
            print(f"[Window: {window.get('app', 'unknown')} - {window.get('title', 'unknown')}]")
        else:
            print(f"Skipping unknown event: {event_type}")


def _move_mouse(event: Event, intelligent: bool = False) -> None:
    """Move mouse, using intelligent positioning if available."""
    x = event.get("x")
    y = event.get("y")
    
    if intelligent and (x is None or y is None):
        # Try to infer position from context
        ocr_text = event.get("ocr_text", "")
        if ocr_text:
            location = find_text_on_screen(ocr_text)
            if location:
                x, y = location
    
    if x is not None and y is not None:
        pyautogui.moveTo(x, y, duration=0.1)  # Slight duration for natural movement


def _handle_click(event: Event, intelligent: bool = False, analyzer: Optional[ActionAnalyzer] = None) -> None:
    """Handle mouse click, using intelligent element finding if available."""
    x = event.get("x")
    y = event.get("y")
    button = (event.get("button") or "left").replace("Button.", "")
    pressed = bool(event.get("pressed", True))
    
    # Intelligent element finding
    if intelligent:
        # Try to find element by semantic description
        ocr_text = event.get("ocr_text", "")
        semantic_target = event.get("semantic_target", "")
        
        if ocr_text or semantic_target:
            # Try to find the element on screen
            target_text = ocr_text if ocr_text else semantic_target
            
            # Extract meaningful text (remove common words)
            meaningful_text = _extract_meaningful_text(target_text)
            if meaningful_text:
                location = find_text_on_screen(meaningful_text, confidence=0.7)
                if location:
                    x, y = location
                    print(f"[Found element: '{meaningful_text}' at ({x}, {y})]")
                else:
                    # Try semantic description
                    location = find_element_by_semantic_description(semantic_target)
                    if location:
                        x, y = location
                        print(f"[Found element semantically: '{semantic_target}' at ({x}, {y})]")
        
        # If we still don't have coordinates, use original
        if x is None or y is None:
            x = event.get("x")
            y = event.get("y")
            if x and y:
                print(f"[Using original coordinates: ({x}, {y})]")
    
    if x is not None and y is not None:
        # Move to position first
        pyautogui.moveTo(x, y, duration=0.1)
        time.sleep(0.05)  # Small pause for stability
        
        if pressed:
            pyautogui.mouseDown(x, y, button=button)
        else:
            pyautogui.mouseUp(x, y, button=button)
    else:
        print(f"[Warning: Could not determine click location for event]")


def _extract_meaningful_text(text: str) -> Optional[str]:
    """Extract meaningful words from OCR text, filtering out common UI words."""
    if not text:
        return None
    
    # Common words to filter out
    filter_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "click", "button", "field", "input", "text", "menu", "option"
    }
    
    words = text.lower().split()
    meaningful = [w for w in words if w not in filter_words and len(w) > 2]
    
    # Return the longest meaningful word or phrase
    if meaningful:
        # Try to return a phrase of 2-3 words
        if len(meaningful) >= 2:
            return " ".join(meaningful[:2])
        return meaningful[0]
    
    return text[:20] if text else None


def _handle_scroll(event: Event) -> None:
    dx = int(event.get("dx", 0))
    dy = int(event.get("dy", 0))
    pyautogui.scroll(dy)
    if dx:
        pyautogui.hscroll(dx)


def _handle_key(event: Event, press: bool) -> None:
    key = str(event.get("key", ""))
    key = KEY_ALIASES.get(key, key)

    if len(key) == 1:
        if press:
            pyautogui.keyDown(key)
        else:
            pyautogui.keyUp(key)
    else:
        normalized = key.replace("Key.", "")
        if press:
            pyautogui.keyDown(normalized)
        else:
            pyautogui.keyUp(normalized)

