"""
Phone Command Server
A Flask server that receives commands from your computer and executes them on your iPhone
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Store pending commands
pending_commands = []
command_history = []

# HTML template for the iPhone interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phone Command Receiver</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .status {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .command-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .command-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .command-type {
            font-weight: bold;
            color: #667eea;
            font-size: 18px;
        }
        .command-time {
            color: #999;
            font-size: 12px;
        }
        .command-data {
            color: #333;
            margin-top: 8px;
            word-break: break-word;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-execute {
            background: #667eea;
            color: white;
        }
        .btn-execute:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        .btn-dismiss {
            background: #e9ecef;
            color: #666;
        }
        .btn-dismiss:hover {
            background: #dee2e6;
        }
        .no-commands {
            text-align: center;
            color: #999;
            padding: 40px 20px;
        }
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #667eea;
            color: white;
            border: none;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            transform: rotate(180deg) scale(1.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Phone Commands</h1>
        <div class="status" id="status">Waiting for commands...</div>
        <div id="commands-container">
            <div class="no-commands">No pending commands</div>
        </div>
    </div>
    <button class="refresh-btn" onclick="loadCommands()">↻</button>

    <script>
        let commandIds = new Set();

        function loadCommands() {
            fetch('/api/commands')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('commands-container');
                    const status = document.getElementById('status');
                    
                    if (data.commands.length === 0) {
                        container.innerHTML = '<div class="no-commands">No pending commands</div>';
                        status.textContent = 'Waiting for commands...';
                        return;
                    }

                    status.textContent = `${data.commands.length} pending command(s)`;
                    container.innerHTML = '';

                    data.commands.forEach(cmd => {
                        if (!commandIds.has(cmd.id)) {
                            commandIds.add(cmd.id);
                            const card = createCommandCard(cmd);
                            container.appendChild(card);
                        }
                    });
                })
                .catch(error => {
                    console.error('Error loading commands:', error);
                    document.getElementById('status').textContent = 'Error loading commands';
                });
        }

        function createCommandCard(cmd) {
            const card = document.createElement('div');
            card.className = 'command-card';
            card.id = `cmd-${cmd.id}`;
            
            const time = new Date(cmd.timestamp).toLocaleTimeString();
            
            card.innerHTML = `
                <div class="command-header">
                    <span class="command-type">${cmd.type}</span>
                    <span class="command-time">${time}</span>
                </div>
                <div class="command-data">${formatCommandData(cmd)}</div>
                <div class="button-group">
                    <button class="btn-execute" onclick="executeCommand(${cmd.id})">Execute</button>
                    <button class="btn-dismiss" onclick="dismissCommand(${cmd.id})">Dismiss</button>
                </div>
            `;
            
            return card;
        }

        function formatCommandData(cmd) {
            if (cmd.type === 'open_app') {
                return `Open app: <strong>${cmd.data.app_name || cmd.data.app_id}</strong>`;
            } else if (cmd.type === 'send_message') {
                return `Send message to <strong>${cmd.data.recipient}</strong>: "${cmd.data.message}"`;
            } else if (cmd.type === 'call') {
                return `Call: <strong>${cmd.data.phone_number}</strong>`;
            } else if (cmd.type === 'shortcut') {
                return `Run shortcut: <strong>${cmd.data.shortcut_name}</strong>`;
            } else {
                return JSON.stringify(cmd.data, null, 2);
            }
        }

        function getActionUrl(cmd) {
            // Use a redirect page approach - more reliable than direct URL schemes
            // The server will handle the redirect to the proper URL scheme
            return `/execute/${cmd.id}`;
        }

        function executeCommand(cmdId) {
            // Find the command
            const cmd = Array.from(document.querySelectorAll('.command-card')).find(card => {
                return card.id === `cmd-${cmdId}`;
            });
            
            if (!cmd) {
                alert('Command not found');
                return;
            }
            
            // Get command data from the stored commands
            fetch(`/api/commands`)
                .then(response => response.json())
                .then(data => {
                    const command = data.commands.find(c => c.id === cmdId);
                    if (!command) {
                        alert('Command not found');
                        return;
                    }
                    
                    // Try primary method (Shortcuts)
                    let actionUrl = getActionUrl(command);
                    
                    // If shortcuts URL fails, try fallback
                    if (!actionUrl) {
                        actionUrl = getFallbackUrl(command);
                    }
                    
                    if (actionUrl) {
                        // Method 1: Try opening in new window (for shortcuts://)
                        try {
                            window.location.href = actionUrl;
                        } catch (e) {
                            // Method 2: Try using window.open
                            try {
                                window.open(actionUrl, '_self');
                            } catch (e2) {
                                // Method 3: Create a link and click it
                                const link = document.createElement('a');
                                link.href = actionUrl;
                                link.style.display = 'none';
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }
                        }
                        
                        // Mark as executed on server
                        fetch(`/api/commands/${cmdId}/execute`, { method: 'POST' })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    // Remove from UI after a short delay
                                    setTimeout(() => {
                                        dismissCommand(cmdId);
                                    }, 1000);
                                }
                            })
                            .catch(error => {
                                console.error('Error marking command as executed:', error);
                            });
                    } else {
                        alert('Could not generate action URL for this command. Please set up the iOS Shortcut first (see SHORTCUT_SETUP.md)');
                    }
                })
                .catch(error => {
                    console.error('Error executing command:', error);
                    alert('Error executing command');
                });
        }

        function dismissCommand(cmdId) {
            fetch(`/api/commands/${cmdId}`, { method: 'DELETE' })
                .then(() => {
                    const card = document.getElementById(`cmd-${cmdId}`);
                    if (card) {
                        card.remove();
                        commandIds.delete(cmdId);
                    }
                    loadCommands();
                })
                .catch(error => {
                    console.error('Error dismissing command:', error);
                });
        }

        // Auto-refresh every 2 seconds
        setInterval(loadCommands, 2000);
        
        // Load commands on page load
        loadCommands();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the iPhone interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """Get all pending commands"""
    return jsonify({
        'commands': pending_commands,
        'count': len(pending_commands)
    })

@app.route('/api/commands', methods=['POST'])
def create_command():
    """Create a new command from the computer"""
    data = request.json
    
    if not data or 'type' not in data:
        return jsonify({'error': 'Invalid command format'}), 400
    
    command = {
        'id': len(pending_commands) + 1,
        'type': data['type'],
        'data': data.get('data', {}),
        'timestamp': datetime.now().isoformat()
    }
    
    pending_commands.append(command)
    command_history.append(command)
    
    return jsonify({
        'success': True,
        'command': command
    }), 201

@app.route('/api/commands/<int:command_id>/execute', methods=['POST'])
def execute_command(command_id):
    """Mark a command as executed"""
    command = next((c for c in pending_commands if c['id'] == command_id), None)
    
    if not command:
        return jsonify({'error': 'Command not found'}), 404
    
    # Remove command from pending
    pending_commands.remove(command)
    
    return jsonify({
        'success': True,
        'message': 'Command marked as executed.'
    })

@app.route('/api/commands/<int:command_id>', methods=['DELETE'])
def delete_command(command_id):
    """Delete a command"""
    command = next((c for c in pending_commands if c['id'] == command_id), None)
    
    if not command:
        return jsonify({'error': 'Command not found'}), 404
    
    pending_commands.remove(command)
    
    return jsonify({'success': True})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get command history"""
    return jsonify({
        'history': command_history[-50:],  # Last 50 commands
        'count': len(command_history)
    })

@app.route('/api/next-command', methods=['GET'])
def get_next_command():
    """Get the next pending command (for iOS Shortcut)"""
    if pending_commands:
        command = pending_commands[0]  # Get first pending command
        # Return in format that Shortcuts can easily parse
        return jsonify({
            'command_type': command['type'],
            'app_name': command['data'].get('app_name') or command['data'].get('app_id', ''),
            'phone_number': command['data'].get('phone_number', ''),
            'recipient': command['data'].get('recipient', ''),
            'message': command['data'].get('message', ''),
            'shortcut_name': command['data'].get('shortcut_name', ''),
            'command_id': command['id']
        })
    else:
        return jsonify({
            'command_type': 'none',
            'message': 'No pending commands'
        })

@app.route('/execute/<int:command_id>', methods=['GET'])
def execute_redirect(command_id):
    """Redirect page that executes a command via URL scheme"""
    command = next((c for c in pending_commands if c['id'] == command_id), None)
    
    if not command:
        return render_template_string("""
            <html><body>
                <h1>Command not found</h1>
                <p>This command may have already been executed or doesn't exist.</p>
            </body></html>
        """)
    
    # Generate the appropriate URL scheme
    action_url = None
    
    if command['type'] == 'call':
        phone_number = command['data'].get('phone_number', '')
        action_url = f"tel:{phone_number}"
    elif command['type'] == 'send_message':
        recipient = command['data'].get('recipient', '')
        message = command['data'].get('message', '')
        from urllib.parse import quote
        action_url = f"sms:{recipient}?body={quote(message)}"
    elif command['type'] == 'open_app':
        app_name = command['data'].get('app_name', '').lower()
        # Map to known URL schemes
        app_schemes = {
            'messages': 'sms://',
            'phone': 'tel://',
            'mail': 'mailto://',
            'settings': 'App-Prefs://',
            'camera': 'camera://',
        }
        action_url = app_schemes.get(app_name, f"{app_name}://")
    elif command['type'] == 'shortcut':
        shortcut_name = command['data'].get('shortcut_name', '')
        action_url = f"shortcuts://run-shortcut?name={quote(shortcut_name)}"
    
    # Remove from pending
    if command in pending_commands:
        pending_commands.remove(command)
    
    if action_url:
        # Return HTML that immediately redirects
        return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url={action_url}">
            <script>
                window.location.href = "{action_url}";
                setTimeout(function() {{
                    window.location.href = "/";
                }}, 1000);
            </script>
        </head>
        <body>
            <p>Executing command... If nothing happens, <a href="{action_url}">click here</a>.</p>
        </body>
        </html>
        """)
    else:
        return render_template_string("""
            <html><body>
                <h1>Cannot execute command</h1>
                <p>This command type is not supported or the URL scheme is invalid.</p>
                <p><a href="/">Go back</a></p>
            </body></html>
        """)

if __name__ == '__main__':
    print("=" * 60)
    print("Phone Command Server Starting...")
    print("=" * 60)
    print("\nTo access from your iPhone:")
    print("1. Make sure your iPhone is on the same Wi-Fi network")
    print("2. Find your computer's IP address (run 'ipconfig' in CMD)")
    print("3. Open Safari on your iPhone and go to: http://YOUR_IP:5000")
    print("\nServer will start on http://0.0.0.0:5000")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

