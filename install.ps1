# Pomodoro Strike PowerShell Installer
# Run as Administrator for Program Files installation

param(
    [string]$InstallPath = "C:\PomodoroStrike",
    [switch]$AddToStartup,
    [switch]$StartupFolder,
    [switch]$Registry,
    [switch]$TaskScheduler
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Pomodoro Strike Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if executable exists
$exePath = "Python\dist\PomodoroStrike.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "Error: PomodoroStrike.exe not found!" -ForegroundColor Red
    Write-Host "Please build the application first using build.bat" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create installation directory
if (-not (Test-Path $InstallPath)) {
    try {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Host "Created installation directory: $InstallPath" -ForegroundColor Green
    }
    catch {
        Write-Host "Error creating directory: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Copy executable
try {
    Copy-Item $exePath $InstallPath -Force
    Write-Host "Copied executable to: $InstallPath" -ForegroundColor Green
}
catch {
    Write-Host "Error copying executable: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create desktop shortcut
try {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Pomodoro Strike.lnk")
    $Shortcut.TargetPath = "$InstallPath\PomodoroStrike.exe"
    $Shortcut.Save()
    Write-Host "Created desktop shortcut" -ForegroundColor Green
}
catch {
    Write-Host "Error creating desktop shortcut: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Add to startup if requested
if ($AddToStartup) {
    Write-Host ""
    Write-Host "Adding to startup..." -ForegroundColor Yellow
    
    if ($StartupFolder -or (-not $Registry -and -not $TaskScheduler)) {
        # Startup folder method
        try {
            $startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
            Copy-Item "$env:USERPROFILE\Desktop\Pomodoro Strike.lnk" $startupPath -Force
            Write-Host "Added to startup folder" -ForegroundColor Green
        }
        catch {
            Write-Host "Error adding to startup folder: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    if ($Registry) {
        # Registry method
        try {
            $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
            Set-ItemProperty -Path $regPath -Name "PomodoroStrike" -Value "$InstallPath\PomodoroStrike.exe"
            Write-Host "Added to registry startup" -ForegroundColor Green
        }
        catch {
            Write-Host "Error adding to registry: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    if ($TaskScheduler) {
        # Task Scheduler method
        try {
            $action = New-ScheduledTaskAction -Execute "$InstallPath\PomodoroStrike.exe"
            $trigger = New-ScheduledTaskTrigger -AtLogOn
            $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
            Register-ScheduledTask -TaskName "PomodoroStrike" -Action $action -Trigger $trigger -Principal $principal -Force
            Write-Host "Created scheduled task" -ForegroundColor Green
        }
        catch {
            Write-Host "Error creating scheduled task: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Summary:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Location: $InstallPath" -ForegroundColor White
Write-Host "Desktop Shortcut: Created" -ForegroundColor White
if ($AddToStartup) { Write-Host "Startup: Configured" -ForegroundColor White }
Write-Host ""
Write-Host "Pomodoro Strike is ready to use!" -ForegroundColor Green
Write-Host "You can now run the application from your desktop shortcut." -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit" 