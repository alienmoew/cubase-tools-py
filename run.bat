@echo off
REM Quick run script - Always runs in venv
echo ========================================
echo   Cubase Auto Tool - Quick Launcher
echo ========================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting application...
python main.py

