# Auto-Execute Setup Guide

The system now supports **automatic execution** of commands! When you send a command from your computer, it will automatically execute on your iPhone.

## How It Works

1. **Auto-Execute Toggle**: There's a toggle in the top-right corner of the web interface
2. **Automatic Detection**: The page checks for new commands every second
3. **Auto-Execution**: When a new command appears and auto-execute is ON, it runs automatically

## iOS Confirmation Dialogs

**Important**: iOS will still show confirmation dialogs for:
- Phone calls
- Sending messages
- Some app actions

These are **iOS security features** and cannot be bypassed. However, you can minimize them using iOS Shortcuts automation.

## Option 1: Use iOS Shortcuts Automation (Recommended)

This allows you to automate the confirmation dialogs:

### Step 1: Create the Shortcut

1. Open **Shortcuts** app
2. Create a shortcut called **"Execute Phone Command"**
3. Add these actions:

```
1. Get Contents of URL
   - URL: http://YOUR_IP:5000/api/next-command
   - Method: GET

2. Get Dictionary from Input

3. If (command_type = "call")
   - Call (phone_number)
   - [iOS will still ask for confirmation, but shortcut can handle it]

4. If (command_type = "send_message")
   - Send Message (recipient, message)
   - [iOS will still ask for confirmation]

5. If (command_type = "open_app")
   - Open App (app_name)
```

### Step 2: Set Up Automation

1. Go to **Shortcuts** → **Automation** tab
2. Tap **"+"** → **Create Personal Automation**
3. Choose **"App"** → Select **Safari**
4. Choose **"When App Opens"**
5. Add action: **Run Shortcut** → Select "Execute Phone Command"
6. Turn off **"Ask Before Running"** (if you want full automation)
7. Save

Now when Safari opens (or stays open), it will automatically check for commands!

### Step 3: Keep Safari Open

For best results:
- Keep the command page open in Safari
- Add to Home Screen for easier access
- Enable "Keep Screen On" in iPhone settings

## Option 2: Background Automation

You can also set up a time-based automation:

1. **Automation** → **Time of Day**
2. Set to run **every minute** (or as often as you want)
3. Action: **Run Shortcut** → "Execute Phone Command"
4. Turn off "Ask Before Running"

## Option 3: Push Notifications (Advanced)

For even better automation, you could:
1. Set up push notifications when commands arrive
2. Use notification actions to execute commands
3. This requires additional setup (can be added if needed)

## Tips for Full Automation

1. **Keep Safari Open**: The page needs to be active to auto-execute
2. **Add to Home Screen**: Makes it easier to keep open
3. **Disable Screen Lock**: Or set a long timeout
4. **Use Shortcuts Automation**: This handles iOS confirmations better
5. **Test First**: Try with simple commands before automating everything

## Limitations

- iOS **will always** ask for confirmation on calls/messages (security feature)
- Safari may pause JavaScript when the page is in background
- Some actions require the app to be in foreground
- Auto-execute works best when Safari is active

## Troubleshooting

**Commands not auto-executing:**
- Check that auto-execute toggle is ON (top-right corner)
- Make sure Safari page is active/visible
- Check browser console for errors
- Try refreshing the page

**iOS confirmations still appearing:**
- This is normal and cannot be bypassed
- Use Shortcuts automation to streamline the process
- Consider using Siri Shortcuts for voice confirmation

## Next Steps

1. Test auto-execute with a simple command
2. Set up iOS Shortcuts automation
3. Keep Safari open with the command page
4. Enjoy hands-free command execution!

