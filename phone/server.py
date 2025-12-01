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
command_id_counter = 0  # Unique ID counter

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
        .auto-execute-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px 20px;
            border-radius: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
        }
        .toggle-switch {
            position: relative;
            width: 50px;
            height: 26px;
            background: #ccc;
            border-radius: 13px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .toggle-switch.active {
            background: #667eea;
        }
        .toggle-switch::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: white;
            top: 3px;
            left: 3px;
            transition: left 0.3s;
        }
        .toggle-switch.active::after {
            left: 27px;
        }
        .auto-executing {
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="auto-execute-toggle">
        <span style="font-size: 14px; color: #333;">Auto Execute</span>
        <div class="toggle-switch active" id="autoToggle" onclick="toggleAutoExecute()"></div>
    </div>
    <div class="container">
        <h1>📱 Phone Commands</h1>
        <div class="status" id="status">Waiting for commands... (Auto-execute: ON)</div>
        <div id="commands-container">
            <div class="no-commands">No pending commands</div>
        </div>
    </div>
    <button class="refresh-btn" onclick="loadCommands()">↻</button>

    <script>
        let commandIds = new Set();
        let autoExecute = true; // Auto-execute enabled by default
        let executingCommands = new Set(); // Track commands being executed

        function toggleAutoExecute() {
            autoExecute = !autoExecute;
            const toggle = document.getElementById('autoToggle');
            const status = document.getElementById('status');
            
            if (autoExecute) {
                toggle.classList.add('active');
                status.textContent = status.textContent.replace(/\(Auto-execute: (ON|OFF)\)/, '(Auto-execute: ON)');
            } else {
                toggle.classList.remove('active');
                status.textContent = status.textContent.replace(/\(Auto-execute: (ON|OFF)\)/, '(Auto-execute: OFF)');
            }
            
            // Save preference to localStorage
            localStorage.setItem('autoExecute', autoExecute);
        }

        // Load auto-execute preference
        const savedAutoExecute = localStorage.getItem('autoExecute');
        if (savedAutoExecute !== null) {
            autoExecute = savedAutoExecute === 'true';
            if (!autoExecute) {
                document.getElementById('autoToggle').classList.remove('active');
            }
        }

        function loadCommands() {
            fetch('/api/commands')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('commands-container');
                    const status = document.getElementById('status');
                    
                    if (data.commands.length === 0) {
                        container.innerHTML = '<div class="no-commands">No pending commands</div>';
                        const autoStatus = autoExecute ? '(Auto-execute: ON)' : '(Auto-execute: OFF)';
                        status.textContent = `Waiting for commands... ${autoStatus}`;
                        return;
                    }

                    const autoStatus = autoExecute ? '(Auto-execute: ON)' : '(Auto-execute: OFF)';
                    status.textContent = `${data.commands.length} pending command(s) ${autoStatus}`;
                    container.innerHTML = '';

                    data.commands.forEach(cmd => {
                        if (!commandIds.has(cmd.id)) {
                            commandIds.add(cmd.id);
                            const card = createCommandCard(cmd);
                            container.appendChild(card);
                            
                            // Auto-execute if enabled and not already executing
                            if (autoExecute && !executingCommands.has(cmd.id)) {
                                // Small delay to ensure UI is updated
                                setTimeout(() => {
                                    executeCommand(cmd.id, true); // true = auto-execute
                                }, 500);
                            }
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

        function executeCommand(cmdId, isAutoExecute = false) {
            // Prevent duplicate execution
            if (executingCommands.has(cmdId)) {
                return;
            }
            executingCommands.add(cmdId);
            
            // Update UI to show executing state
            const card = document.getElementById(`cmd-${cmdId}`);
            if (card) {
                card.classList.add('auto-executing');
            }
            
                    // Get command data from the stored commands
                    fetch(`/api/commands`)
                        .then(response => response.json())
                        .then(data => {
                            const command = data.commands.find(c => c.id === cmdId);
                            if (!command) {
                                executingCommands.delete(cmdId);
                                // Command might have been executed already or doesn't exist
                                // Remove from UI if it exists
                                const card = document.getElementById(`cmd-${cmdId}`);
                                if (card) {
                                    card.remove();
                                    commandIds.delete(cmdId);
                                }
                                if (!isAutoExecute) {
                                    console.log('Command not found - may have been executed already');
                                }
                                return;
                            }
                    
                    // Get action URL
                    let actionUrl = getActionUrl(command);
                    
                    if (actionUrl) {
                        // Execute the command
                        // Use multiple methods to ensure it works
                        const executeAction = () => {
                            // Try iframe method first (most reliable for auto-execution)
                            const iframe = document.createElement('iframe');
                            iframe.style.display = 'none';
                            iframe.src = actionUrl;
                            document.body.appendChild(iframe);
                            
                            // Also try direct navigation as backup
                            setTimeout(() => {
                                try {
                                    window.location.href = actionUrl;
                                } catch (e) {
                                    // Fallback: create and click link
                                    const link = document.createElement('a');
                                    link.href = actionUrl;
                                    link.style.display = 'none';
                                    document.body.appendChild(link);
                                    link.click();
                                    setTimeout(() => document.body.removeChild(link), 100);
                                }
                            }, 100);
                            
                            // Remove iframe after a delay
                            setTimeout(() => {
                                if (iframe.parentNode) {
                                    document.body.removeChild(iframe);
                                }
                            }, 1000);
                        };
                        
                        executeAction();
                        
                        // Mark as executed on server (don't wait for response)
                        fetch(`/api/commands/${cmdId}/execute`, { method: 'POST' })
                            .then(response => {
                                if (response.ok) {
                                    return response.json();
                                } else {
                                    // Command might have been executed already
                                    console.log('Command may have been executed already');
                                    return { success: true };
                                }
                            })
                            .then(data => {
                                // Remove from UI after a delay
                                setTimeout(() => {
                                    const card = document.getElementById(`cmd-${cmdId}`);
                                    if (card) {
                                        card.remove();
                                        commandIds.delete(cmdId);
                                    }
                                    executingCommands.delete(cmdId);
                                    loadCommands(); // Refresh to update UI
                                }, 1500);
                            })
                            .catch(error => {
                                console.error('Error marking command as executed:', error);
                                // Still remove from UI even if API call fails
                                setTimeout(() => {
                                    executingCommands.delete(cmdId);
                                    loadCommands();
                                }, 1500);
                            });
                    } else {
                        executingCommands.delete(cmdId);
                        if (!isAutoExecute) {
                            alert('Could not generate action URL for this command. Please set up the iOS Shortcut first (see SHORTCUT_SETUP.md)');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error executing command:', error);
                    executingCommands.delete(cmdId);
                    if (!isAutoExecute) {
                        alert('Error executing command');
                    }
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

        // Auto-refresh more frequently for auto-execution (every 1 second)
        setInterval(loadCommands, 1000);
        
        // Load commands on page load
        loadCommands();
        
        // Also try to keep page active (prevents iOS from pausing JavaScript)
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                loadCommands();
            }
        });
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
    global command_id_counter
    data = request.json
    
    if not data or 'type' not in data:
        return jsonify({'error': 'Invalid command format'}), 400
    
    # Use a unique counter for IDs instead of len(pending_commands)
    command_id_counter += 1
    
    command = {
        'id': command_id_counter,
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
        # Command might have been executed already, try to redirect back
        return render_template_string("""
            <html><body>
                <h1>Command not found</h1>
                <p>This command may have already been executed or doesn't exist.</p>
                <p><a href="/">Go back to command page</a></p>
                <script>
                    setTimeout(function() {
                        window.location.href = "/";
                    }, 2000);
                </script>
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
        from urllib.parse import quote
        action_url = f"shortcuts://run-shortcut?name={quote(shortcut_name)}"
    
    # Don't remove command here - let the API endpoint handle it
    # This prevents race conditions
    
    if action_url:
        # Return HTML that immediately redirects
        return render_template_string(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url={action_url}">
            <script>
                // Mark as executed in background
                fetch('/api/commands/{command_id}/execute', {{ method: 'POST' }})
                    .catch(err => console.log('Mark executed:', err));
                
                // Redirect to action
                window.location.href = "{action_url}";
                
                // Fallback: redirect back after delay
                setTimeout(function() {{
                    window.location.href = "/";
                }}, 2000);
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

