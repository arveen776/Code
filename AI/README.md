# Simple OpenAI Chat Interface

A simple web-based chat interface to test your OpenAI API key.

## How to Run

### Method 1: Using Python (Easiest - Recommended)

1. Open PowerShell or Command Prompt in this folder
2. Run one of these commands:

   **Python 3:**
   ```bash
   python -m http.server 8000
   ```

   **Python 2:**
   ```bash
   python -m SimpleHTTPServer 8000
   ```

3. Open your browser and go to: `http://localhost:8000/chat.html`
4. Enter your OpenAI API key and start chatting!

### Method 2: Using Node.js

1. Install http-server globally (if not already installed):
   ```bash
   npm install -g http-server
   ```

2. Run the server:
   ```bash
   http-server -p 8000
   ```

3. Open your browser and go to: `http://localhost:8000/chat.html`

### Method 3: Direct File Open (May have CORS issues)

1. Simply double-click `chat.html` to open it in your browser
2. **Note:** Some browsers may block API requests when opening files directly. If you see CORS errors, use Method 1 or 2 instead.

### Method 4: Using VS Code Live Server

1. Install the "Live Server" extension in VS Code
2. Right-click on `chat.html` and select "Open with Live Server"

## Usage

1. Open the chat interface in your browser
2. Enter your OpenAI API key in the input field at the top
3. Click "Save Key" (the key is stored locally in your browser)
4. Type your message and click "Send" or press Enter

## Note

Your API key is stored locally in your browser's localStorage and is never sent anywhere except to OpenAI's API.

