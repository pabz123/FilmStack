@echo off
REM ========================================
REM MovieFlix Clean Build Folders
REM Removes build and dist folders
REM ========================================
echo.
echo ========================================
echo   Clean Build Folders
echo ========================================
echo.

set CLEANED=0

if exist build (
    echo Removing build folder...
    rmdir /s /q build
    if not exist build (
        echo [32m✓ build folder removed[0m
        set CLEANED=1
    ) else (
        echo [31m✗ Failed to remove build folder[0m
    )
) else (
    echo [90m○ build folder doesn't exist[0m
)

if exist dist (
    echo Removing dist folder...
    rmdir /s /q dist
    if not exist dist (
        echo [32m✓ dist folder removed[0m
        set CLEANED=1
    ) else (
        echo [31m✗ Failed to remove dist folder[0m
    )
) else (
    echo [90m○ dist folder doesn't exist[0m
)

echo.
if %CLEANED%==1 (
    echo [32mCleaned successfully![0m
) else (
    echo [90mNothing to clean[0m
)
echo.
echo You can now run build_lite.bat
echo.
pause
