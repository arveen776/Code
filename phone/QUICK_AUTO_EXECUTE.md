# Quick Auto-Execute Guide

## ✅ Auto-Execute is Now Enabled!

When you send a command from your computer, it will **automatically execute** on your iPhone!

## How to Use

1. **Start the server**: `python server.py`
2. **Open on iPhone**: Go to `http://YOUR_IP:5000` in Safari
3. **Keep Safari open** (important for auto-execution)
4. **Send commands** from your computer - they'll execute automatically!

## Toggle Auto-Execute

- **Top-right corner** of the web page
- Toggle ON/OFF as needed
- Setting is saved (persists when you refresh)

## About iOS Confirmations

⚠️ **Important**: iOS will still show confirmation dialogs for:
- **Phone calls** - You'll need to tap "Call" 
- **Messages** - You'll need to tap "Send"

This is an **iOS security feature** and cannot be bypassed. However:

### Option 1: Use Siri Shortcuts
Create shortcuts that can be triggered with voice or automation to handle confirmations faster.

### Option 2: Keep Phone Unlocked
If your phone is unlocked and you're nearby, you can quickly tap the confirmation.

### Option 3: Use iOS Shortcuts Automation
Set up automation to run commands automatically (see `AUTO_EXECUTE_SETUP.md`)

## What Works Automatically

✅ **Opening apps** - Usually works without confirmation  
✅ **Running shortcuts** - Works automatically  
✅ **Opening URLs** - Works automatically  
⚠️ **Calls/Messages** - Requires one tap on iOS confirmation

## Tips

1. **Keep Safari open** - Auto-execute needs the page to be active
2. **Add to Home Screen** - Makes it easier to keep open
3. **Test first** - Try a simple command to verify it works
4. **Use Shortcuts** - For better automation of confirmations

## Example

```bash
# Send a command
python client.py call +1234567890

# On iPhone:
# 1. Command appears automatically
# 2. Executes automatically (opens Phone app)
# 3. You tap "Call" on iOS confirmation
# Done! ✅
```

Enjoy hands-free command execution! 🎉

