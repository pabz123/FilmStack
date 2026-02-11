@echo off
REM ========================================
REM MovieFlix LITE Build Script
REM Creates lightweight version without VLC
REM Users install VLC separately
REM ========================================
echo.
echo ========================================
echo   MovieFlix LITE Build
echo   (VLC NOT included)
echo ========================================
echo.
echo This creates a lightweight version:
echo - Size: ~80-100MB (fits GitHub!)
echo - Users install VLC separately
echo - VLC download: https://www.videolan.org/
echo.
pause

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [32m[OK][0m Virtual environment activated
) else (
    echo [31m[ERROR][0m venv not found! Run: python -m venv venv
    pause
    exit /b 1
)

REM Install/Update dependencies
echo.
echo [36mStep 1/5:[0m Installing dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [31m[ERROR][0m Failed to install dependencies
    pause
    exit /b 1
)
echo [32m[OK][0m Dependencies installed

REM Clean old builds
echo.
echo [36mStep 2/5:[0m Cleaning old builds...
if exist build (
    echo Removing build folder...
    rmdir /s /q build
    echo [32m✓[0m build folder removed
)
if exist dist (
    echo Removing dist folder...
    rmdir /s /q dist
    echo [32m✓[0m dist folder removed
)
if not exist build if not exist dist (
    echo [32m✓[0m No old builds to clean
)
echo [32m[OK][0m Ready for fresh build

REM Build with PyInstaller (Lite spec)
echo.
echo [36mStep 3/5:[0m Building LITE executable (2-3 minutes)...
echo.
echo [33mNote:[0m VLC is NOT bundled. Users must install VLC separately.
echo.
pyinstaller MovieFlix_Lite.spec --clean --noconfirm
if errorlevel 1 (
    echo [31m[ERROR][0m Build failed! Check the errors above
    pause
    exit /b 1
)
echo [32m[OK][0m Build completed

REM Copy additional files
echo.
echo [36mStep 4/5:[0m Copying additional files...

REM Create library folder
if not exist dist\MovieFlix\library mkdir dist\MovieFlix\library
echo [32m[OK][0m Created library folder

REM Copy .env
if not exist dist\MovieFlix\.env (
    if exist .env (
        copy .env dist\MovieFlix\.env >nul
        echo [32m[OK][0m Copied .env file
    )
)

REM Create VLC_REQUIRED.txt notice
echo VLC Media Player Required > dist\MovieFlix\VLC_REQUIRED.txt
echo ========================== >> dist\MovieFlix\VLC_REQUIRED.txt
echo. >> dist\MovieFlix\VLC_REQUIRED.txt
echo MovieFlix requires VLC Media Player for video playback. >> dist\MovieFlix\VLC_REQUIRED.txt
echo. >> dist\MovieFlix\VLC_REQUIRED.txt
echo Download VLC (FREE): >> dist\MovieFlix\VLC_REQUIRED.txt
echo https://www.videolan.org/vlc/ >> dist\MovieFlix\VLC_REQUIRED.txt
echo. >> dist\MovieFlix\VLC_REQUIRED.txt
echo Installation: >> dist\MovieFlix\VLC_REQUIRED.txt
echo 1. Download VLC for Windows (64-bit) >> dist\MovieFlix\VLC_REQUIRED.txt
echo 2. Install VLC >> dist\MovieFlix\VLC_REQUIRED.txt
echo 3. Run MovieFlix.exe >> dist\MovieFlix\VLC_REQUIRED.txt
echo. >> dist\MovieFlix\VLC_REQUIRED.txt
echo VLC will be detected automatically! >> dist\MovieFlix\VLC_REQUIRED.txt
echo [32m[OK][0m Created VLC_REQUIRED.txt

REM Copy README
if exist USER_README.txt (
    copy USER_README.txt dist\MovieFlix\README.txt >nul
    echo [32m[OK][0m Copied README
)

REM Create portable archive
echo.
echo [36mStep 5/5:[0m Creating portable archive...
cd dist
if exist MovieFlix_Lite_v1.0.zip del MovieFlix_Lite_v1.0.zip
powershell -Command "Compress-Archive -Path MovieFlix -DestinationPath MovieFlix_Lite_v1.0.zip -CompressionLevel Optimal"
if errorlevel 1 (
    echo [33m[WARNING][0m Failed to create zip archive
) else (
    echo [32m[OK][0m Created MovieFlix_Lite_v1.0.zip
)
cd ..

REM Summary
echo.
echo ========================================
echo   LITE BUILD COMPLETE!
echo ========================================
echo.
echo Location: dist\MovieFlix\
echo Executable: dist\MovieFlix\MovieFlix.exe
echo Archive: dist\MovieFlix_Lite_v1.0.zip
echo.
echo [36mSize Information:[0m
if exist dist\MovieFlix (
    powershell -Command "$size = (Get-ChildItem -Path 'dist\MovieFlix' -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host ('Folder: {0:N2} MB' -f $size)"
)
if exist dist\MovieFlix_Lite_v1.0.zip (
    for %%A in (dist\MovieFlix_Lite_v1.0.zip) do (
        set /a SIZE_MB=%%~zA/1048576
        echo ZIP: %%~zA bytes (~!SIZE_MB! MB^)
    )
)
echo.
echo [32mThis version fits on GitHub! (^<100MB)[0m
echo.
echo [36mIMPORTANT:[0m
echo - Users MUST install VLC from https://www.videolan.org/
echo - VLC_REQUIRED.txt included in package
echo - App will detect VLC automatically
echo.
echo [36mNext Steps:[0m
echo 1. Test: Run dist\MovieFlix\MovieFlix.exe (requires VLC installed)
echo 2. Upload: dist\MovieFlix_Lite_v1.0.zip to GitHub Releases
echo 3. Document: Mention VLC requirement in release notes
echo.
pause
