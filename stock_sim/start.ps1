# PowerShell script to start the Stock Trading Simulator

Write-Host "Starting Stock Trading Simulator..." -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

# Check if port is in use
$portInUse = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Warning: Port 3000 is already in use!" -ForegroundColor Red
    Write-Host "Please stop the other process first." -ForegroundColor Red
    Write-Host ""
    Write-Host "To find the process, run: Get-NetTCPConnection -LocalPort 3000" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the server
Write-Host "Starting server on http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
node server.js




