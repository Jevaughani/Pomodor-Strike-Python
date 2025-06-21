@echo off
echo Installing Pomodoro Strike...
echo.

REM Create installation directory
if not exist "%APPDATA%\PomodoroStrike" mkdir "%APPDATA%\PomodoroStrike"

REM Copy executable
copy "dist\PomodoroStrike.exe" "%APPDATA%\PomodoroStrike\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Pomodoro Strike.lnk'); $Shortcut.TargetPath = '%APPDATA%\PomodoroStrike\PomodoroStrike.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo Pomodoro Strike has been installed to: %APPDATA%\PomodoroStrike
echo A desktop shortcut has been created.
echo.
pause
