# Phone Command System

A simple system to send commands from your Windows 11 computer to your iPhone 15 Pro.

## Features

- 🚀 Send commands from your computer to your iPhone
- 📱 Beautiful web interface on your iPhone
- 🔄 Real-time command updates
- 📞 Make calls, send messages, open apps
- ⚡ Run iOS Shortcuts

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Find Your Computer's IP Address

On Windows, open PowerShell or CMD and run:
```bash
ipconfig
```

Look for your Wi-Fi adapter's IPv4 address (e.g., `192.168.1.100`)

### 3. Start the Server

```bash
python server.py
```

The server will start on `http://0.0.0.0:5000`

### 4. Access from Your iPhone

1. Make sure your iPhone is on the **same Wi-Fi network** as your computer
2. Open Safari on your iPhone
3. Navigate to: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.1.100:5000`
4. Bookmark the page for easy access!

### 5. Send Commands from Your Computer

Open a new terminal and run:

```bash
# Interactive mode
python client.py

# Or use direct commands
python client.py open_app messages
python client.py send_message +1234567890 "Hello from my computer!"
python client.py call +1234567890
python client.py shortcut "My Shortcut Name"
python client.py list
```

## Available Commands

### Open App
```bash
python client.py open_app messages
python client.py open_app phone
python client.py open_app camera
python client.py open_app settings
```

### Send Message
```bash
python client.py send_message +1234567890 "Your message here"
```

### Make a Call
```bash
python client.py call +1234567890
```

### Run iOS Shortcut
```bash
python client.py shortcut "Shortcut Name"
```

## How It Works

1. **Server** (`server.py`): Runs on your Windows computer, receives commands and serves a web interface
2. **Client** (`client.py`): Sends commands from your computer to the server
3. **iPhone Interface**: A web page on your iPhone that displays pending commands
4. **Execution**: When you tap "Execute" on your iPhone, it opens the appropriate URL scheme or Shortcut

## iOS URL Schemes

The system uses iOS URL schemes to interact with your phone:
- `tel:` - Make phone calls
- `sms:` - Send messages
- `shortcuts://` - Run iOS Shortcuts
- App-specific schemes for opening apps

## Limitations & Known Issues

- Both devices must be on the same Wi-Fi network
- Some actions require manual confirmation on iPhone
- **iOS Safari blocks many URL schemes** - This is a known limitation
- Some URL schemes may not work in Safari (iOS security restriction)
- **Solution**: Use iOS Shortcuts for more reliable execution (see SHORTCUT_SETUP.md)

## Important: URL Scheme Limitations

iOS Safari has security restrictions that prevent many URL schemes from working directly. The current implementation uses a redirect page approach, but for maximum reliability, consider:

1. **Using iOS Shortcuts** (recommended) - See `SHORTCUT_SETUP.md`
2. **Testing which URL schemes work** on your device
3. **Using the Shortcuts app** to create custom actions

Common URL schemes that typically work:
- `tel:` - Phone calls
- `sms:` - Messages (may require confirmation)
- `shortcuts://` - Running shortcuts (most reliable)

## Troubleshooting

**Can't connect from iPhone:**
- Check that both devices are on the same Wi-Fi network
- Verify your computer's firewall allows connections on port 5000
- Make sure the server is running

**Commands not executing:**
- Some URL schemes may require apps to be installed
- iOS Shortcuts must exist with the exact name specified
- Check that you're tapping "Execute" on the iPhone interface

## Next Steps

Future enhancements could include:
- Authentication for security
- More command types
- Command scheduling
- Notification support
- Voice command integration

## Security Note

This is a simple local network tool. For production use, add authentication and encryption!

