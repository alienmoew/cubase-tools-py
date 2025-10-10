@echo off
echo ========================================
echo    CUBASE AUTO TOOLS - BUILD SCRIPT
echo ========================================
echo.

:: Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Virtual environment not detected!
    echo Please activate your venv first:
    echo    venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo Virtual environment detected: %VIRTUAL_ENV%
echo.

:: Run the build script
echo Starting build process...
python build.py

if %errorlevel% neq 0 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    echo Check the 'dist' folder for your executable.
    echo.
    pause
)
