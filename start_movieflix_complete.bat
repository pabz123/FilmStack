@echo off
REM MovieFlix Complete Launcher - Starts backend and app automatically

title MovieFlix Launcher

echo ========================================
echo   MovieFlix Launcher
echo ========================================
echo.

REM Change to movie_library directory
cd /d "%~dp0"

echo Step 1: Checking if backend is already running...
curl -s http://localhost:8765/docs > nul 2>&1
if %errorlevel% == 0 (
    echo + Backend is already running
    goto :launch_app
)

echo.
echo Step 2: Checking if port 8765 is in use...
netstat -ano | findstr ":8765.*LISTENING" > nul 2>&1
if %errorlevel% == 0 (
    echo ! Port 8765 is in use by another process
    echo.
    echo Attempting to free port 8765...
    
    REM Kill processes on port 8765
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8765.*LISTENING"') do (
        echo   Killing process PID: %%a
        taskkill /F /PID %%a > nul 2>&1
    )
    
    timeout /t 2 /nobreak > nul
    echo   + Port freed!
)

echo.
echo Step 3: Starting backend server...
start "MovieFlix Backend" /MIN venv\Scripts\pythonw.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8765

echo.
echo Step 4: Waiting for backend to start...
timeout /t 2 /nobreak > nul

REM Wait for backend to be ready (max 15 seconds)
set /a count=0
:wait_backend
curl -s http://localhost:8765/docs > nul 2>&1
if %errorlevel% neq 0 (
    set /a count+=1
    if %count% geq 30 (
        echo.
        echo ========================================
        echo   ERROR: Backend Failed to Start!
        echo ========================================
        echo.
        echo The backend server did not start within 15 seconds.
        echo.
        echo Troubleshooting:
        echo   1. Check if port 8765 is already in use:
        echo      netstat -ano ^| findstr :8765
        echo.
        echo   2. Try starting backend manually:
        echo      venv\Scripts\python.exe -m uvicorn backend.main:app --port 8765
        echo.
        echo   3. Check for errors in the output
        echo.
        pause
        exit /b 1
    )
    timeout /t 0.5 /nobreak > nul
    goto :wait_backend
)

echo + Backend is ready!
echo.

:launch_app
echo Step 5: Launching MovieFlix...
echo.

REM Check if we should use .exe or Python script
if exist "MovieFlix.exe" (
    echo Starting MovieFlix.exe...
    start "" "MovieFlix.exe"
) else (
    echo Starting with Python...
    start "" venv\Scripts\pythonw.exe start_movieflix.py
)

echo.
echo ========================================
echo   MovieFlix is starting!
echo ========================================
echo.
echo If login says "Unable to connect to backend":
echo   1. Wait a few more seconds
echo   2. Or restart this launcher
echo.
echo Note: Backend is running in background.
echo To stop backend, run:
echo   taskkill /F /FI "WINDOWTITLE eq MovieFlix Backend*"
echo.
echo You can close this window now.
echo.
timeout /t 5
exit
