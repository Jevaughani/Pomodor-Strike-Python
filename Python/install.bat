@echo off
echo ========================================
echo    Pomodoro Strike Installer
echo ========================================
echo.

REM Check if executable exists
if not exist "dist\PomodoroStrike.exe" (
    echo Error: PomodoroStrike.exe not found in dist folder!
    echo Please build the application first using build.bat
    pause
    exit /b 1
)

echo Installation Options:
echo 1. Install to AppData (Default - Recommended)
echo 2. Install to C:\PomodoroStrike
echo 3. Install to Program Files (Requires Admin)
echo 4. Custom location
echo.
set /p choice="Choose installation option (1-4): "

if "%choice%"=="1" goto appdata
if "%choice%"=="2" goto cdrive
if "%choice%"=="3" goto programfiles
if "%choice%"=="4" goto custom
goto appdata

:appdata
echo.
echo Installing to AppData...
set INSTALL_DIR=%APPDATA%\PomodoroStrike
goto install

:cdrive
echo.
echo Installing to C:\PomodoroStrike...
set INSTALL_DIR=C:\PomodoroStrike
goto install

:programfiles
echo.
echo Installing to Program Files...
set INSTALL_DIR=C:\Program Files\PomodoroStrike
goto install

:custom
echo.
set /p INSTALL_DIR="Enter installation path: "
goto install

:install
REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo Copying files...
copy "dist\PomodoroStrike.exe" "%INSTALL_DIR%\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Pomodoro Strike.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\PomodoroStrike.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo Pomodoro Strike has been installed to: %INSTALL_DIR%
echo A desktop shortcut has been created.
echo.

REM Ask about startup
set /p startup="Add to startup? (y/n): "
if /i "%startup%"=="y" goto addstartup
goto finish

:addstartup
echo.
echo Startup Options:
echo 1. Startup Folder (Recommended)
echo 2. Registry (Requires Admin)
echo 3. Task Scheduler (Most Reliable)
echo.
set /p startup_choice="Choose startup method (1-3): "

if "%startup_choice%"=="1" goto startupfolder
if "%startup_choice%"=="2" goto registry
if "%startup_choice%"=="3" goto taskscheduler
goto startupfolder

:startupfolder
echo Adding to startup folder...
copy "%USERPROFILE%\Desktop\Pomodoro Strike.lnk" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
echo Added to startup folder successfully!
goto finish

:registry
echo Adding to registry startup...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "PomodoroStrike" /t REG_SZ /d "%INSTALL_DIR%\PomodoroStrike.exe" /f
echo Added to registry startup successfully!
goto finish

:taskscheduler
echo Creating scheduled task...
schtasks /create /tn "PomodoroStrike" /tr "%INSTALL_DIR%\PomodoroStrike.exe" /sc onlogon /ru "%USERNAME%" /f
echo Created scheduled task successfully!
goto finish

:finish
echo.
echo ========================================
echo Installation Summary:
echo ========================================
echo Location: %INSTALL_DIR%
echo Desktop Shortcut: Created
if "%startup%"=="y" echo Startup: Configured
echo.
echo Pomodoro Strike is ready to use!
echo You can now run the application from your desktop shortcut.
echo.
pause
