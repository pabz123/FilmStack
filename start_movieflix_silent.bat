@echo off
REM MovieFlix Silent Launcher - No console windows!
REM This starts everything in the background

cd /d "%~dp0"

REM Kill any existing processes on port 8765 silently
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8765.*LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Wait a moment for port cleanup
timeout /t 1 /nobreak >nul 2>&1

REM Start backend silently (no window) using pythonw.exe
start "" /B venv\Scripts\pythonw.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8765

REM Wait for backend to be ready (max 10 seconds)
set /a count=0
:wait_backend
timeout /t 1 /nobreak >nul 2>&1
curl -s http://localhost:8765/docs >nul 2>&1
if %errorlevel% neq 0 (
    set /a count+=1
    if %count% lss 10 goto :wait_backend
)

REM Backend ready or timed out, launch MovieFlix (no window)
start "" venv\Scripts\pythonw.exe start_movieflix.py

REM Exit silently
exit
