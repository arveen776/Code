# iOS Shortcut Setup - Step by Step

Since Safari blocks many URL schemes, we need to use iOS Shortcuts. Here's the easiest way:

## Quick Setup (5 minutes)

### Step 1: Create the Shortcut

1. Open **Shortcuts** app on your iPhone
2. Tap the **"+"** button to create a new shortcut
3. Name it: **"Execute Phone Command"** (exact name is important!)

### Step 2: Add Actions

Tap "Add Action" and add these actions in order:

#### Action 1: Get Contents of URL
- Search for "Get Contents of URL"
- URL: `http://YOUR_COMPUTER_IP:5000/api/next-command`
  - Replace `YOUR_COMPUTER_IP` with your computer's IP (from `ipconfig`)
- Method: GET

#### Action 2: Get Dictionary from Input
- Search for "Get Dictionary from Input"
- This parses the JSON response

#### Action 3: If Statement
- Search for "If"
- Condition: Dictionary Value for key "command_type" equals "open_app"
- Then:
  - Add "Open App" action
  - For "App", tap and select "Dictionary Value" → "app_name"

#### Action 4: More If Statements
Add similar If statements for:
- `command_type` = "call" → Use "Call" action with `phone_number`
- `command_type` = "send_message" → Use "Send Message" action with `recipient` and `message`
- `command_type` = "shortcut" → Use "Run Shortcut" action with `shortcut_name`

### Step 3: Add API Endpoint

We need to add an endpoint that returns the next command. Let me update the server...

---

## Alternative: Simpler Approach

If the above is too complex, we can use a simpler method where the shortcut just opens URLs directly. Let me know which you prefer!

