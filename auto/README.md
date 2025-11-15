# Voice-Driven Browser Controller (MVP)

This project explores how to drive a desktop browser using natural, voice-first commands. The current iteration focuses on building the core loop:

1. Capture speech from the system microphone.
2. Convert it to text with a speech-to-text (STT) engine (Google Web Speech via `SpeechRecognition` by default, OpenAI Whisper optional).
3. Interpret the text into high-level intents with lightweight rules, with an optional LLM fallback for ambiguous phrases.
4. Execute browser actions (scroll, tabs, navigation) via synthetic keyboard/mouse events using `pyautogui`.

> ⚠️ **Safety:** The script sends real keyboard shortcuts to whatever window is focused. Keep the browser in the foreground while testing, and stop the script (`Ctrl+C`) if it begins issuing unintended actions.

## Getting Started

1. **Install Python 3.10+** and `pip`.
2. **Install system audio deps** (Windows users will usually need the [PyAudio wheel](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)).
3. **Install Python deps:**
   ```powershell
   pip install -r requirements.txt
   ```
4. **(Optional)** Create a `.env` file with `OPENAI_API_KEY=...` if you want LLM intent disambiguation.

## Usage

```powershell
python main.py
```

Speak commands such as:

- “Scroll down a bit”
- “Open a new tab and go to Wikipedia”
- “Back”

The console will log what it heard, the inferred intent, and the action taken. Say “stop listening” or press `Ctrl+C` to exit.

## Roadmap

- ✅ MVP microphone loop + basic intent mapping.
- ⏳ LLM-enhanced intent understanding and slot filling.
- ⏳ Browser-specific integrations (Chrome DevTools Protocol for robust tab/page control).
- ⏳ Feedback UI + confirmation prompts.
- ⏳ Custom phrase training and multilingual support.

Feel free to suggest additional intents or integrations!


