from __future__ import annotations

import time
from typing import Callable, Dict, Optional

import pyautogui

from .intent_engine import IntentResult


class BrowserActionExecutor:
    """Maps intents to concrete browser automation calls."""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        pyautogui.FAILSAFE = True
        self._handlers: Dict[str, Callable[[IntentResult], Optional[bool]]] = {
            "scroll_down": lambda _: self._scroll(-500),
            "scroll_up": lambda _: self._scroll(500),
            "go_back": lambda _: self._hotkey("alt", "left"),
            "go_forward": lambda _: self._hotkey("alt", "right"),
            "refresh": lambda _: self._press("f5"),
            "new_tab": lambda intent: self._new_tab(intent.slots.get("url")),
            "new_tab_site": lambda intent: self._new_tab(intent.slots.get("url")),
            "close_tab": lambda _: self._hotkey("ctrl", "w"),
            "goto_url": lambda intent: self._goto(intent.slots.get("url")),
            "stop": lambda _: False,
        }

    def execute(self, intent: IntentResult) -> Optional[bool]:
        handler = self._handlers.get(intent.name)
        if not handler:
            return None
        return handler(intent)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scroll(self, delta: int) -> bool:
        if self.dry_run:
            print(f"[dry-run] scroll {delta}")
            return True
        pyautogui.scroll(delta)
        return True

    def _hotkey(self, *keys: str) -> bool:
        if self.dry_run:
            print(f"[dry-run] hotkey {keys}")
            return True
        pyautogui.hotkey(*keys)
        return True

    def _press(self, key: str) -> bool:
        if self.dry_run:
            print(f"[dry-run] press {key}")
            return True
        pyautogui.press(key)
        return True

    def _new_tab(self, url: Optional[str]) -> bool:
        self._hotkey("ctrl", "t")
        time.sleep(0.2)
        if url:
            self._type_and_submit(url)
        return True

    def _goto(self, url: Optional[str]) -> bool:
        if not url:
            return False
        self._hotkey("ctrl", "l")
        self._type_and_submit(url)
        return True

    def _type_and_submit(self, url: str) -> None:
        normalized = self._normalize_url(url)
        if self.dry_run:
            print(f"[dry-run] type '{normalized}' + enter")
            return
        pyautogui.typewrite(normalized)
        pyautogui.press("enter")

    @staticmethod
    def _normalize_url(url: str) -> str:
        clean = url.strip().lower()
        replacements = {
            " dot com": ".com",
            " dot org": ".org",
            " dot net": ".net",
            " dot io": ".io",
        }
        for pattern, repl in replacements.items():
            clean = clean.replace(pattern, repl)
        clean = clean.replace(" dot ", ".").replace(" ", "")

        if clean.startswith(("http://", "https://")):
            return clean

        if not clean:
            return clean

        if "." not in clean:
            clean = f"{clean}.com"

        return f"https://{clean}"


