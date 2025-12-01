import threading
import time
from typing import Dict, List, Optional

try:
    from pynput import keyboard, mouse
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(
        "Missing dependency 'pynput'. Install it with `pip install pynput`."
    ) from exc

from screen_understanding import get_active_window, get_screen_context


Event = Dict[str, object]


class Recorder:
    """Capture mouse and keyboard activity until stopped."""

    def __init__(self, capture_context: bool = True) -> None:
        self.events: List[Event] = []
        self.start_time: Optional[float] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()
        self._should_stop = False
        self.capture_context = capture_context
        self._last_window: Optional[Dict] = None

    # --------------------------------------------------------------------- API
    def start(self) -> None:
        """Start recording events."""
        if self.start_time is not None:
            raise RuntimeError("Recorder already running.")

        self.events = []
        self.start_time = time.time()
        self._should_stop = False

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
        with self._lock:
            event["t"] = round(float(event.get("t", self._elapsed())), 6)
            
            # Capture window context
            if self.capture_context:
                current_window = get_active_window()
                if current_window != self._last_window:
                    # Record window change
                    self.events.append({
                        "type": "window_change",
                        "t": event["t"],
                        "window": current_window
                    })
                    self._last_window = current_window
                
                event["window"] = current_window
            
            self.events.append(event)

    # --------------------------------------------------------------- Listeners
    def _on_move(self, x: int, y: int) -> None:
        try:
            self._record({"type": "mouse_move", "x": x, "y": y})
        except Exception:
            # Don't let exceptions stop the listener
            pass

    def _on_click(
        self, x: int, y: int, button: mouse.Button, pressed: bool
    ) -> None:
        try:
            button_name = button.name if hasattr(button, 'name') else str(button)
            event = {
                "type": "mouse_click",
                "x": x,
                "y": y,
                "button": button_name,
                "pressed": pressed,
            }
            
            # Capture screen context when button is released (more accurate)
            if self.capture_context and not pressed:
                context = get_screen_context(x, y)
                event.update(context)
            
            self._record(event)
        except Exception:
            # Don't let exceptions stop the listener
            pass

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        try:
            self._record({"type": "mouse_scroll", "x": x, "y": y, "dx": dx, "dy": dy})
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
            event = {
                "type": "key_press",
                "key": self._normalize_key(key),
            }
            
            # Capture context for text input
            if self.capture_context:
                # Get mouse position to capture context near where typing happens
                try:
                    from pynput.mouse import Controller
                    mouse_controller = Controller()
                    mouse_pos = mouse_controller.position
                    context = get_screen_context(mouse_pos[0], mouse_pos[1])
                    event.update(context)
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

