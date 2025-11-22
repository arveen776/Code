"""
Phone Command Client
Send commands from your Windows computer to your iPhone
"""

import requests
import json
import sys

# Default server URL (change this to your computer's IP address)
SERVER_URL = "http://localhost:5000"

def send_command(command_type, data):
    """Send a command to the server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/commands",
            json={
                'type': command_type,
                'data': data
            },
            timeout=5
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Command sent successfully!")
            print(f"   Type: {command_type}")
            print(f"   ID: {result['command']['id']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to server at {SERVER_URL}")
        print("   Make sure the server is running (python server.py)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def open_app(app_name, app_id=None):
    """Command to open an app on iPhone"""
    if not app_id:
        # Common iOS app URL schemes
        app_schemes = {
            'messages': 'sms',
            'phone': 'tel',
            'mail': 'mailto',
            'safari': 'http',
            'settings': 'prefs',
            'photos': 'photos-redirect',
            'camera': 'camera',
            'music': 'music',
            'maps': 'maps',
            'calendar': 'calshow',
            'notes': 'mobilenotes',
            'reminders': 'x-apple-reminder',
        }
        app_id = app_schemes.get(app_name.lower(), app_name.lower())
    
    return send_command('open_app', {
        'app_name': app_name,
        'app_id': app_id
    })

def send_message(recipient, message):
    """Command to send a message"""
    return send_command('send_message', {
        'recipient': recipient,
        'message': message
    })

def make_call(phone_number):
    """Command to make a phone call"""
    return send_command('call', {
        'phone_number': phone_number
    })

def run_shortcut(shortcut_name):
    """Command to run an iOS Shortcut"""
    return send_command('shortcut', {
        'shortcut_name': shortcut_name
    })

def list_commands():
    """List all pending commands"""
    try:
        response = requests.get(f"{SERVER_URL}/api/commands", timeout=5)
        if response.status_code == 200:
            data = response.json()
            commands = data['commands']
            
            if not commands:
                print("No pending commands")
                return
            
            print(f"\n📋 Pending Commands ({len(commands)}):")
            print("-" * 60)
            for cmd in commands:
                print(f"ID: {cmd['id']} | Type: {cmd['type']} | Time: {cmd['timestamp']}")
                print(f"   Data: {json.dumps(cmd['data'], indent=2)}")
                print()
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Interactive command line interface"""
    print("=" * 60)
    print("Phone Command Client")
    print("=" * 60)
    print(f"Server: {SERVER_URL}")
    print("\nAvailable commands:")
    print("  1. open_app <app_name>")
    print("  2. send_message <phone_number> <message>")
    print("  3. call <phone_number>")
    print("  4. shortcut <shortcut_name>")
    print("  5. list - Show pending commands")
    print("  6. quit - Exit")
    print("=" * 60)
    print()
    
    while True:
        try:
            user_input = input("Command > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'list':
                list_commands()
                continue
            
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == 'open_app':
                if len(parts) < 2:
                    print("Usage: open_app <app_name>")
                    continue
                app_name = ' '.join(parts[1:])
                open_app(app_name)
            
            elif command == 'send_message':
                if len(parts) < 3:
                    print("Usage: send_message <phone_number> <message>")
                    continue
                phone_number = parts[1]
                message = ' '.join(parts[2:])
                send_message(phone_number, message)
            
            elif command == 'call':
                if len(parts) < 2:
                    print("Usage: call <phone_number>")
                    continue
                phone_number = parts[1]
                make_call(phone_number)
            
            elif command == 'shortcut':
                if len(parts) < 2:
                    print("Usage: shortcut <shortcut_name>")
                    continue
                shortcut_name = ' '.join(parts[1:])
                run_shortcut(shortcut_name)
            
            else:
                print(f"Unknown command: {command}")
                print("Type a command or 'quit' to exit")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    # Check if running as script with arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'open_app' and len(sys.argv) > 2:
            open_app(' '.join(sys.argv[2:]))
        elif sys.argv[1] == 'send_message' and len(sys.argv) > 3:
            send_message(sys.argv[2], ' '.join(sys.argv[3:]))
        elif sys.argv[1] == 'call' and len(sys.argv) > 2:
            make_call(sys.argv[2])
        elif sys.argv[1] == 'shortcut' and len(sys.argv) > 2:
            run_shortcut(' '.join(sys.argv[2:]))
        elif sys.argv[1] == 'list':
            list_commands()
        else:
            print("Usage:")
            print("  python client.py open_app <app_name>")
            print("  python client.py send_message <phone> <message>")
            print("  python client.py call <phone_number>")
            print("  python client.py shortcut <shortcut_name>")
            print("  python client.py list")
    else:
        main()

