@echo off
SETLOCAL EnableDelayedExpansion

echo =========================================
echo   MovieFlix Debug Test
echo =========================================
echo.

REM Kill all python processes
echo [1/5] Killing old processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo       Done.
echo.

REM Clear old log
echo [2/5] Clearing old log...
del movieflix_startup.log >nul 2>&1
echo       Done.
echo.

REM Start backend in separate window
echo [3/5] Starting backend in separate window...
start "Backend" venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8765
timeout /t 8 /nobreak >nul
echo       Done. Backend should be running.
echo.

REM Test backend
echo [4/5] Testing backend...
curl -s http://127.0.0.1:8765/health
echo.
echo       If you see JSON above, backend is OK.
echo.

REM Start frontend with full console output using VENV PYTHON
echo [5/5] Starting MovieFlix Frontend...
echo =========================================
echo   WATCH THE OUTPUT BELOW:
echo   It will show exactly where it hangs!
echo =========================================
echo.
echo Using Python from venv...
venv\Scripts\python.exe start_movieflix.py
echo.
echo =========================================
echo   MovieFlix closed
echo =========================================
echo.

REM Show log
echo Startup log:
echo =========================================
type movieflix_startup.log 2>nul
echo =========================================

pause
