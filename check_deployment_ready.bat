@echo off
REM ========================================
REM MovieFlix Deployment Readiness Check
REM ========================================
echo.
echo ========================================
echo   MovieFlix Deployment Readiness
echo ========================================
echo.

set READY=1

REM Check Python
echo [1/8] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [31m[FAIL][0m Python not found
    set READY=0
) else (
    python --version
    echo [32m[OK][0m Python installed
)

REM Check venv
echo.
echo [2/8] Checking virtual environment...
if exist venv\Scripts\activate.bat (
    echo [32m[OK][0m Virtual environment exists
) else (
    echo [31m[FAIL][0m venv not found - Run: python -m venv venv
    set READY=0
)

REM Check requirements
echo.
echo [3/8] Checking dependencies...
if exist requirements.txt (
    echo [32m[OK][0m requirements.txt found
) else (
    echo [31m[FAIL][0m requirements.txt missing
    set READY=0
)

REM Check icon
echo.
echo [4/8] Checking icon...
if exist MovieFlix.ico (
    echo [32m[OK][0m MovieFlix.ico found
) else (
    echo [33m[WARN][0m MovieFlix.ico not found (installer will have no icon)
)

REM Check VLC
echo.
echo [5/8] Checking VLC folder...
if exist VLC (
    echo [32m[OK][0m VLC folder found - Will be bundled
) else (
    echo [33m[WARN][0m VLC folder not found
    echo          Users will need VLC installed
    echo          Download from: https://www.videolan.org/
)

REM Check spec file
echo.
echo [6/8] Checking PyInstaller spec...
if exist MovieFlix.spec (
    echo [32m[OK][0m MovieFlix.spec found
) else (
    echo [31m[FAIL][0m MovieFlix.spec missing
    set READY=0
)

REM Check Inno Setup (optional)
echo.
echo [7/8] Checking Inno Setup (optional)...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo [32m[OK][0m Inno Setup 6 installed (x86)
    echo          Can create professional installer
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    echo [32m[OK][0m Inno Setup 6 installed
    echo          Can create professional installer
) else (
    echo [33m[INFO][0m Inno Setup not installed
    echo          Will only create portable version
    echo          Download from: https://jrsoftware.org/isinfo.php
)

REM Check disk space
echo.
echo [8/8] Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set FREESPACE=%%a
echo     Free space: %FREESPACE% bytes
echo [32m[OK][0m Sufficient space

REM Summary
echo.
echo ========================================
if %READY%==1 (
    echo   [32mREADY TO BUILD![0m
    echo ========================================
    echo.
    echo Everything looks good! You can now:
    echo.
    echo 1. Build portable version:
    echo    [36mbuild_professional.bat[0m
    echo.
    echo 2. Build everything (portable + installer):
    echo    [36mdeploy_complete.bat[0m
    echo.
    echo Estimated build time: 3-5 minutes
    echo Expected output size: 150-250 MB
) else (
    echo   [31mNOT READY[0m
    echo ========================================
    echo.
    echo Please fix the issues marked [FAIL] above
    echo.
    echo Common fixes:
    echo - Install Python 3.11+
    echo - Create venv: python -m venv venv
    echo - Activate venv: venv\Scripts\activate
    echo - Install deps: pip install -r requirements.txt
)
echo.
pause
