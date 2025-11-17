import requests
import re
import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import os
import json
import pyautogui
import time

# Disable pyautogui failsafe for smoother operation
pyautogui.FAILSAFE = False

# Ollama chat endpoint
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-r1:14b"

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
microphone = sr.Microphone()
tts_engine = pyttsx3.init()

# Configure TTS settings
tts_engine.setProperty('rate', 150)  # Speed of speech
tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# Try to set a better voice if available
voices = tts_engine.getProperty('voices')
if voices:
    # Prefer a more natural-sounding voice if available
    for voice in voices:
        if 'english' in voice.name.lower():
            tts_engine.setProperty('voice', voice.id)
            break

def ask_jarvis(messages, check_command=False):
    """Ask Jarvis a question. If check_command=True, ask if user wants to execute a command."""
    if check_command:
        # Add a special prompt to detect if user wants to execute a command
        command_check_messages = messages + [{
            "role": "user",
            "content": "IMPORTANT: Does the user want me to execute a command or action on their computer? Examples: opening apps, websites, window management, or system commands. Respond with ONLY a JSON object: {\"is_command\": true/false, \"command_type\": \"open_website|open_app|window_manage|system|none\", \"details\": \"specific details about what to do\"}. If not a command, set is_command to false."
        }]
        
        payload = {
            "model": MODEL_NAME,
            "messages": command_check_messages,
            "stream": False
        }
        
        resp = requests.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        content = data["message"]["content"]
        content_clean = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        
        # Try to parse JSON response
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content_clean, re.DOTALL)
            if json_match:
                command_info = json.loads(json_match.group())
                return command_info
        except:
            pass
        
        return {"is_command": False, "command_type": "none", "details": ""}
    else:
        # Normal conversation mode
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False
        }

        resp = requests.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()

        # DeepSeek replies in data["message"]["content"]
        content = data["message"]["content"]

        # Remove <think>...</think> block so you only see the final answer
        content_clean = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)

        return content_clean.strip()

def listen_for_voice():
    """Listen to microphone and return transcribed text."""
    try:
        with microphone as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("\n[ Listening... Speak now ]")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
        
        print("[ Processing your speech... ]")
        # Use Google's speech recognition (requires internet)
        # For offline, you can use 'sphinx' instead
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.WaitTimeoutError:
        print("[ No speech detected. Try again. ]")
        return None
    except sr.UnknownValueError:
        print("[ Could not understand audio. Please try again. ]")
        return None
    except sr.RequestError as e:
        print(f"[ Error with speech recognition service: {e} ]")
        print("[ Falling back to text input... ]")
        return None
    except Exception as e:
        print(f"[ Error listening: {e} ]")
        return None

def speak(text):
    """Convert text to speech and speak it aloud."""
    try:
        # Print the text being spoken
        print(f"\nJarvis: {text}\n")
        # Speak the text
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"[ Error with text-to-speech: {e} ]")
        # If TTS fails, just print the text
        print(f"\nJarvis: {text}\n")

def execute_command(user_input, command_info):
    """Execute a command based on user input and command information."""
    command_type = command_info.get("command_type", "none")
    details = command_info.get("details", "").lower()
    user_lower = user_input.lower()
    
    try:
        # Open Website
        website_keywords = ["youtube", "google", "facebook", "twitter", "instagram", "github", "reddit", "gmail", "outlook", "netflix", "amazon", "spotify", "website", "web"]
        is_website_command = (command_type == "open_website" or 
                            ("open" in user_lower and any(keyword in user_lower for keyword in website_keywords)) or
                            ("http" in user_lower or ".com" in user_lower or ".org" in user_lower))
        
        if is_website_command:
            # Extract website name
            website_patterns = {
                "youtube": "https://youtube.com",
                "google": "https://google.com",
                "facebook": "https://facebook.com",
                "twitter": "https://twitter.com",
                "x.com": "https://x.com",
                "instagram": "https://instagram.com",
                "github": "https://github.com",
                "reddit": "https://reddit.com",
                "gmail": "https://gmail.com",
                "outlook": "https://outlook.com",
                "netflix": "https://netflix.com",
                "amazon": "https://amazon.com",
                "spotify": "https://open.spotify.com",
            }
            
            url = None
            for site, url_val in website_patterns.items():
                if site in user_lower:
                    url = url_val
                    break
            
            if url:
                webbrowser.open(url)
                return f"Opening {url} in your browser."
            elif "http" in user_lower or ".com" in user_lower or ".org" in user_lower:
                # Try to extract URL from input
                url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', user_input)
                if url_match:
                    url = url_match.group(1)
                    if not url.startswith("http"):
                        url = "https://" + url
                    webbrowser.open(url)
                    return f"Opening {url} in your browser."
            
        # Open Application
        app_keywords = ["notepad", "calculator", "cmd", "powershell", "chrome", "firefox", "edge", "code", "discord", "steam", "app", "application", "paint", "explorer"]
        is_app_command = (command_type == "open_app" or 
                         ("open" in user_lower and ("app" in user_lower or "application" in user_lower or any(app in user_lower for app in app_keywords))))
        
        if is_app_command:
            app_patterns = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe",
                "command prompt": "cmd.exe",
                "powershell": "powershell.exe",
                "chrome": "chrome.exe",
                "google chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "microsoft edge": "msedge.exe",
                "code": "code.exe",
                "vs code": "code.exe",
                "visual studio code": "code.exe",
                "discord": "Discord.exe",
                "spotify": "Spotify.exe",
                "steam": "steam.exe",
                "file explorer": "explorer.exe",
                "explorer": "explorer.exe",
            }
            
            app_name = None
            app_path = None
            
            for app_key, app_exe in app_patterns.items():
                if app_key in user_lower:
                    app_name = app_key
                    app_path = app_exe
                    break
            
            if app_path:
                try:
                    # Try to launch the app
                    subprocess.Popen(app_path, shell=True)
                    return f"Opening {app_name}."
                except Exception as e:
                    # Try alternative methods
                    try:
                        # Try os.startfile for Windows
                        os.startfile(app_path)
                        return f"Opening {app_name}."
                    except:
                        # Try launching via start command (Windows)
                        try:
                            subprocess.run(["start", "", app_path], shell=True, check=False)
                            return f"Opening {app_name}."
                        except Exception as e2:
                            return f"Could not open {app_name}. It may not be installed or not in the system PATH."
        
        # Window Management
        window_keywords = ["split", "screen", "snap", "maximize", "minimize", "window"]
        is_window_command = (command_type == "window_manage" or 
                            any(keyword in user_lower for keyword in window_keywords))
        
        if is_window_command:
            # Windows 10/11 Snap feature simulation
            if "split" in user_lower or "snap" in user_lower:
                # Get current window
                try:
                    # Simulate Windows key + Left/Right arrow for snap
                    if "left" in user_lower:
                        pyautogui.hotkey('win', 'left')
                        time.sleep(0.3)
                        return "Split screen to the left."
                    elif "right" in user_lower:
                        pyautogui.hotkey('win', 'right')
                        time.sleep(0.3)
                        return "Split screen to the right."
                    else:
                        # Default to right
                        pyautogui.hotkey('win', 'right')
                        time.sleep(0.3)
                        return "Splitting current window."
                except Exception as e:
                    return f"Split screen command executed. Error: {str(e)}"
            
            elif "maximize" in user_lower:
                pyautogui.hotkey('win', 'up')
                return "Maximizing current window."
            
            elif "minimize" in user_lower:
                pyautogui.hotkey('win', 'down')
                return "Minimizing current window."
        
        # System Commands
        elif command_type == "system":
            if "shutdown" in user_lower or "turn off" in user_lower:
                speak("Shutting down the computer in 30 seconds. Say cancel to abort.")
                subprocess.run(["shutdown", "/s", "/t", "30"])
                return "Computer will shut down in 30 seconds. Say 'cancel shutdown' to abort."
            
            elif "restart" in user_lower or "reboot" in user_lower:
                speak("Restarting the computer in 30 seconds. Say cancel to abort.")
                subprocess.run(["shutdown", "/r", "/t", "30"])
                return "Computer will restart in 30 seconds. Say 'cancel shutdown' to abort."
            
            elif "cancel shutdown" in user_lower or "abort shutdown" in user_lower:
                subprocess.run(["shutdown", "/a"])
                return "Shutdown cancelled."
        
        # Default - command recognized but not implemented
        return f"Command recognized but could not execute: {details}. Please try a different phrase."
        
    except Exception as e:
        return f"Error executing command: {str(e)}"

def detect_command(user_input):
    """Detect if user wants to execute a command using pattern matching."""
    user_lower = user_input.lower()
    
    # Quick pattern-based detection
    command_patterns = [
        ("open", ["open", "launch", "start"]),
        ("website", ["youtube", "google", "facebook", "twitter", "instagram", "github", "reddit", "website", "web"]),
        ("app", ["notepad", "calculator", "chrome", "firefox", "edge", "code", "vs code", "discord", "spotify", "steam", "app", "application"]),
        ("window", ["split", "screen", "snap", "maximize", "minimize", "window"]),
        ("system", ["shutdown", "restart", "reboot", "turn off"]),
    ]
    
    # Check for command keywords
    has_command_keyword = any(keyword in user_lower for keyword in ["open", "launch", "start", "split", "maximize", "minimize", "shutdown", "restart"])
    
    return has_command_keyword

def main():
    print("=" * 60)
    print("Jarvis Voice Assistant (local DeepSeek-R1)")
    print("=" * 60)
    print("\nCommands:")
    print("  - Speak naturally to have a conversation")
    print("  - Execute commands by saying: 'open YouTube', 'open Notepad', 'split screen', etc.")
    print("  - Say 'exit' or 'quit' to end the session")
    print("  - Press Enter to use text input if voice fails")
    print("  - Press Ctrl+C to exit\n")
    print("\nAvailable Commands:")
    print("  • Open websites: 'open YouTube', 'open Google', 'open GitHub'")
    print("  • Open apps: 'open Notepad', 'open Calculator', 'open Chrome', 'open VS Code'")
    print("  • Window management: 'split screen', 'split left', 'maximize window', 'minimize window'")
    print("  • System: 'shutdown computer', 'restart computer'\n")
    
    # Calibrate microphone on startup
    print("Calibrating microphone for ambient noise...")
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready! You can start speaking now.\n")
    except Exception as e:
        print(f"Warning: Could not calibrate microphone: {e}")
        print("Voice input may not work properly.\n")

    # System message = personality + behavior
    messages = [
        {
            "role": "system",
            "content": (
                "You are Jarvis, a highly capable AI assistant running locally on the user's computer. "
                "You are calm, polite, slightly witty, and extremely helpful. "
                "Since this is a voice conversation, keep your responses concise and natural. "
                "You can execute commands on the user's computer like opening apps, websites, managing windows, "
                "or system commands. When a user asks you to do something, execute it and confirm. "
                "Explain your reasoning when useful, but avoid very long monologues. "
                "Help with coding, math, planning, and general questions."
            )
        }
    ]

    while True:
        try:
            # Try voice input first
            user_input = listen_for_voice()
            
            # If voice input failed, fall back to text input
            if user_input is None:
                user_input = input("\nType your message (or press Enter to try voice again): ").strip()
                if not user_input:
                    continue
                    
        except (EOFError, KeyboardInterrupt):
            speak("Jarvis shutting down. Goodbye.")
            break

        if user_input.lower().strip() in {"exit", "quit", "goodbye"}:
            speak("Understood. Powering down. Goodbye.")
            break

        # Check if user wants to execute a command
        if detect_command(user_input):
            print("[ Command detected. Executing... ]")
            messages.append({"role": "user", "content": user_input})
            
            # Get command info from AI (optional, we'll also use pattern matching)
            try:
                command_info = ask_jarvis(messages, check_command=True)
                if isinstance(command_info, dict) and command_info.get("is_command"):
                    result = execute_command(user_input, command_info)
                    speak(result)
                    messages.append({"role": "assistant", "content": result})
                    continue
            except Exception as e:
                print(f"[ Error checking command with AI: {e} ]")
            
            # Fall back to pattern-based execution
            command_info = {"command_type": "auto", "details": user_input}
            result = execute_command(user_input, command_info)
            
            # Only speak if command was actually executed (not an error message)
            if "error" not in result.lower() and "could not" not in result.lower():
                speak(result)
                messages.append({"role": "assistant", "content": result})
                continue
            else:
                # If command execution failed, continue to normal conversation
                print(f"[ {result} - Continuing to normal conversation... ]")
                # Message already in messages, continue to normal AI conversation below
        else:
            # Normal conversation - add to messages for AI
            messages.append({"role": "user", "content": user_input})

        # Normal AI conversation
        try:
            reply = ask_jarvis(messages)
        except Exception as e:
            error_msg = f"Error talking to Jarvis: {e}"
            print(f"[{error_msg}]")
            speak("Sorry, I encountered an error. Please try again.")
            continue

        # Speak the reply
        speak(reply)

        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
