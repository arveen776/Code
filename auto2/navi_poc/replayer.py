import time
from typing import Dict, Iterable, List

try:
    import pyautogui
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(
        "Missing dependency 'pyautogui'. Install it with `pip install pyautogui`."
    ) from exc

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


def replay(events: Iterable[Event]) -> None:
    """Replay a list of recorded events sequentially."""
    events_list: List[Event] = list(events)
    if not events_list:
        print("No events to replay.")
        return

    previous_time = 0.0
    for event in events_list:
        event_time = float(event.get("t", previous_time))
        delay = max(0.0, event_time - previous_time)
        if delay:
            time.sleep(delay)
        previous_time = event_time

        event_type = event.get("type")
        if event_type == "mouse_move":
            _move_mouse(event)
        elif event_type == "mouse_click":
            _handle_click(event)
        elif event_type == "mouse_scroll":
            _handle_scroll(event)
        elif event_type == "key_press":
            _handle_key(event, press=True)
        elif event_type == "key_release":
            _handle_key(event, press=False)
        else:
            print(f"Skipping unknown event: {event_type}")


def _move_mouse(event: Event) -> None:
    pyautogui.moveTo(event.get("x"), event.get("y"), duration=0)


def _handle_click(event: Event) -> None:
    x, y = event.get("x"), event.get("y")
    button = (event.get("button") or "left").replace("Button.", "")
    pressed = bool(event.get("pressed", True))

    if pressed:
        pyautogui.mouseDown(x, y, button=button)
    else:
        pyautogui.mouseUp(x, y, button=button)


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

