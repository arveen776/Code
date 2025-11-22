# Testing Your Setup

## Quick Test

1. **Start the server**: `python server.py`
2. **Open on iPhone**: Go to `http://YOUR_IP:5000`
3. **Send a test command**:
   ```bash
   python client.py call +1234567890
   ```
4. **On iPhone**: Tap "Execute"

## What Should Happen

- For `call`: Should open Phone app with the number
- For `send_message`: Should open Messages app
- For `open_app`: May or may not work depending on the app
- For `shortcut`: Should work if shortcut exists

## If It Doesn't Work

### Error: "Safari cannot open the page because the address is invalid"

This means Safari is blocking the URL scheme. Solutions:

1. **Use iOS Shortcuts** (Best solution)
   - See `SHORTCUT_SETUP.md`
   - Create a shortcut that handles the command
   - Use `shortcuts://` URL scheme (more reliable)

2. **Test URL schemes directly**
   - Try opening `tel:1234567890` directly in Safari
   - If it works, the issue is with our redirect
   - If it doesn't, Safari is blocking it

3. **Use alternative methods**
   - Some commands work better through Shortcuts
   - Consider creating shortcuts for each action type

## Testing URL Schemes

You can test if a URL scheme works by typing it directly in Safari's address bar:

- `tel:1234567890` - Should open Phone app
- `sms:1234567890` - Should open Messages app  
- `shortcuts://run-shortcut?name=YourShortcut` - Should run shortcut
- `camera://` - May or may not work
- `prefs://` - Should open Settings

If a scheme works directly but not through our system, there's a bug in our code.
If it doesn't work directly, Safari is blocking it and you need to use Shortcuts.

