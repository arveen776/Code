# NAVI v0 Proof of Concept

Tiny but functional macro recorder + natural-language runner.

## Setup

```powershell
cd "C:\Users\singh\code ideas\auto2\navi_poc"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```powershell
python main.py           # interactive menu
python main.py --mode record
python main.py --mode list
python main.py --mode replay
python main.py --mode command
```

Recording flow:

1. Choose `record`.
2. Press Enter to start; perform the workflow.
3. Press Enter again to stop.
4. Provide a name + natural-language description.

Running by command uses a simple keyword overlap between your command and the workflow description to pick the best match, then replays it with `pyautogui`.

