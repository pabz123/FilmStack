@echo off
REM Build MovieFlix.exe with PyInstaller
REM This creates a standalone executable with icon and VLC support

echo ========================================
echo   MovieFlix .exe Builder
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "start_movieflix.py" (
    echo ERROR: start_movieflix.py not found!
    echo Please run this script from the FilmStack directory
    pause
    exit /b 1
)

REM Check for Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Try to find Python executable (venv or system)
set PYTHON_EXE=python
if exist "venv\Scripts\python.exe" (
    set PYTHON_EXE=venv\Scripts\python.exe
    echo Using virtual environment Python
) else (
    echo Using system Python
)

echo Step 1: Installing PyInstaller...
%PYTHON_EXE% -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 2: Cleaning old builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "MovieFlix.exe" del /f /q MovieFlix.exe

echo Step 3: Verifying required files...
if not exist "MovieFlix.spec" (
    echo ERROR: MovieFlix.spec not found!
    pause
    exit /b 1
)

echo Step 4: Building MovieFlix.exe...
echo This may take 2-5 minutes...
echo.
%PYTHON_EXE% -m PyInstaller --clean --noconfirm MovieFlix.spec

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
echo Common issues:
echo - Missing Python dependencies (run: pip install -r requirements.txt)
echo - Missing required files (check if all files are present)
echo - Antivirus blocking PyInstaller
echo.
)

pause