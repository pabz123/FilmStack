@echo off
echo Testing Lite Build...
echo.

cd dist\MovieFlix
echo Running MovieFlix.exe...
MovieFlix.exe > ..\..\lite_output.log 2>&1

echo.
echo Check lite_output.log for any output
pause
