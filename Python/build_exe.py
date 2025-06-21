#!/usr/bin/env python3
"""
Build script for Pomodoro Strike executable
Uses PyInstaller to create a standalone executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Cleaned {dir_name}")

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pomodoro_strike.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('settings.json', '.'),
        ('todos.json', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'pystray',
        'CTkToolTip',
        'tkinter',
        'json',
        'threading',
        'time',
        'datetime',
        'winsound',
        'platform',
        'math',
        'random',
        'csv',
        'collections',
        'sys',
        'os'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PomodoroStrike',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('pomodoro_strike.spec', 'w') as f:
        f.write(spec_content)
    print("✓ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # Use the spec file for building
    result = subprocess.run([
        'pyinstaller',
        '--clean',
        'pomodoro_strike.spec'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Executable built successfully!")
        print(f"📁 Executable location: {os.path.abspath('dist/PomodoroStrike.exe')}")
    else:
        print("✗ Build failed!")
        print("Error output:")
        print(result.stderr)
        return False
    
    return True

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo Installing Pomodoro Strike...
echo.

REM Create installation directory
if not exist "%APPDATA%\\PomodoroStrike" mkdir "%APPDATA%\\PomodoroStrike"

REM Copy executable
copy "dist\\PomodoroStrike.exe" "%APPDATA%\\PomodoroStrike\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Pomodoro Strike.lnk'); $Shortcut.TargetPath = '%APPDATA%\\PomodoroStrike\\PomodoroStrike.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo Pomodoro Strike has been installed to: %APPDATA%\\PomodoroStrike
echo A desktop shortcut has been created.
echo.
pause
'''
    
    with open('install.bat', 'w') as f:
        f.write(installer_content)
    print("✓ Created installer script")

def main():
    """Main build process"""
    print("🚀 Starting Pomodoro Strike build process...")
    print("=" * 50)
    
    # Check and install dependencies
    check_dependencies()
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        # Create installer
        create_installer_script()
        
        print("\n" + "=" * 50)
        print("🎉 Build completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the executable: dist/PomodoroStrike.exe")
        print("2. Run install.bat to install the application")
        print("3. Distribute the executable or installer")
    else:
        print("\n❌ Build failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 