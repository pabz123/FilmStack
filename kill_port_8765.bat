@echo off
REM Kill all processes using port 8765

echo ========================================
echo   Kill Port 8765 Processes
echo ========================================
echo.

echo Checking for processes on port 8765...
echo.

REM Find processes using port 8765
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8765.*LISTENING"') do (
    echo Found process with PID: %%a
    echo Killing process...
    taskkill /F /PID %%a
    echo.
)

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak > nul

echo.
echo Verifying port 8765 is free...
netstat -ano | findstr ":8765.*LISTENING"

if %errorlevel% == 0 (
    echo.
    echo Port 8765 is still in use!
    echo Try running this script again or restart your computer.
) else (
    echo.
    echo ========================================
    echo   SUCCESS!
    echo ========================================
    echo.
    echo Port 8765 is now FREE!
    echo You can now start MovieFlix.
)

echo.
pause
