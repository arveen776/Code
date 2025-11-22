# Quick Start Guide

## Step 1: Install Dependencies

Open PowerShell or CMD in this folder and run:
```bash
pip install -r requirements.txt
```

## Step 2: Find Your IP Address

In PowerShell/CMD, run:
```bash
ipconfig
```

Find the IPv4 address under your Wi-Fi adapter (looks like `192.168.1.XXX`)

## Step 3: Start the Server

Double-click `start_server.bat` or run:
```bash
python server.py
```

You'll see a message showing the server is running.

## Step 4: Open on Your iPhone

1. Make sure your iPhone is on the **same Wi-Fi network**
2. Open Safari on your iPhone
3. Go to: `http://YOUR_IP:5000` (replace YOUR_IP with the address from Step 2)
4. Bookmark it!

## Step 5: Send Your First Command

Open a new terminal window and try:

```bash
# Open Messages app
python client.py open_app messages

# Or use the batch file
send_command.bat open_app messages
```

Then check your iPhone - you should see the command appear! Tap "Execute" to run it.

## Example Commands

```bash
# Open apps
send_command.bat open_app camera
send_command.bat open_app phone
send_command.bat open_app settings

# Send a message (will open Messages app with recipient)
send_command.bat send_message +1234567890 "Hello from my PC!"

# Make a call
send_command.bat call +1234567890

# Run an iOS Shortcut (must exist on your iPhone)
send_command.bat shortcut "My Shortcut Name"

# List pending commands
send_command.bat list
```

## Troubleshooting

**iPhone can't connect:**
- Check both devices are on same Wi-Fi
- Windows Firewall might be blocking - allow Python through firewall
- Try using your computer's IP address instead of localhost

**Commands not working:**
- Make sure you tap "Execute" on your iPhone
- Some apps need to be installed
- URL schemes might vary on iOS 17+

Enjoy controlling your iPhone from your computer! 🎉

