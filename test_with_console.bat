@echo off
echo ===================================
echo   Testing MovieFlix with Console
echo ===================================
echo.

REM Kill old processes
echo Killing old processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start backend visibly for debugging
echo Starting backend...
start "MovieFlix Backend" venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8765

timeout /t 8 /nobreak

REM Start frontend with console visible to see errors
echo.
echo Starting MovieFlix GUI (watch for errors)...
echo ===================================
echo.
venv\Scripts\python.exe start_movieflix.py

pause
