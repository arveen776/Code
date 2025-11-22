# iOS Shortcut Setup Guide

Since URL schemes don't work reliably from Safari, we'll use **iOS Shortcuts** as the primary execution method. This is more reliable and gives you more control.

## Option 1: Universal Command Shortcut (Recommended)

Create one shortcut that handles all command types:

### Steps:

1. **Open Shortcuts app** on your iPhone
2. **Create a new shortcut** called "Execute Phone Command"
3. **Add these actions**:

```
1. Get Contents of URL
   - URL: http://YOUR_COMPUTER_IP:5000/api/execute/next
   - Method: GET

2. Get Dictionary from Input
   - (This parses the JSON response)

3. If (Dictionary Value for "command_type" equals "open_app")
   - Open App
     - App: (Use Dictionary Value for "app_name")

4. Otherwise, If (Dictionary Value for "command_type" equals "call")
   - Call
     - Phone Number: (Use Dictionary Value for "phone_number")

5. Otherwise, If (Dictionary Value for "command_type" equals "send_message")
   - Send Message
     - Recipients: (Use Dictionary Value for "recipient")
     - Message: (Use Dictionary Value for "message")

6. Otherwise, If (Dictionary Value for "command_type" equals "shortcut")
   - Run Shortcut
     - Shortcut: (Use Dictionary Value for "shortcut_name")
```

4. **Save the shortcut**

## Option 2: Simple Webhook Shortcut (Easier)

Create a simpler shortcut that just opens a URL:

1. **Create shortcut** called "Phone Command"
2. **Add action**: "Open URLs"
   - URL: `http://YOUR_IP:5000/execute`
3. **Save**

Then we'll update the server to handle execution via this shortcut.

## Option 3: Individual Shortcuts

Create separate shortcuts for each action type:
- "Open App Command"
- "Call Command"  
- "Message Command"

Then use the shortcut name in your commands.

---

**After creating the shortcut, update the server to use it!**

