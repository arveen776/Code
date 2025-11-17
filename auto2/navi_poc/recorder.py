import threading
import time
from typing import Dict, List, Optional

try:
    from pynput import keyboard, mouse
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(
        "Missing dependency 'pynput'. Install it with `pip install pynput`."
    ) from exc


Event = Dict[str, object]


class Recorder:
    """Capture mouse and keyboard activity until stopped."""

    def __init__(self) -> None:
        self.events: List[Event] = []
        self.start_time: Optional[float] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()

    # --------------------------------------------------------------------- API
    def start(self) -> None:
        """Start recording events."""
        if self.start_time is not None:
            raise RuntimeError("Recorder already running.")

        self.events = []
        self.start_time = time.time()

        self._mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )

        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self) -> List[Event]:
        """Stop recording and return the captured events."""
        if self.start_time is None:
            raise RuntimeError("Recorder not running.")

        for listener in (self._mouse_listener, self._keyboard_listener):
            if listener is not None:
                listener.stop()
                listener.join()

        self._mouse_listener = None
        self._keyboard_listener = None

        events = list(self.events)
        self.events = []
        self.start_time = None
        return events

    # ----------------------------------------------------------------- Helpers
    def _elapsed(self) -> float:
        assert self.start_time is not None
        return time.time() - self.start_time

    def _record(self, event: Event) -> None:
        with self._lock:
            event["t"] = round(float(event.get("t", self._elapsed())), 6)
            self.events.append(event)

    # --------------------------------------------------------------- Listeners
    def _on_move(self, x: int, y: int) -> None:
        self._record({"type": "mouse_move", "x": x, "y": y})

    def _on_click(
        self, x: int, y: int, button: mouse.Button, pressed: bool
    ) -> None:
        self._record(
            {
                "type": "mouse_click",
                "x": x,
                "y": y,
                "button": button.name,
                "pressed": pressed,
            }
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        self._record({"type": "mouse_scroll", "x": x, "y": y, "dx": dx, "dy": dy})

    def _on_key_press(self, key: keyboard.KeyCode | keyboard.Key) -> None:
        self._record(
            {
                "type": "key_press",
                "key": self._normalize_key(key),
            }
        )

    def _on_key_release(self, key: keyboard.KeyCode | keyboard.Key) -> None:
        self._record(
            {
                "type": "key_release",
                "key": self._normalize_key(key),
            }
        )

    @staticmethod
    def _normalize_key(key: keyboard.KeyCode | keyboard.Key) -> str:
        try:
            return key.char  # type: ignore[return-value]
        except AttributeError:
            return str(key)

