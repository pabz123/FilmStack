@echo off
REM Build MovieFlix.exe with PyInstaller
REM This creates a standalone executable with icon and VLC support

echo ========================================
echo   MovieFlix .exe Builder
echo ========================================
echo.

echo Step 1: Installing PyInstaller...
venv\Scripts\python.exe -m pip install pyinstaller --quiet

echo Step 2: Cleaning old builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "MovieFlix.exe" del /f /q MovieFlix.exe

echo Step 3: Building MovieFlix.exe...
echo This may take 2-5 minutes...
echo.
venv\Scripts\pyinstaller --clean --noconfirm MovieFlix.spec

if exist "dist\MovieFlix.exe" (
    echo.
    echo ========================================
    echo   SUCCESS!
    echo ========================================
    echo.
    echo MovieFlix.exe created in dist\ folder
    echo.
    echo Moving to root directory...
    move /y "dist\MovieFlix.exe" "MovieFlix.exe"
    
    echo.
    echo ========================================
    echo   NEXT STEPS:
    echo ========================================
    echo.
    echo 1. Run MovieFlix.exe to test
    echo 2. Create desktop shortcut:
    echo    Right-click MovieFlix.exe ^> Send to ^> Desktop
    echo.
    echo 3. The .exe includes:
    echo    - Custom red M icon
    echo    - VLC integration
    echo    - No console window
    echo    - Portable (can copy to other PCs)
    echo.
    
    REM Clean up build artifacts
    echo Cleaning up build files...
    rmdir /s /q build
    rmdir /s /q dist
    
    echo.
    echo Build complete! Launch MovieFlix.exe to start!
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR!
    echo ========================================
    echo.
    echo Build failed. Check the error messages above.
    echo.
)

pause
