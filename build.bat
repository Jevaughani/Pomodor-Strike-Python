@echo off
echo Building Pomodoro Strike Executable...
echo.

cd Python

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller

REM Run the build script
echo.
echo Starting build process...
python build_exe.py

echo.
echo Build process completed!
echo Check the 'dist' folder for the executable.
pause 