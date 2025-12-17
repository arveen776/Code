# Troubleshooting Guide

## Common Errors and Solutions

### Error: Port 3000 is already in use

**Solution:**
1. Find the process using port 3000:
   ```powershell
   netstat -ano | findstr :3000
   ```
2. Kill the process (replace PID with the actual process ID):
   ```powershell
   taskkill /PID <PID> /F
   ```
3. Or change the port in `server.js` (line 17):
   ```javascript
   const PORT = 3001; // or any other available port
   ```

### Error: Cannot find module 'xxx'

**Solution:**
```bash
npm install
```

This installs all required dependencies.

### Error: EADDRINUSE

This means the port is already in use. See solution above.

### Error when loading services

If you see errors about missing modules in the `services/` or `config/` folders:

1. Make sure all files exist:
   - `config/apiConfig.js`
   - `services/polygonService.js`
   - `services/alphaVantageService.js`
   - `services/stockDataService.js`

2. Check file permissions

3. Reinstall dependencies:
   ```bash
   rm -rf node_modules
   npm install
   ```

### Server starts but shows API errors

This is normal if you haven't configured API keys. The app will use mock data.

To fix:
1. Get API keys (see SETUP.md)
2. Create `.env` file with your keys
3. Restart the server

### WebSocket connection errors

If you see WebSocket errors in the browser console:

1. Make sure Socket.IO is installed:
   ```bash
   npm install socket.io
   ```

2. Check browser console for specific errors

3. Make sure you're accessing via `http://localhost:3000` (not file://)

## Getting Help

To see the exact error:

1. **Windows PowerShell:**
   ```powershell
   node server.js
   ```

2. **Check the full error message** - it will tell you:
   - Which module is missing
   - Which line has the error
   - What the problem is

3. **Common issues:**
   - Missing dependencies → Run `npm install`
   - Port in use → Kill the process or change port
   - Syntax error → Check the error message for the file and line

## Testing the Server

1. **Check if server starts:**
   ```bash
   node server.js
   ```
   You should see: "Stock Simulator server running on http://localhost:3000"

2. **Test in browser:**
   - Open http://localhost:3000
   - Check browser console (F12) for errors

3. **Test API endpoints:**
   - http://localhost:3000/api/symbols
   - Should return JSON with stock symbols

## Still Having Issues?

1. Share the **exact error message** you're seeing
2. Check which step fails:
   - Installing dependencies?
   - Starting the server?
   - Loading the webpage?
3. Check Node.js version:
   ```bash
   node --version
   ```
   Should be v14 or higher.




