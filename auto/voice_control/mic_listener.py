from __future__ import annotations

from typing import Optional

import speech_recognition as sr


class MicrophoneListener:
    """Light wrapper around SpeechRecognition's microphone loop."""

    def __init__(self) -> None:
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = 250
        self._recognizer.pause_threshold = 0.6

    def capture(self, timeout: Optional[float] = None) -> Optional[str]:
        with sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=6)
            except sr.WaitTimeoutError:
                print("[mic] timed out waiting for speech")
                return None

        try:
            return self._recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as err:
            print(f"[mic] STT request failed: {err}")
            return None


