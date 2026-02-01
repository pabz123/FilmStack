@echo off
REM MovieFlix Silent Desktop Shortcut Creator
REM Creates a desktop shortcut that starts MovieFlix completely silently

echo ========================================
echo   MovieFlix Silent Launcher Setup
echo ========================================
echo.

REM Get current directory
set "MOVIEFLIX_DIR=%~dp0"

echo Creating silent desktop shortcut...
echo.

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\MovieFlix.lnk'); $Shortcut.TargetPath = '%MOVIEFLIX_DIR%MovieFlix_Silent.vbs'; $Shortcut.WorkingDirectory = '%MOVIEFLIX_DIR%'; $Shortcut.IconLocation = '%MOVIEFLIX_DIR%MovieFlix.ico'; $Shortcut.Description = 'MovieFlix - Your Personal Netflix'; $Shortcut.WindowStyle = 1; $Shortcut.Save()"

if %errorlevel% == 0 (
    echo ========================================
    echo   SUCCESS!
    echo ========================================
    echo.
    echo Desktop shortcut created: MovieFlix
    echo.
    echo Features:
    echo   ✓ Completely silent startup
    echo   ✓ No console windows
    echo   ✓ Backend starts automatically
    echo   ✓ Professional app experience
    echo.
    echo How it works:
    echo   1. Kills any old processes on port 8765
    echo   2. Starts backend silently in background
    echo   3. Waits for backend to be ready
    echo   4. Launches MovieFlix UI
    echo   5. All without showing any windows!
    echo.
    echo Double-click "MovieFlix" on your desktop to start!
    echo.
) else (
    echo ========================================
    echo   ERROR
    echo ========================================
    echo.
    echo Failed to create desktop shortcut.
    echo.
    echo Try running as Administrator.
    echo.
)

pause
