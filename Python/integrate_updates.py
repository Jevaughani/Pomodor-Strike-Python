#!/usr/bin/env python3
"""
Integration guide for adding update system to main application
This shows how to add update functionality to pomodoro_strike.py
"""

# Add these imports to pomodoro_strike.py
"""
import threading
import time
from update_system import UpdateSystem, check_for_updates_async
"""

# Add this to the PomodoroStrike.__init__ method
"""
def __init__(self):
    # ... existing initialization code ...
    
    # Initialize update system
    self.update_system = UpdateSystem()
    
    # Start update checker in background
    self.start_update_checker()
"""

# Add these methods to the PomodoroStrike class
"""
def start_update_checker(self):
    '''Start background update checker'''
    def update_checker():
        while True:
            try:
                # Check for updates every 24 hours
                time.sleep(24 * 60 * 60)  # 24 hours
                update_callback = check_for_updates_async()
                if update_callback:
                    # Schedule update dialog in main thread
                    self.after(0, update_callback)
            except Exception as e:
                print(f"Update checker error: {e}")
    
    # Start update checker in background thread
    update_thread = threading.Thread(target=update_checker, daemon=True)
    update_thread.start()

def check_for_updates_manual(self):
    '''Manual update check from settings'''
    try:
        update_info = self.update_system.check_for_updates(silent=False)
        if update_info:
            self.update_system.create_update_dialog(update_info)
        else:
            messagebox.showinfo("No Updates", "You are running the latest version!")
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to check for updates: {e}")

def show_version_info(self):
    '''Show current version information'''
    current_version = self.update_system.get_current_version()
    messagebox.showinfo(
        "Version Information", 
        f"Pomodoro Strike\nVersion: {current_version}\n\nCheck for updates in settings."
    )
"""

# Add this to the settings modal creation
"""
def create_settings_modal(self):
    # ... existing settings code ...
    
    # Add update section
    update_frame = ctk.CTkFrame(settings_window)
    update_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(update_frame, text="Updates", font=ctk.CTkFont(weight="bold")).pack(pady=5)
    
    # Version info
    version_info = ctk.CTkLabel(update_frame, text=f"Current Version: {self.update_system.get_current_version()}")
    version_info.pack(pady=5)
    
    # Check for updates button
    ctk.CTkButton(
        update_frame, 
        text="Check for Updates", 
        command=self.check_for_updates_manual
    ).pack(pady=5)
    
    # Auto-update toggle
    auto_update_var = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(
        update_frame, 
        text="Check for updates automatically", 
        variable=auto_update_var
    ).pack(pady=5)
"""

# Example of how to add update menu item to system tray
"""
def setup_system_tray(self):
    # ... existing system tray code ...
    
    # Add update menu item
    menu = (
        item('Show App', self.show_app),
        item('Check for Updates', self.check_for_updates_manual),
        item('Version Info', self.show_version_info),
        item('Quit', self.quit_app)
    )
"""

if __name__ == "__main__":
    print("Integration Guide for Update System")
    print("=" * 50)
    print("\nTo integrate the update system into pomodoro_strike.py:")
    print("\n1. Add the required imports")
    print("2. Initialize UpdateSystem in __init__")
    print("3. Add update checker methods")
    print("4. Add update UI elements to settings")
    print("5. Add update menu items to system tray")
    print("\nSee the comments above for specific code examples.") 