from __future__ import annotations

import argparse
import sys
import time
from typing import Optional

from dotenv import load_dotenv

from voice_control import BrowserActionExecutor, IntentEngine, MicrophoneListener


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Voice command loop for basic browser control.",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Use typed input instead of microphone (debug mode).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log intended actions without issuing real key presses.",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM-based intent fallback even if an API key is present.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    intent_engine = IntentEngine(enable_llm=not args.no_llm)
    executor = BrowserActionExecutor(dry_run=args.dry_run)
    listener: Optional[MicrophoneListener] = None if args.text else MicrophoneListener()

    print("Voice control ready. Say 'stop listening' or press Ctrl+C to exit.")
    time.sleep(0.2)

    while True:
        utterance = capture(listener)
        if utterance is None:
            continue

        print(f"[heard] {utterance}")
        intent = intent_engine.detect(utterance)
        if not intent:
            print("[intent] unsure, please rephrase.")
            continue

        print(f"[intent] {intent.name} ({intent.source}, {intent.confidence:.2f})")
        result = executor.execute(intent)

        if result is False or intent.name == "stop":
            print("Stopping listener.")
            break


def capture(listener: Optional[MicrophoneListener]) -> Optional[str]:
    if listener is None:
        try:
            return input("Command> ")
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

    try:
        print("Listening...")
        utterance = listener.capture(timeout=8.0)
    except KeyboardInterrupt:
        print()
        sys.exit(0)

    return utterance


if __name__ == "__main__":
    main()


