# Pomodoro Strike - Python Version

A modern, feature-rich Pomodoro timer application built with Python and CustomTkinter. Designed to boost productivity with a beautiful dark theme, comprehensive task management, advanced notifications, and powerful productivity tracking.

![Pomodoro Strike](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)

## MESSAGE FROM CREATOR
>PLEASE NOTE AS IT STANDS THE UPDATE SYSTEM IS NOT FUNCTIONAL. PLEASE DISABLE AUTO UPDATE IN SETTINGS. THIS MIGHT AFFECT OTHER FEATUES AS WELL I FEAR
>
> ~ Jevaughani Lee

## ✨ Features

### ⏱️ Timer System
- **Customizable Pomodoro Sessions**: Adjustable focus time (default: 35 minutes)
- **Smart Break Management**: Short breaks (5 min) and long breaks (15 min)
- **Auto-start Options**: Automatically start next session or break
- **Session Tracking**: Visual indicators for completed sessions
- **Pause/Resume**: Full control over timer with pause functionality

### 📋 Task Management
- **Todo List Integration**: Built-in task management system
- **Task Categories**: Organize tasks by category with color coding
- **Priority Levels**: High, Medium, Low priority with visual indicators
- **Due Dates**: Set deadlines with overdue highlighting
- **Task Completion Tracking**: Monitor progress and completion rates

### 🎯 Productivity Features
- **Focus Streaks**: Track consecutive productive days
- **Daily Goals**: Set and monitor daily productivity targets
- **Achievement System**: Unlock achievements for milestones
- **Productivity Dashboard**: Comprehensive statistics and analytics
- **Best Hours Tracking**: Identify your most productive time slots
- **Session Completion Rates**: Monitor focus session success

### 🎨 User Interface
- **Dark Theme**: Modern, eye-friendly dark interface
- **Customizable Themes**: Multiple color themes available
- **Minimalist Mode**: Clean, distraction-free interface
- **Progress Ring**: Beautiful animated timer visualization
- **Responsive Design**: Adapts to window resizing
- **Always on Top**: Keep timer visible while working

### 🔔 Notifications & Reminders
- **System Notifications**: Desktop notifications for timer events
- **Sound Alerts**: Multiple sound options (bell, chime, etc.)
- **Water Reminders**: Hydration reminders during long sessions
- **System Tray**: Minimize to system tray with quick access
- **Motivational Quotes**: Inspirational quotes during breaks

### 📊 Analytics & Reporting
- **Daily Statistics**: Track focus time, sessions, and tasks
- **Weekly/Monthly Reports**: Long-term productivity insights
- **Data Export**: Export productivity data to CSV format
- **Productivity Score**: Calculated performance metrics
- **Progress Visualization**: Charts and progress bars

### ⚙️ Advanced Settings
- **Idle Detection**: Auto-pause when inactive
- **Transparency Control**: Adjust window opacity
- **Keyboard Shortcuts**: Quick access to common functions
- **Custom Break Intervals**: Flexible break scheduling
- **Appearance Modes**: Light/dark theme switching

### 🔄 Auto-Updates
- **Automatic Update Checks**: Daily background update checks
- **Seamless Updates**: One-click download and installation
- **Version Management**: Automatic version tracking
- **Release Notes**: View what's new in each update

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Windows operating system (for system tray functionality)

### Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pomodoro-strike-python.git
   cd pomodoro-strike-python
   ```

2. **Install dependencies**
   ```bash
   cd Python
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python pomodoro_strike.py
   ```

### Building Executable

#### Option 1: Using Build Script (Recommended)
1. **Run the build script**
   ```bash
   # On Windows
   build.bat
   
   # Or manually
   cd Python
   python build_exe.py
   ```

2. **Find the executable**
   - Location: `Python/dist/PomodoroStrike.exe`
   - Run directly or use the installer: `Python/install.bat`

#### Option 2: Manual PyInstaller
1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**
   ```bash
   cd Python
   pyinstaller --onefile --windowed --name PomodoroStrike pomodoro_strike.py
   ```

### Download Pre-built Executable
- **Latest Release**: Download from [GitHub Releases](https://github.com/yourusername/pomodoro-strike-python/releases)
- **Direct Download**: `PomodoroStrike.exe` - no installation required
- **Installer**: `install.bat` - installs to AppData with desktop shortcut

### Installation Methods

#### Method 1: Batch Installer (Simple)
```bash
# Run the batch installer
install.bat
```

#### Method 2: PowerShell Installer (Advanced)
```powershell
# Basic installation to C:\PomodoroStrike
.\install.ps1

# Install with startup (startup folder)
.\install.ps1 -AddToStartup -StartupFolder

# Install with registry startup
.\install.ps1 -AddToStartup -Registry

# Install with task scheduler startup
.\install.ps1 -AddToStartup -TaskScheduler

# Install to custom location
.\install.ps1 -InstallPath "D:\MyApps\PomodoroStrike" -AddToStartup
```

#### Method 3: Manual Installation
Follow the detailed steps below for manual installation.

### Installation to C Drive (Recommended)

#### Step 1: Create Application Folder
1. **Create a dedicated folder** for the application:
   ```bash
   # Create folder in C drive
   mkdir "C:\PomodoroStrike"
   
   # Or create in Program Files (requires admin)
   mkdir "C:\Program Files\PomodoroStrike"
   ```

2. **Copy the executable** to the folder:
   ```bash
   # Copy from build location
   copy "Python\dist\PomodoroStrike.exe" "C:\PomodoroStrike\"
   
   # Or if using installer
   copy "Python\install.bat" "C:\PomodoroStrike\"
   ```

#### Step 2: Create Desktop Shortcut
```bash
# Create desktop shortcut
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Pomodoro Strike.lnk'); $Shortcut.TargetPath = 'C:\PomodoroStrike\PomodoroStrike.exe'; $Shortcut.Save()"
```

#### Step 3: Add to Startup (Optional)
1. **Using Startup Folder** (Recommended):
   ```bash
   # Copy shortcut to startup folder
   copy "%USERPROFILE%\Desktop\Pomodoro Strike.lnk" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
   ```

2. **Using Registry** (Advanced):
   ```bash
   # Add to registry startup (run as administrator)
   reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "PomodoroStrike" /t REG_SZ /d "C:\PomodoroStrike\PomodoroStrike.exe" /f
   ```

3. **Using Task Scheduler** (Most Reliable):
   ```bash
   # Create scheduled task (run as administrator)
   schtasks /create /tn "PomodoroStrike" /tr "C:\PomodoroStrike\PomodoroStrike.exe" /sc onlogon /ru "%USERNAME%" /f
   ```

### Alternative Installation Locations

#### Option 1: AppData (Default)
- **Location**: `%APPDATA%\PomodoroStrike\`
- **Pros**: User-specific, no admin rights needed
- **Cons**: Hidden folder, harder to find

#### Option 2: Program Files
- **Location**: `C:\Program Files\PomodoroStrike\`
- **Pros**: Standard location, easy to find
- **Cons**: Requires admin rights for installation

#### Option 3: Custom Location
- **Location**: Any folder you prefer
- **Pros**: Full control over location
- **Cons**: Need to remember where you put it

### Startup Configuration

#### Automatic Startup Options
1. **Startup Folder**: Easiest method, user-specific
2. **Registry**: System-wide, requires admin
3. **Task Scheduler**: Most reliable, can set conditions
4. **Application Settings**: Built-in option in settings

#### Disable Startup
```bash
# Remove from startup folder
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Pomodoro Strike.lnk"

# Remove from registry
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "PomodoroStrike" /f

# Remove scheduled task
schtasks /delete /tn "PomodoroStrike" /f
```

## 📦 Dependencies

- **customtkinter** (5.2.0): Modern UI framework
- **pillow** (10.0.1): Image processing for icons and graphics
- **pystray** (0.19.4): System tray functionality
- **CTkToolTip** (0.8): Enhanced tooltips
- **requests** (2.31.0): HTTP requests for update system

## 🎮 Usage

### Basic Timer Operation
1. **Start a Focus Session**: Click the play button or press Space
2. **Pause/Resume**: Click pause button or press Space again
3. **Reset Timer**: Click reset to start over
4. **Switch Modes**: Use mode buttons for different session types

### Task Management
1. **Add Tasks**: Click the "+" button in the todo sidebar
2. **Set Priority**: Choose High, Medium, or Low priority
3. **Add Categories**: Organize tasks with custom categories
4. **Set Due Dates**: Add deadlines for time-sensitive tasks
5. **Mark Complete**: Check off completed tasks

### Productivity Tracking
1. **View Dashboard**: Access productivity statistics
2. **Set Goals**: Configure daily productivity targets
3. **Track Progress**: Monitor focus streaks and achievements
4. **Export Data**: Download productivity reports

### Update System
1. **Automatic Checks**: Updates are checked daily in the background
2. **Manual Check**: Check for updates through settings
3. **Download Updates**: One-click download and installation
4. **Version History**: View release notes and changelog

## ⚙️ Configuration

### Default Settings
- **Focus Time**: 35 minutes
- **Short Break**: 5 minutes
- **Long Break**: 15 minutes
- **Long Break Frequency**: Every 4 sessions
- **Water Reminders**: Every 60 minutes
- **Theme**: Blue (dark mode)
- **Auto-updates**: Enabled (daily checks)

### Customization
Access settings through the gear icon to customize:
- Timer durations
- Notification preferences
- Sound settings
- Appearance options
- Productivity goals
- Update preferences

## 🔄 Update System

### How Updates Work
1. **Background Checks**: Application checks for updates daily
2. **GitHub Integration**: Uses GitHub Releases API for version checking
3. **Automatic Download**: Downloads updates in the background
4. **Seamless Installation**: Installs updates and restarts automatically
5. **Backup System**: Creates backups before updating

### Update Process
1. **Version Check**: Compares current version with latest release
2. **Download**: Downloads new executable from GitHub Releases
3. **Backup**: Creates backup of current executable
4. **Install**: Replaces current executable with new version
5. **Restart**: Automatically restarts the application

### Manual Update Check
- Access settings and click "Check for Updates"
- View current version and latest available version
- Download and install updates manually if needed

## 🎯 Productivity Tips

- **Use the 4-session cycle** for optimal productivity
- **Take short breaks** to maintain high focus levels
- **Eliminate distractions** during focus sessions
- **Track your progress** to stay motivated
- **Adjust session length** based on your energy levels
- **Plan your tasks** before starting a session

## 🐛 Known Issues

This application is actively developed and may contain some bugs. Known issues include:
- Occasional UI lag during heavy system load
- System tray icon may not appear on some Windows configurations
- Sound notifications may not work on all audio systems
- Other bugs that may or may not have been discovered

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests to help improve the application.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Building for Development
1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Run the application**
   ```bash
   python pomodoro_strike.py
   ```

3. **Build executable**
   ```bash
   python build_exe.py
   ```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CustomTkinter** team for the excellent UI framework
- **Pomodoro Technique** creators for the productivity methodology
- **Open source community** for various libraries and tools

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the existing issues for solutions
- Review the configuration options

---

**Happy Productivity! 🚀** 