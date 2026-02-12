@echo off
echo ================================================
echo Collecting all error logs
echo ================================================

echo. > all_errors.txt
echo ================================================ >> all_errors.txt
echo MOVIEFLIX ERROR REPORT >> all_errors.txt
echo Generated: %date% %time% >> all_errors.txt
echo ================================================ >> all_errors.txt

if exist movieflix_startup.log (
    echo. >> all_errors.txt
    echo ======== STARTUP LOG ======== >> all_errors.txt
    type movieflix_startup.log >> all_errors.txt
) else (
    echo. >> all_errors.txt
    echo No startup log found >> all_errors.txt
)

if exist backend_error.log (
    echo. >> all_errors.txt
    echo ======== BACKEND ERROR LOG ======== >> all_errors.txt
    type backend_error.log >> all_errors.txt
) else (
    echo. >> all_errors.txt
    echo No backend error log found >> all_errors.txt
)

if exist dist\MovieFlix\*.log (
    echo. >> all_errors.txt
    echo ======== DIST FOLDER LOGS ======== >> all_errors.txt
    type dist\MovieFlix\*.log >> all_errors.txt
) else (
    echo. >> all_errors.txt
    echo No logs in dist folder >> all_errors.txt
)

echo.
echo ================================================
echo All errors collected in: all_errors.txt
echo ================================================
echo.
echo Opening file...
notepad all_errors.txt

pause
