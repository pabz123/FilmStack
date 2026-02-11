@echo off
REM ========================================
REM MovieFlix DEBUG Build
REM Creates version with console window to see errors
REM ========================================
echo.
echo ========================================
echo   MovieFlix DEBUG Build
echo   Console window ENABLED
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [32m[OK][0m Virtual environment activated
) else (
    echo [31m[ERROR][0m venv not found!
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo [32m[OK][0m Dependencies installed

REM Clean old builds
echo.
echo Cleaning old debug builds...
if exist build (
    echo Removing build folder...
    rmdir /s /q build
    echo [32m✓[0m build folder removed
)
if exist dist\MovieFlix_Debug (
    echo Removing old debug dist folder...
    rmdir /s /q dist\MovieFlix_Debug
    echo [32m✓[0m dist\MovieFlix_Debug folder removed
)
echo [32m[OK][0m Cleaned

REM Build with debug spec
echo.
echo Building DEBUG version (console enabled)...
echo This will show all errors in console window!
echo.
pyinstaller MovieFlix_Debug.spec --clean --noconfirm
if errorlevel 1 (
    echo [31m[ERROR][0m Build failed!
    pause
    exit /b 1
)
echo [32m[OK][0m Debug build completed

REM Copy files
echo.
echo Copying files...
if not exist dist\MovieFlix_Debug\library mkdir dist\MovieFlix_Debug\library
if exist .env copy .env dist\MovieFlix_Debug\.env >nul

REM Create instruction file
echo DEBUG VERSION > dist\MovieFlix_Debug\DEBUG_INFO.txt
echo ============= >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo. >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo This is a DEBUG build with console window enabled. >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo. >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo When you run MovieFlix_Debug.exe, a console window will appear. >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo This shows all startup messages and errors. >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo. >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo Look for error messages in the console! >> dist\MovieFlix_Debug\DEBUG_INFO.txt
echo Copy any errors you see and report them. >> dist\MovieFlix_Debug\DEBUG_INFO.txt

echo.
echo ========================================
echo   DEBUG BUILD COMPLETE!
echo ========================================
echo.
echo Location: dist\MovieFlix_Debug\
echo Executable: dist\MovieFlix_Debug\MovieFlix_Debug.exe
echo.
echo [36mIMPORTANT:[0m
echo - This build has a CONSOLE WINDOW
echo - You will see all error messages
echo - Copy any errors and send them back
echo.
echo [33mTo test:[0m
echo 1. cd dist\MovieFlix_Debug
echo 2. Run MovieFlix_Debug.exe
echo 3. Watch the console for errors
echo 4. Take screenshot of any error messages
echo.
pause
