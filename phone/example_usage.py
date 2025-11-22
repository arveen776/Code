"""
Example usage of the Phone Command System
This shows how to send commands programmatically
"""

from client import open_app, send_message, make_call, run_shortcut

# Example 1: Open an app
print("Example 1: Opening Messages app...")
open_app("messages")

# Example 2: Send a message
print("\nExample 2: Sending a message...")
send_message("+1234567890", "Hello from my computer!")

# Example 3: Make a call
print("\nExample 3: Making a call...")
make_call("+1234567890")

# Example 4: Run an iOS Shortcut
print("\nExample 4: Running a shortcut...")
run_shortcut("My Shortcut Name")

# Example 5: Open Camera
print("\nExample 5: Opening Camera...")
open_app("camera")

print("\n✅ All commands sent! Check your iPhone to execute them.")

