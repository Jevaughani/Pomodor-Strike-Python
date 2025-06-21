#!/usr/bin/env python3
"""
Update system for Pomodoro Strike
Handles checking for updates and downloading them
"""

import os
import sys
import json
import requests
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
import hashlib

class UpdateSystem:
    def __init__(self):
        self.current_version = "1.0.0"
        self.update_url = "https://api.github.com/repos/yourusername/pomodoro-strike-python/releases/latest"
        self.download_base_url = "https://github.com/yourusername/pomodoro-strike-python/releases/download"
        self.app_name = "PomodoroStrike"
        self.update_check_interval = 24 * 60 * 60  # 24 hours in seconds
        
        # Data directories
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), 'PomodoroStrike')
        self.update_info_file = os.path.join(self.app_data_dir, 'update_info.json')
        
        # Ensure app data directory exists
        os.makedirs(self.app_data_dir, exist_ok=True)
        
    def get_current_version(self):
        """Get the current version from version file or default"""
        version_file = os.path.join(self.app_data_dir, 'version.txt')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        return self.current_version
    
    def save_current_version(self, version):
        """Save the current version to file"""
        version_file = os.path.join(self.app_data_dir, 'version.txt')
        try:
            with open(version_file, 'w') as f:
                f.write(version)
        except Exception as e:
            print(f"Error saving version: {e}")
    
    def check_for_updates(self, silent=False):
        """Check for available updates"""
        try:
            # Load last check time
            last_check = self.load_update_info().get('last_check', 0)
            current_time = time.time()
            
            # Don't check too frequently
            if current_time - last_check < self.update_check_interval and not silent:
                return None
            
            # Check GitHub API for latest release
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')
            current_version = self.get_current_version()
            
            # Update last check time
            self.save_update_info({
                'last_check': current_time,
                'latest_version': latest_version,
                'current_version': current_version
            })
            
            if self.compare_versions(latest_version, current_version) > 0:
                return {
                    'version': latest_version,
                    'download_url': release_data['html_url'],
                    'release_notes': release_data.get('body', ''),
                    'published_at': release_data['published_at']
                }
            
            return None
            
        except Exception as e:
            if not silent:
                print(f"Error checking for updates: {e}")
            return None
    
    def compare_versions(self, version1, version2):
        """Compare two version strings. Returns 1 if version1 > version2, -1 if version1 < version2, 0 if equal"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad with zeros if needed
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for i in range(max_len):
            if v1_parts[i] > v2_parts[i]:
                return 1
            elif v1_parts[i] < v2_parts[i]:
                return -1
        
        return 0
    
    def download_update(self, update_info, progress_callback=None):
        """Download the update"""
        try:
            # Create temporary directory for download
            temp_dir = os.path.join(self.app_data_dir, 'temp_update')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Download the executable
            download_url = f"{self.download_base_url}/v{update_info['version']}/{self.app_name}.exe"
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            file_path = os.path.join(temp_dir, f"{self.app_name}.exe")
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            progress_callback(progress)
            
            return file_path
            
        except Exception as e:
            print(f"Error downloading update: {e}")
            return None
    
    def install_update(self, update_file_path):
        """Install the downloaded update"""
        try:
            # Create backup of current executable
            current_exe = sys.executable if getattr(sys, 'frozen', False) else None
            if current_exe and os.path.exists(current_exe):
                backup_path = current_exe + '.backup'
                import shutil
                shutil.copy2(current_exe, backup_path)
            
            # Replace current executable
            if current_exe:
                import shutil
                shutil.copy2(update_file_path, current_exe)
                
                # Clean up
                os.remove(update_file_path)
                os.rmdir(os.path.dirname(update_file_path))
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error installing update: {e}")
            return False
    
    def load_update_info(self):
        """Load update information from file"""
        try:
            if os.path.exists(self.update_info_file):
                with open(self.update_info_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading update info: {e}")
        return {}
    
    def save_update_info(self, info):
        """Save update information to file"""
        try:
            with open(self.update_info_file, 'w') as f:
                json.dump(info, f)
        except Exception as e:
            print(f"Error saving update info: {e}")
    
    def create_update_dialog(self, update_info):
        """Create a dialog to show update information and offer to download"""
        dialog = ctk.CTkToplevel()
        dialog.title("Update Available")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Make dialog modal
        dialog.transient()
        dialog.grab_set()
        
        # Title
        title_label = ctk.CTkLabel(
            dialog, 
            text="🎉 Update Available!", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Version info
        version_frame = ctk.CTkFrame(dialog)
        version_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(version_frame, text=f"Current Version: {self.get_current_version()}").pack(pady=5)
        ctk.CTkLabel(version_frame, text=f"New Version: {update_info['version']}").pack(pady=5)
        
        # Release notes
        notes_label = ctk.CTkLabel(dialog, text="Release Notes:", font=ctk.CTkFont(weight="bold"))
        notes_label.pack(pady=(20, 5))
        
        notes_text = ctk.CTkTextbox(dialog, height=150)
        notes_text.pack(fill="x", padx=20, pady=(0, 20))
        notes_text.insert("1.0", update_info.get('release_notes', 'No release notes available.'))
        notes_text.configure(state="disabled")
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def download_update():
            download_dialog = self.create_download_dialog(update_info, dialog)
        
        def skip_update():
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame, 
            text="Download Update", 
            command=download_update,
            fg_color="green"
        ).pack(side="left", padx=(0, 10), expand=True)
        
        ctk.CTkButton(
            button_frame, 
            text="Skip This Version", 
            command=skip_update
        ).pack(side="right", expand=True)
    
    def create_download_dialog(self, update_info, parent_dialog):
        """Create a dialog to show download progress"""
        dialog = ctk.CTkToplevel()
        dialog.title("Downloading Update")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        dialog.transient()
        dialog.grab_set()
        
        # Title
        title_label = ctk.CTkLabel(
            dialog, 
            text="📥 Downloading Update...", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Progress bar
        progress_bar = ctk.CTkProgressBar(dialog)
        progress_bar.pack(fill="x", padx=20, pady=10)
        progress_bar.set(0)
        
        # Status label
        status_label = ctk.CTkLabel(dialog, text="Preparing download...")
        status_label.pack(pady=10)
        
        def update_progress(progress):
            progress_bar.set(progress / 100)
            status_label.configure(text=f"Downloading... {progress:.1f}%")
            dialog.update()
        
        def download_complete():
            status_label.configure(text="Download complete! Installing...")
            dialog.update()
            
            # Install the update
            if self.install_update(downloaded_file):
                messagebox.showinfo(
                    "Update Complete", 
                    "Update installed successfully! The application will restart."
                )
                # Restart the application
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                messagebox.showerror(
                    "Update Failed", 
                    "Failed to install the update. Please try again."
                )
            
            dialog.destroy()
            parent_dialog.destroy()
        
        def download_failed():
            status_label.configure(text="Download failed!")
            messagebox.showerror(
                "Download Failed", 
                "Failed to download the update. Please check your internet connection and try again."
            )
            dialog.destroy()
        
        # Start download in a separate thread
        def download_thread():
            try:
                nonlocal downloaded_file
                downloaded_file = self.download_update(update_info, update_progress)
                if downloaded_file:
                    dialog.after(0, download_complete)
                else:
                    dialog.after(0, download_failed)
            except Exception as e:
                print(f"Download error: {e}")
                dialog.after(0, download_failed)
        
        downloaded_file = None
        threading.Thread(target=download_thread, daemon=True).start()

def check_for_updates_async():
    """Check for updates asynchronously (can be called from main app)"""
    update_system = UpdateSystem()
    update_info = update_system.check_for_updates(silent=True)
    
    if update_info:
        # Schedule the update dialog to show in the main thread
        def show_update_dialog():
            update_system.create_update_dialog(update_info)
        
        # This should be called from the main application thread
        return show_update_dialog
    
    return None

if __name__ == "__main__":
    # Test the update system
    update_system = UpdateSystem()
    print(f"Current version: {update_system.get_current_version()}")
    
    update_info = update_system.check_for_updates()
    if update_info:
        print(f"Update available: {update_info['version']}")
    else:
        print("No updates available") 