@echo off
if "%1"=="" (
    echo Usage: send_command.bat [command] [arguments]
    echo.
    echo Examples:
    echo   send_command.bat open_app messages
    echo   send_command.bat send_message +1234567890 "Hello"
    echo   send_command.bat call +1234567890
    echo   send_command.bat shortcut "My Shortcut"
    echo   send_command.bat list
    exit /b
)
python client.py %*

