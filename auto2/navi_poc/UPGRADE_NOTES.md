# NAVI Upgrade: Intelligent Action Understanding

## Overview

The system has been upgraded from simple event recording/replay to intelligent action understanding and semantic replication.

## Key Improvements

### 1. Screen Understanding (`screen_understanding.py`)
- **OCR Integration**: Captures text visible on screen near click/action points
- **Window Context**: Tracks active application and window titles
- **Element Detection**: Can find UI elements by semantic description, not just coordinates

### 2. Action Analysis (`action_analyzer.py`)
- **Semantic Intent Recognition**: Understands what actions mean (e.g., "clicking Save button" vs just "click at x,y")
- **Workflow Understanding**: Analyzes entire workflow to extract high-level steps
- **LLM Integration**: Uses Ollama for deeper understanding when available

### 3. Enhanced Recording (`recorder.py`)
- **Context Capture**: Records window information, OCR text, and screen context with each action
- **Semantic Metadata**: Stores what was clicked/typed, not just coordinates

### 4. Intelligent Replay (`replayer.py`)
- **Semantic Element Finding**: Finds UI elements by text/description instead of fixed coordinates
- **Adaptive Execution**: Can adapt to UI changes by finding elements semantically
- **Workflow Analysis**: Shows what the workflow does before execution

### 5. LLM Integration
- **Auto-description**: Generates workflow descriptions automatically
- **Intelligent Matching**: Uses semantic understanding to match user commands to workflows
- **Action Understanding**: Analyzes actions to understand user intent

## New Dependencies

```
pillow>=10.0          # Image processing
pytesseract>=0.3.10  # OCR (requires Tesseract installed separately)
pywin32>=306          # Windows API for window detection
psutil>=5.9           # Process information
ollama>=0.1.0         # LLM integration (optional but recommended)
```

## Installation Notes

1. **Tesseract OCR**: 
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH or set `TESSERACT_CMD` environment variable

2. **Ollama** (optional but recommended):
   - Install from https://ollama.ai
   - Pull a model: `ollama pull llama3.2`
   - System works without it but with reduced intelligence

## How It Works

### Recording
1. User performs actions
2. System captures:
   - Mouse/keyboard events (as before)
   - Window context (app, title)
   - OCR text near click points
   - Screen regions for visual reference
3. Actions are analyzed to extract semantic meaning
4. Workflow understanding is generated

### Replay
1. System analyzes workflow to understand intent
2. For each action:
   - If intelligent mode: Tries to find element by text/description
   - Falls back to coordinates if semantic search fails
   - Adapts to UI changes automatically
3. Shows progress and found elements

## Usage

The interface remains the same, but now:
- Workflows are automatically analyzed
- Descriptions can be auto-generated
- Replay adapts to UI changes
- Better matching of natural language commands

## Benefits

1. **Robustness**: Works even if UI elements move
2. **Understanding**: Knows what actions mean, not just what they are
3. **Adaptability**: Can find elements by meaning, not just position
4. **Intelligence**: Uses LLM to understand and describe workflows

## Limitations

- OCR requires good screen contrast and readable text
- Semantic finding may be slower than coordinate-based replay
- Some applications may not expose text via OCR
- LLM features require Ollama to be running

