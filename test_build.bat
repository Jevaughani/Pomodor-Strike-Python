@echo off
echo Testing Pomodoro Strike Build Process
echo ======================================
echo.

REM Check if we're in the right directory
if not exist "Python\pomodoro_strike.py" (
    echo Error: pomodoro_strike.py not found in Python folder!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

echo ✅ Found pomodoro_strike.py
echo.

REM Change to Python directory and run build
cd Python
echo Running build script...
python build_exe.py

REM Check if build was successful
if exist "dist\PomodoroStrike.exe" (
    echo.
    echo ✅ Build successful!
    echo 📁 Executable location: %CD%\dist\PomodoroStrike.exe
    echo 📏 File size: 
    for %%A in (dist\PomodoroStrike.exe) do echo    %%~zA bytes
    echo.
    echo 🧪 Testing executable...
    echo Starting Pomodoro Strike (will close automatically for testing)...
    timeout /t 3 /nobreak >nul
    start /wait dist\PomodoroStrike.exe
    echo ✅ Executable test completed!
) else (
    echo.
    echo ❌ Build failed! Executable not found.
    echo Check the error messages above.
)

echo.
pause 