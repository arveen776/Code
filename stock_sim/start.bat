@echo off
echo Starting Stock Trading Simulator...
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    echo.
)

REM Check if port is in use
netstat -ano | findstr :3000 >nul
if %errorlevel% == 0 (
    echo Warning: Port 3000 is already in use!
    echo Please stop the other process first.
    echo.
    pause
    exit /b 1
)

REM Start the server
echo Starting server on http://localhost:3000
echo Press Ctrl+C to stop
echo.
node server.js




