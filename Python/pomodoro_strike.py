# Author: Jevaughani Lee

import customtkinter as ctk
import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import messagebox
import winsound
import platform
from PIL import Image, ImageTk, ImageDraw
import pystray
from pystray import MenuItem as item
import math
import random
import csv
from collections import defaultdict
from CTkToolTip import *
import sys

def get_data_path(file_name: str) -> str:
    """Get path to data file, works for script and frozen exe."""
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        datadir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(datadir, file_name)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Motivational quotes
MOTIVATIONAL_QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Focus is not about saying yes to the things you've got to focus on, but about saying no to the hundred other good ideas. - Steve Jobs",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "The future depends on what you do today. - Mahatma Gandhi",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
    "It always seems impossible until it's done. - Nelson Mandela",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Success usually comes to those who are too busy to be looking for it. - Henry David Thoreau",
    "The only person you are destined to become is the person you decide to be. - Ralph Waldo Emerson"
]

# Pomodoro technique tips
POMODORO_TIPS = [
    "Take short breaks to maintain high focus levels",
    "Use the 4-session cycle for optimal productivity",
    "Eliminate distractions during focus sessions",
    "Track your progress to stay motivated",
    "Adjust session length based on your energy levels",
    "Use the long break to step away from your work",
    "Plan your tasks before starting a session",
    "Review your completed sessions regularly"
]

class ProductivityData:
    def __init__(self):
        self.focus_streak = 0
        self.longest_streak = 0
        self.daily_goals = {
            "focus_sessions": 8,
            "focus_time": 240,  # minutes
            "tasks_completed": 5
        }
        self.achievements = []
        self.daily_stats = defaultdict(lambda: {
            "focus_sessions": 0,
            "focus_time": 0,
            "tasks_completed": 0,
            "productivity_score": 0.0
        })
        self.weekly_stats = defaultdict(lambda: {
            "focus_sessions": 0,
            "focus_time": 0,
            "tasks_completed": 0,
            "productivity_score": 0.0
        })
        self.monthly_stats = defaultdict(lambda: {
            "focus_sessions": 0,
            "focus_time": 0,
            "tasks_completed": 0,
            "productivity_score": 0.0
        })
        self.best_hours = defaultdict(int)
        self.session_completion_rates = []
        
    def update_focus_streak(self, completed_session: bool):
        """Update focus streak based on session completion"""
        if completed_session:
            self.focus_streak += 1
            if self.focus_streak > self.longest_streak:
                self.longest_streak = self.focus_streak
        else:
            self.focus_streak = 0
            
    def calculate_productivity_score(self, focus_time: int, tasks_completed: int, sessions_completed: int) -> float:
        """Calculate productivity score (0-100)"""
        # Base score from focus time (40% weight)
        time_score = min(40, (focus_time / 240) * 40)  # 240 minutes = 4 hours target
        
        # Task completion score (30% weight)
        task_score = min(30, (tasks_completed / 5) * 30)  # 5 tasks target
        
        # Session completion score (30% weight)
        session_score = min(30, (sessions_completed / 8) * 30)  # 8 sessions target
        
        return time_score + task_score + session_score
        
    def update_daily_stats(self, focus_time: int, tasks_completed: int = 0):
        """Update daily statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_stats[today]["focus_time"] += focus_time
        self.daily_stats[today]["focus_sessions"] += 1
        self.daily_stats[today]["tasks_completed"] += tasks_completed
        
        # Calculate productivity score
        self.daily_stats[today]["productivity_score"] = float(self.calculate_productivity_score(
            int(self.daily_stats[today]["focus_time"]),
            int(self.daily_stats[today]["tasks_completed"]),
            int(self.daily_stats[today]["focus_sessions"])
        ))
        
        # Update weekly and monthly stats
        week_key = datetime.now().strftime("%Y-W%U")
        month_key = datetime.now().strftime("%Y-%m")
        
        self.weekly_stats[week_key]["focus_time"] += focus_time
        self.weekly_stats[week_key]["focus_sessions"] += 1
        self.weekly_stats[week_key]["tasks_completed"] += tasks_completed
        
        self.monthly_stats[month_key]["focus_time"] += focus_time
        self.monthly_stats[month_key]["focus_sessions"] += 1
        self.monthly_stats[month_key]["tasks_completed"] += tasks_completed
        
        # Update best hours
        current_hour = datetime.now().hour
        self.best_hours[current_hour] += 1
        
    def check_achievements(self):
        """Check and award achievements"""
        new_achievements = []
        
        # Focus streak achievements
        if self.focus_streak >= 5 and "5 Day Streak" not in self.achievements:
            new_achievements.append("5 Day Streak")
        if self.focus_streak >= 10 and "10 Day Streak" not in self.achievements:
            new_achievements.append("10 Day Streak")
        if self.focus_streak >= 30 and "30 Day Streak" not in self.achievements:
            new_achievements.append("30 Day Streak")
            
        # Daily goal achievements
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.daily_stats:
            stats = self.daily_stats[today]
            if stats["focus_time"] >= 240 and "4 Hour Focus" not in self.achievements:
                new_achievements.append("4 Hour Focus")
            if stats["tasks_completed"] >= 10 and "Task Master" not in self.achievements:
                new_achievements.append("Task Master")
                
        self.achievements.extend(new_achievements)
        return new_achievements

class ProgressRing(ctk.CTkFrame):
    def __init__(self, master, size=300, **kwargs):
        super().__init__(master, **kwargs)
        self.size = size
        self.progress = 0.0  # 0.0 to 1.0
        self.ring_width = 15
        self.animation_step = 0
        self.glow_color = "#3498db"  # Default to focus blue
        
        # Create canvas for the ring
        self.canvas = tk.Canvas(
            self, 
            width=size, 
            height=size, 
            bg=self._apply_appearance_mode(self.cget("fg_color")),
            highlightthickness=0
        )
        self.canvas.pack(expand=True)
        
        # Calculate ring parameters
        self.center = size // 2
        self.radius = (size - self.ring_width * 2) // 2
        
        # Draw initial ring
        self.draw_ring()
        self.animate_glow()
        
    def draw_ring(self):
        """Draw the progress ring"""
        self.canvas.delete("all")
        
        # Pulsating glow effect
        self.draw_pulsating_glow()
        
        # Background ring
        self.canvas.create_arc(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            start=0,
            extent=360,
            width=self.ring_width,
            outline=self._apply_appearance_mode(("gray70", "gray30")),
            style="arc"
        )
        
        # Progress ring
        if self.progress > 0:
            extent = self.progress * 360
            self.canvas.create_arc(
                self.center - self.radius,
                self.center - self.radius,
                self.center + self.radius,
                self.center + self.radius,
                start=90,  # Start from top
                extent=-extent,
                width=self.ring_width,
                outline=self.glow_color,
                style="arc"
            )
            
    def draw_pulsating_glow(self):
        """Draw a pulsating glow effect"""
        pulse_factor = (math.sin(math.radians(self.animation_step)) + 1) / 2  # Varies between 0 and 1
        num_layers = 15
        
        for i in range(num_layers):
            radius = self.radius + (i * 2) * pulse_factor
            alpha = 1 - (i / num_layers)
            
            # Create a transparent color for the glow
            glow_color = self.interpolate_color(self._apply_appearance_mode(self._fg_color), self.glow_color, 0.1 * alpha)
            
            self.canvas.create_oval(
                self.center - radius,
                self.center - radius,
                self.center + radius,
                self.center + radius,
                outline=glow_color,
                width=2
            )

    def animate_glow(self):
        """Animate the glow effect"""
        self.animation_step += 2
        self.draw_ring()
        self.after(50, self.animate_glow)
        
    def set_color(self, color):
        """Set the color of the progress ring and glow"""
        self.glow_color = color
        self.draw_ring()
        
    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two hex colors"""
        c1 = self.winfo_rgb(color1)
        c2 = self.winfo_rgb(color2)
        
        r = int(c1[0] + (c2[0] - c1[0]) * factor)
        g = int(c1[1] + (c2[1] - c1[1]) * factor)
        b = int(c1[2] + (c2[2] - c1[2]) * factor)
        
        return f"#{r//256:02x}{g//256:02x}{b//256:02x}"
            
    def set_progress(self, progress):
        """Set progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        self.draw_ring()
        
    def _apply_appearance_mode(self, color_tuple):
        """Apply appearance mode to colors"""
        if ctk.get_appearance_mode() == "dark":
            return color_tuple[1] if len(color_tuple) > 1 else color_tuple[0]
        else:
            return color_tuple[0]

class TodoItem:
    def __init__(self, text: str, completed: bool = False, created_at: Optional[str] = None, 
                 category: str = "General", priority: str = "Medium", due_date: Optional[str] = None):
        self.id = int(time.time() * 1000)
        self.text = text
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()
        self.category = category
        self.priority = priority
        self.due_date = due_date
        self.estimated_time = 0  # in minutes
        self.actual_time = 0     # in minutes

class PomodoroStrike(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Pomodoro Strike - Focus Timer")
        self.state('zoomed')  # Start maximized/fullscreen
        self.minsize(1200, 800)
        
        # Set app icon
        try:
            width, height = 64, 64
            icon_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_image)
            
            bolt_color = (255, 204, 0, 255) # Yellow
            points = [
                (width*0.5, height*0.1), (width*0.3, height*0.5), 
                (width*0.45, height*0.5), (width*0.35, height*0.9), 
                (width*0.7, height*0.4), (width*0.55, height*0.4),
                (width*0.5, height*0.1)
            ]
            draw.polygon(points, fill=bolt_color)
            
            app_icon = ImageTk.PhotoImage(icon_image)
            self.iconphoto(True, app_icon)
        except Exception as e:
            print(f"Failed to set app icon: {e}")
        
        # Initialize state
        self.mode = "pomodoro"
        self.is_running = False
        self.is_paused = False
        self.time_left = 25 * 60  # 25 minutes in seconds
        self.total_time = 25 * 60
        self.sessions = 0
        self.total_focus_time = 0
        self.timer_thread = None
        self.stop_timer = False
        
        # UI state
        self.is_fullscreen = True
        self.is_minimalist = False
        self.current_theme = "blue"
        self.always_on_top = False
        self.window_transparency = 1.0
        
        # Productivity data
        self.productivity_data = ProductivityData()
        
        # Settings
        self.settings = {
            "pomodoro_time": 25,
            "short_break_time": 5,
            "long_break_time": 15,
            "auto_start": False,
            "notifications": True,
            "sound": "bell",
            "system_tray": True,
            "water_reminders": True,
            "water_interval": 60,  # minutes
            "theme": "blue",
            "appearance_mode": "dark",
            "minimalist_mode": False,
            "always_on_top": False,
            "window_transparency": 1.0,
            "custom_break_interval": 4,  # every X sessions
            "long_break_frequency": 4,   # every 4, 6, 8 sessions
            "auto_pause_idle": False,
            "idle_threshold": 300,  # 5 minutes
            "show_motivational_quotes": True,
            "show_pomodoro_tips": True
        }
        
        # Todo list
        self.todos: List[TodoItem] = []
        
        # Categories and priorities
        self.categories = ["General", "Work", "Study", "Personal", "Health", "Finance"]
        self.priorities = ["Low", "Medium", "High", "Urgent"]
        
        # System tray
        self.system_tray = None
        self.last_water_reminder = datetime.now()
        self.last_activity = datetime.now()
        
        # Load data
        self.load_settings()
        self.load_todos()
        self.load_total_focus_time()
        self.load_productivity_data()
        
        # Apply theme
        self.apply_theme()
        
        # Create UI
        self.create_widgets()
        
        # Update UI after creation
        self.update_display()
        self.update_session_dots()
        self.update_sidebar_stats()
        
        # Bind keyboard shortcuts
        self.bind("<Key>", self.handle_keyboard_shortcuts)
        
        # Setup system tray
        if self.settings["system_tray"]:
            self.setup_system_tray()
            
        # Bind window events
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind resize events
        self.bind("<Configure>", self.on_resize)
        
        # Bind mouse and keyboard events for idle detection
        self.bind("<Button-1>", self.update_activity)
        self.bind("<Key>", self.update_activity)
        
        # Start idle monitoring
        if self.settings["auto_pause_idle"]:
            self.start_idle_monitoring()
            
        # Show motivational quote
        if self.settings["show_motivational_quotes"]:
            self.show_motivational_quote()
        
        # Initial UI update
        self.update_total_time_display()
        
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        try:
            # Create a more representative icon with a transparent background
            width, height = 64, 64
            icon_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_image)
            
            # Define lightning bolt shape
            bolt_color = (255, 204, 0, 255) # Yellow
            points = [
                (width*0.5, height*0.1), (width*0.3, height*0.5), 
                (width*0.45, height*0.5), (width*0.35, height*0.9), 
                (width*0.7, height*0.4), (width*0.55, height*0.4),
                (width*0.5, height*0.1)
            ]
            draw.polygon(points, fill=bolt_color)

            menu = pystray.Menu(
                item('Show App', self.show_app),
                item('Start Timer', self.start_timer),
                item('Pause Timer', self.pause_timer),
                pystray.Menu.SEPARATOR,
                item('Quit', self.quit_app)
            )
            
            self.system_tray = pystray.Icon("Pomodoro Strike", icon_image, "Pomodoro Strike", menu)
            
            # Start system tray in a separate thread
            threading.Thread(target=self.system_tray.run, daemon=True).start()
            
        except Exception as e:
            print(f"System tray setup failed: {e}")
            
    def show_app(self, icon=None, item=None):
        """Show the main window"""
        self.deiconify()
        self.lift()
        self.focus_force()
        
    def hide_app(self):
        """Hide the main window to system tray"""
        if self.system_tray:
            self.withdraw()
            
    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        self.stop_timer = True # ensure timer thread exits
        if self.system_tray:
            self.system_tray.stop()
        self.destroy() # use destroy instead of quit
        
    def on_closing(self):
        """Handle window closing"""
        if self.settings["system_tray"] and self.system_tray:
            self.hide_app()
        else:
            self.quit_app()
        
    def create_widgets(self):
        # Configure grid for full window
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content_area()
        
        # Settings modal
        self.create_settings_modal()
        
    def create_sidebar(self):
        """Create a modern sidebar with navigation and controls"""
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)

        # App branding
        self.branding_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.branding_frame.pack(fill="x", padx=20, pady=(20, 30))

        ctk.CTkLabel(
            self.branding_frame,
            text="⚡",
            font=ctk.CTkFont(size=32)
        ).pack()

        ctk.CTkLabel(
            self.branding_frame,
            text="Pomodoro Strike",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack()

        ctk.CTkLabel(
            self.branding_frame,
            text="Focus Timer & Task Manager",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            self.branding_frame,
            text="by Jevaughani Lee",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(pady=(5,0))

        # Quick stats
        self.stats_frame = ctk.CTkFrame(self.sidebar)
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.stats_frame,
            text="📊 Today's Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))

        # Focus time today
        focus_frame = ctk.CTkFrame(self.stats_frame)
        focus_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(focus_frame, text="Focus Time", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.sidebar_focus_time = ctk.CTkLabel(
            focus_frame,
            text="00:00",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.sidebar_focus_time.pack(anchor="w", padx=10, pady=(0, 5))

        # Sessions completed
        sessions_frame = ctk.CTkFrame(self.stats_frame)
        sessions_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(sessions_frame, text="Sessions", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.sidebar_sessions = ctk.CTkLabel(
            sessions_frame,
            text="0",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.sidebar_sessions.pack(anchor="w", padx=10, pady=(0, 5))

        # Tasks completed
        tasks_frame = ctk.CTkFrame(self.stats_frame)
        tasks_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(tasks_frame, text="Tasks Done", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.sidebar_tasks = ctk.CTkLabel(
            tasks_frame,
            text="0",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.sidebar_tasks.pack(anchor="w", padx=10, pady=(0, 5))

        # Navigation buttons
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.nav_frame,
            text="Navigation",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        # Dashboard button
        self.dashboard_nav_btn = ctk.CTkButton(
            self.nav_frame,
            text="📊 Dashboard",
            command=self.show_productivity_dashboard,
            height=40,
            anchor="w"
        )
        self.dashboard_nav_btn.pack(fill="x", pady=2)
        
        # Tasks button
        self.tasks_nav_btn = ctk.CTkButton(
            self.nav_frame,
            text="📋 Tasks",
            command=self.toggle_todo_sidebar,
            height=40,
            anchor="w"
        )
        self.tasks_nav_btn.pack(fill="x", pady=2)
        
        # Settings button
        self.settings_nav_btn = ctk.CTkButton(
            self.nav_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            height=40,
            anchor="w"
        )
        self.settings_nav_btn.pack(fill="x", pady=2)
        
        # Bottom section - current streak
        self.streak_frame = ctk.CTkFrame(self.sidebar)
        self.streak_frame.pack(fill="x", padx=20, pady=(0, 20), side="bottom")
        
        ctk.CTkLabel(
            self.streak_frame,
            text="🔥 Focus Streak",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        self.streak_label = ctk.CTkLabel(
            self.streak_frame,
            text=f"{self.productivity_data.focus_streak} days",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FF6B6B"
        )
        self.streak_label.pack(pady=(0, 15))
        
    def create_main_content_area(self):
        """Create the main content area with timer and controls"""
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Configure main content grid
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Top section - Mode selector and session info
        self.create_top_section()
        
        # Center section - Timer with progress ring
        self.create_timer_section()
        
        # Bottom section - Controls and session dots
        self.create_bottom_section()
        
    def create_top_section(self):
        """Create the top section with mode selector and session info"""
        top_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_frame.grid_columnconfigure(1, weight=1)

        # Mode selector
        mode_frame = ctk.CTkFrame(top_frame)
        mode_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Mode buttons
        self.focus_btn = ctk.CTkButton(
            mode_frame,
            text="🧠 Focus",
            command=lambda: self.switch_mode("pomodoro"),
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.focus_btn.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.short_break_btn = ctk.CTkButton(
            mode_frame,
            text="☕ Short Break",
            command=lambda: self.switch_mode("short_break"),
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.short_break_btn.pack(side="left", fill="x", expand=True, padx=5, pady=10)

        self.long_break_btn = ctk.CTkButton(
            mode_frame,
            text="🛏️ Long Break",
            command=lambda: self.switch_mode("long_break"),
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.long_break_btn.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=10)

        # Quick Controls Frame
        controls_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=2, sticky="e")

        # Theme toggle
        self.theme_btn = ctk.CTkButton(
            controls_frame,
            text="🌙" if self.settings["appearance_mode"] == "dark" else "☀️",
            width=50,
            command=self.toggle_appearance_mode
        )
        self.theme_btn.pack(side="left", padx=(0, 5))
        CTkToolTip(self.theme_btn, message="Toggle Dark/Light Mode")

        # Fullscreen toggle
        self.fullscreen_btn = ctk.CTkButton(
            controls_frame,
            text="⛶",
            width=50,
            command=self.toggle_fullscreen
        )
        self.fullscreen_btn.pack(side="left", padx=5)
        CTkToolTip(self.fullscreen_btn, message="Toggle Fullscreen")

        # Minimalist mode
        self.minimalist_btn = ctk.CTkButton(
            controls_frame,
            text="🎯",
            width=50,
            command=self.toggle_minimalist_mode
        )
        self.minimalist_btn.pack(side="left", padx=(5, 0))
        CTkToolTip(self.minimalist_btn, message="Toggle Minimalist Mode")
        
    def create_timer_section(self):
        """Create the center timer section with progress ring"""
        timer_frame = ctk.CTkFrame(self.main_content)
        timer_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        
        # Configure timer frame grid
        timer_frame.grid_columnconfigure(0, weight=1)
        timer_frame.grid_rowconfigure(0, weight=1)
        
        # Timer container
        timer_container = ctk.CTkFrame(timer_frame, fg_color="transparent")
        timer_container.grid(row=0, column=0, sticky="nsew")
        
        # Progress ring with larger size
        self.progress_ring = ProgressRing(timer_container, size=400)
        self.progress_ring.pack(expand=True)
        
        # Time display overlay
        time_frame = ctk.CTkFrame(timer_container, fg_color="transparent")
        time_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.time_display = ctk.CTkLabel(
            time_frame,
            text="25:00",
            font=ctk.CTkFont(size=96, weight="bold")
        )
        self.time_display.pack()
        
        # Mode label
        self.mode_label = ctk.CTkLabel(
            time_frame,
            text="Focus Time",
            font=ctk.CTkFont(size=24),
            text_color="gray"
        )
        self.mode_label.pack(pady=(10, 0))
        
    def create_bottom_section(self):
        """Create the bottom section with controls and stats"""
        bottom_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        # Controls
        controls_frame = ctk.CTkFrame(bottom_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        controls_frame.grid_columnconfigure(2, weight=1)

        # Control buttons
        self.start_btn = ctk.CTkButton(
            controls_frame,
            text="▶️ Start",
            command=self.start_timer,
            height=55,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(15, 5), pady=15)

        self.pause_btn = ctk.CTkButton(
            controls_frame,
            text="⏸️ Pause",
            command=self.pause_timer,
            height=55,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.pause_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=15)
        self.pause_btn.configure(state="disabled")

        self.reset_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Reset",
            command=self.reset_timer,
            height=55,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.reset_btn.grid(row=0, column=2, sticky="ew", padx=(5, 15), pady=15)

        # Session info
        session_frame = ctk.CTkFrame(bottom_frame)
        session_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        ctk.CTkLabel(
            session_frame,
            text="Session Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        # Session dots
        dots_frame = ctk.CTkFrame(session_frame, fg_color="transparent")
        dots_frame.pack(pady=(0, 10))
        
        self.session_dots = []
        for i in range(4):
            dot = ctk.CTkLabel(dots_frame, text="○", font=ctk.CTkFont(size=20))
            dot.pack(side="left", padx=5)
            self.session_dots.append(dot)
            
    def update_session_dots(self):
        for i, dot in enumerate(self.session_dots):
            if i < self.sessions % 4:
                dot.configure(text="●", text_color="green")
            else:
                dot.configure(text="○", text_color="gray")
                
    def create_settings_modal(self):
        self.settings_window = None
        
    def open_settings(self):
        if self.settings_window is not None:
            self.settings_window.focus()
            return
            
        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.geometry("550x800")
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self)
        self.settings_window.grab_set()
        
        # Settings content
        content_frame = ctk.CTkScrollableFrame(self.settings_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Timer Settings
        ctk.CTkLabel(
            content_frame, 
            text="Timer Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Focus time
        ctk.CTkLabel(content_frame, text="Focus Time (minutes)", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.pomodoro_time_entry = ctk.CTkEntry(content_frame)
        self.pomodoro_time_entry.pack(fill="x", pady=(0, 15))
        self.pomodoro_time_entry.insert(0, str(self.settings["pomodoro_time"]))
        
        # Short break time
        ctk.CTkLabel(content_frame, text="Short Break (minutes)", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.short_break_entry = ctk.CTkEntry(content_frame)
        self.short_break_entry.pack(fill="x", pady=(0, 15))
        self.short_break_entry.insert(0, str(self.settings["short_break_time"]))
        
        # Long break time
        ctk.CTkLabel(content_frame, text="Long Break (minutes)", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.long_break_entry = ctk.CTkEntry(content_frame)
        self.long_break_entry.pack(fill="x", pady=(0, 20))
        self.long_break_entry.insert(0, str(self.settings["long_break_time"]))
        
        # Advanced Timer Settings
        ctk.CTkLabel(
            content_frame, 
            text="Advanced Timer Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Custom break interval
        ctk.CTkLabel(content_frame, text="Custom Break Interval (every X sessions)", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.custom_break_interval_entry = ctk.CTkEntry(content_frame)
        self.custom_break_interval_entry.pack(fill="x", pady=(0, 15))
        self.custom_break_interval_entry.insert(0, str(self.settings["custom_break_interval"]))
        
        # Long break frequency
        ctk.CTkLabel(content_frame, text="Long Break Frequency (every X sessions)", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.long_break_frequency_entry = ctk.CTkEntry(content_frame)
        self.long_break_frequency_entry.pack(fill="x", pady=(0, 20))
        self.long_break_frequency_entry.insert(0, str(self.settings["long_break_frequency"]))
        
        # Appearance Settings
        ctk.CTkLabel(
            content_frame, 
            text="Appearance Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Notification Settings
        ctk.CTkLabel(
            content_frame, 
            text="Notification Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Auto-start breaks
        self.auto_start_var = ctk.BooleanVar(value=self.settings["auto_start"])
        auto_start_checkbox = ctk.CTkCheckBox(
            content_frame, 
            text="Auto-start breaks",
            variable=self.auto_start_var
        )
        auto_start_checkbox.pack(anchor="w", pady=(0, 15))
        
        # Notifications
        self.notifications_var = ctk.BooleanVar(value=self.settings["notifications"])
        notifications_checkbox = ctk.CTkCheckBox(
            content_frame, 
            text="Enable notifications",
            variable=self.notifications_var
        )
        notifications_checkbox.pack(anchor="w", pady=(0, 15))
        
        # System tray
        self.system_tray_var = ctk.BooleanVar(value=self.settings["system_tray"])
        system_tray_checkbox = ctk.CTkCheckBox(
            content_frame, 
            text="Minimize to system tray",
            variable=self.system_tray_var
        )
        system_tray_checkbox.pack(anchor="w", pady=(0, 15))
        
        # Water reminders
        self.water_reminders_var = ctk.BooleanVar(value=self.settings["water_reminders"])
        water_reminders_checkbox = ctk.CTkCheckBox(
            content_frame, 
            text="Water break reminders",
            variable=self.water_reminders_var
        )
        water_reminders_checkbox.pack(anchor="w", pady=(0, 5))
        
        # Water interval
        ctk.CTkLabel(content_frame, text="Water reminder interval (minutes)", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 5))
        self.water_interval_entry = ctk.CTkEntry(content_frame)
        self.water_interval_entry.pack(fill="x", pady=(0, 20))
        self.water_interval_entry.insert(0, str(self.settings["water_interval"]))
        
        # Sound Settings
        ctk.CTkLabel(
            content_frame, 
            text="Sound Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Sound
        ctk.CTkLabel(content_frame, text="Sound alerts", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.sound_var = ctk.StringVar(value=self.settings["sound"])
        sound_menu = ctk.CTkOptionMenu(
            content_frame,
            values=["bell", "chime", "digital", "none"],
            variable=self.sound_var
        )
        sound_menu.pack(fill="x", pady=(0, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(content_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.close_settings
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=self.save_settings
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Handle window close
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings)
        
    def close_settings(self):
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
            
    def save_settings(self):
        try:
            self.settings["pomodoro_time"] = int(self.pomodoro_time_entry.get())
            self.settings["short_break_time"] = int(self.short_break_entry.get())
            self.settings["long_break_time"] = int(self.long_break_entry.get())
            self.settings["custom_break_interval"] = int(self.custom_break_interval_entry.get())
            self.settings["long_break_frequency"] = int(self.long_break_frequency_entry.get())
            self.settings["auto_start"] = self.auto_start_var.get()
            self.settings["notifications"] = self.notifications_var.get()
            self.settings["system_tray"] = self.system_tray_var.get()
            self.settings["water_reminders"] = self.water_reminders_var.get()
            self.settings["water_interval"] = int(self.water_interval_entry.get())
            self.settings["sound"] = self.sound_var.get()
            
            self.save_settings_to_file()
            
            # Apply theme changes
            self.apply_theme()
            
            self.reset_timer()
            
            # Update system tray if setting changed
            if self.settings["system_tray"] and not self.system_tray:
                self.setup_system_tray()
            elif not self.settings["system_tray"] and self.system_tray:
                if self.system_tray:
                    self.system_tray.stop()
                self.system_tray = None
                
            self.close_settings()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for time settings.")
            
    def switch_mode(self, mode):
        if self.is_running:
            return
            
        self.mode = mode
        
        # Update time and color based on mode
        if mode == "pomodoro":
            self.time_left = self.settings["pomodoro_time"] * 60
            self.total_time = self.settings["pomodoro_time"] * 60
            self.mode_label.configure(text="Focus Time")
            if hasattr(self, 'progress_ring'):
                self.progress_ring.set_color("#3498db")  # Blue for focus
        elif mode == "short_break":
            self.time_left = self.settings["short_break_time"] * 60
            self.total_time = self.settings["short_break_time"] * 60
            self.mode_label.configure(text="Short Break")
            if hasattr(self, 'progress_ring'):
                self.progress_ring.set_color("#2ecc71")  # Green for short break
        elif mode == "long_break":
            self.time_left = self.settings["long_break_time"] * 60
            self.total_time = self.settings["long_break_time"] * 60
            self.mode_label.configure(text="Long Break")
            if hasattr(self, 'progress_ring'):
                self.progress_ring.set_color("#9b59b6")  # Purple for long break
            
        # Update button states
        self.update_mode_buttons()
        self.update_display()
        
    def update_mode_buttons(self):
        # Reset all buttons
        self.focus_btn.configure(fg_color=("gray75", "gray25"))
        self.short_break_btn.configure(fg_color=("gray75", "gray25"))
        self.long_break_btn.configure(fg_color=("gray75", "gray25"))
        
        # Highlight active button
        if self.mode == "pomodoro":
            self.focus_btn.configure(fg_color=("gray65", "gray35"))
        elif self.mode == "short_break":
            self.short_break_btn.configure(fg_color=("gray65", "gray35"))
        elif self.mode == "long_break":
            self.long_break_btn.configure(fg_color=("gray65", "gray35"))
            
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.stop_timer = False
            
            self.start_btn.configure(state="disabled")
            self.pause_btn.configure(state="normal")
            
            self.timer_thread = threading.Thread(target=self.timer_loop)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
    def pause_timer(self):
        if self.is_running:
            self.is_paused = not self.is_paused
            
            if self.is_paused:
                self.pause_btn.configure(text="▶️ Resume")
            else:
                self.pause_btn.configure(text="⏸️ Pause")
                
    def reset_timer(self):
        self.stop_timer = True
        if self.timer_thread:
            self.timer_thread.join(timeout=0.2)
        self.is_running = False
        self.is_paused = False
        
        # Reset time to total time
        if self.mode == "pomodoro":
            self.time_left = self.settings["pomodoro_time"] * 60
        elif self.mode == "short_break":
            self.time_left = self.settings["short_break_time"] * 60
        elif self.mode == "long_break":
            self.time_left = self.settings["long_break_time"] * 60

        self.total_time = self.time_left
        
        # Reset buttons
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸️ Pause")
        
        self.update_display()
        
    def timer_loop(self):
        while self.time_left > 0 and not self.stop_timer:
            if not self.is_paused:
                time.sleep(1)
                self.time_left -= 1
                
                # Update display in main thread
                self.after(0, self.update_display)
                
        if not self.stop_timer:
            self.after(0, self.handle_timer_complete)
            
    def handle_timer_complete(self):
        self.is_running = False
        self.stop_timer = True
        
        # Reset buttons
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸️ Pause")
        
        # Play sound
        self.play_sound()
        
        # Show notification
        self.show_notification()
        
        # Check water reminder
        self.check_water_reminder()
        
        # Update session count for pomodoro sessions
        if self.mode == "pomodoro":
            self.sessions += 1
            self.total_focus_time += self.settings["pomodoro_time"]
            self.save_total_focus_time()
            self.update_session_dots()
            self.update_total_time_display()
            
            # Update productivity data
            self.productivity_data.update_daily_stats(self.settings["pomodoro_time"])
            self.productivity_data.update_focus_streak(True)
            
            # Check for achievements
            new_achievements = self.productivity_data.check_achievements()
            if new_achievements:
                achievement_text = "\n".join([f"🏆 {achievement}" for achievement in new_achievements])
                messagebox.showinfo("Achievement Unlocked!", f"Congratulations!\n\n{achievement_text}")
                
            # Save productivity data
            self.save_productivity_data()
            
        # Auto-start next session if enabled
        if self.settings["auto_start"]:
            if self.mode == "pomodoro":
                # Check custom break interval
                if self.sessions % self.settings["custom_break_interval"] == 0:
                    if self.sessions % self.settings["long_break_frequency"] == 0:
                        self.switch_mode("long_break")
                    else:
                        self.switch_mode("short_break")
                else:
                    self.switch_mode("short_break")
            else:
                self.switch_mode("pomodoro")
                
        self.update_display()
        self.update_sidebar_stats()

    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.time_display.configure(text=time_str)
        
        # Update progress ring
        if hasattr(self, 'progress_ring') and self.total_time > 0:
            progress = 1.0 - (self.time_left / self.total_time)
            self.progress_ring.set_progress(progress)
        
    def play_sound(self):
        if self.settings["sound"] == "none":
            return
            
        try:
            if platform.system() == "Windows":
                if self.settings["sound"] == "bell":
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                elif self.settings["sound"] == "chime":
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                elif self.settings["sound"] == "digital":
                    winsound.MessageBeep(winsound.MB_ICONHAND)
            else:
                # For other platforms, just use system beep
                print('\a')
        except:
            pass
            
    def show_notification(self, message=None, notification_type="timer"):
        """Show enhanced notifications"""
        if not self.settings["notifications"]:
            return
            
        if message is None:
            if self.mode == "pomodoro":
                message = "Focus session completed! Time for a break."
            else:
                message = "Break time is over! Ready to focus?"
                
        # Different notification types
        if notification_type == "timer":
            title = "Pomodoro Strike"
            icon = "info"
        elif notification_type == "task_added":
            title = "Task Added"
            icon = "info"
        elif notification_type == "water":
            title = "Water Break"
            icon = "warning"
        elif notification_type == "overdue":
            title = "Overdue Tasks"
            icon = "warning"
        else:
            title = "Pomodoro Strike"
            icon = "info"
            
        # Show system tray notification if available
        if self.system_tray:
            try:
                self.system_tray.notify(title, message)
            except:
                pass
                
        # Show message box
        if icon == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
            
    def check_water_reminder(self):
        """Check if it's time for a water reminder"""
        if not self.settings["water_reminders"]:
            return
            
        now = datetime.now()
        time_since_last = (now - self.last_water_reminder).total_seconds() / 60
        
        if time_since_last >= self.settings["water_interval"]:
            self.show_notification("Time to hydrate! Take a water break.", "water")
            self.last_water_reminder = now
            
    def toggle_todo_sidebar(self):
        """Toggle the todo sidebar visibility"""
        if hasattr(self, 'todo_sidebar') and self.todo_sidebar.winfo_viewable():
            self.close_todo_sidebar()
        else:
            self.open_todo_sidebar()
            
    def open_todo_sidebar(self):
        """Open the todo sidebar"""
        if not hasattr(self, 'todo_sidebar'):
            self.create_todo_sidebar()
        self.todo_sidebar.deiconify()
        self.todo_sidebar.lift()
        if hasattr(self, 'todo_input'):
            self.todo_input.focus()
        
    def close_todo_sidebar(self):
        """Close the todo sidebar"""
        if hasattr(self, 'todo_sidebar'):
            self.todo_sidebar.withdraw()
            
    def create_todo_sidebar(self):
        """Create the todo sidebar"""
        # Create todo sidebar as a toplevel window for better UX
        self.todo_sidebar = ctk.CTkToplevel(self)
        self.todo_sidebar.title("Tasks")
        self.todo_sidebar.geometry("400x800")
        self.todo_sidebar.resizable(True, True)
        self.todo_sidebar.transient(self)
        
        # Position the sidebar next to the main window
        self.todo_sidebar.geometry("+%d+%d" % (self.winfo_x() + self.winfo_width(), self.winfo_y()))
        
        # Todo header
        todo_header = ctk.CTkFrame(self.todo_sidebar)
        todo_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            todo_header, 
            text="Today's Tasks", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            todo_header,
            text="✕",
            width=30,
            command=self.close_todo_sidebar
        ).pack(side="right", padx=10, pady=10)
        
        # Todo input with advanced options
        input_frame = ctk.CTkFrame(self.todo_sidebar)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Main input
        self.todo_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Add a new task...",
            height=35
        )
        self.todo_input.pack(fill="x", padx=10, pady=(10, 5))
        self.todo_input.bind("<Return>", lambda e: self.add_todo())
        
        # Advanced options frame
        advanced_frame = ctk.CTkFrame(input_frame)
        advanced_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Category and priority in one row
        options_row1 = ctk.CTkFrame(advanced_frame)
        options_row1.pack(fill="x", pady=2)
        
        ctk.CTkLabel(options_row1, text="Category:", font=ctk.CTkFont(size=10)).pack(side="left", padx=(5, 2))
        self.new_task_category = ctk.CTkOptionMenu(
            options_row1,
            values=self.categories,
            width=80
        )
        self.new_task_category.pack(side="left", padx=2)
        
        ctk.CTkLabel(options_row1, text="Priority:", font=ctk.CTkFont(size=10)).pack(side="left", padx=(10, 2))
        self.new_task_priority = ctk.CTkOptionMenu(
            options_row1,
            values=self.priorities,
            width=80
        )
        self.new_task_priority.pack(side="left", padx=2)
        
        # Due date and estimated time in second row
        options_row2 = ctk.CTkFrame(advanced_frame)
        options_row2.pack(fill="x", pady=2)
        
        ctk.CTkLabel(options_row2, text="Due:", font=ctk.CTkFont(size=10)).pack(side="left", padx=(5, 2))
        self.new_task_due_date = ctk.CTkEntry(
            options_row2,
            placeholder_text="YYYY-MM-DD",
            width=100
        )
        self.new_task_due_date.pack(side="left", padx=2)
        
        ctk.CTkLabel(options_row2, text="Est. (min):", font=ctk.CTkFont(size=10)).pack(side="left", padx=(10, 2))
        self.new_task_estimated = ctk.CTkEntry(
            options_row2,
            placeholder_text="30",
            width=60
        )
        self.new_task_estimated.pack(side="left", padx=2)
        
        # Add button
        add_button_frame = ctk.CTkFrame(input_frame)
        add_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            add_button_frame,
            text="+ Add Task",
            command=self.add_todo,
            height=30
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            add_button_frame,
            text="📊 Stats",
            command=self.show_task_stats,
            height=30
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Todo list
        self.todo_list_frame = ctk.CTkScrollableFrame(self.todo_sidebar)
        self.todo_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Todo stats
        stats_frame = ctk.CTkFrame(self.todo_sidebar)
        stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Completed count
        completed_frame = ctk.CTkFrame(stats_frame)
        completed_frame.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkLabel(completed_frame, text="Completed", font=ctk.CTkFont(size=12)).pack()
        self.completed_count_label = ctk.CTkLabel(
            completed_frame, 
            text="0", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.completed_count_label.pack()
        
        # Remaining count
        remaining_frame = ctk.CTkFrame(stats_frame)
        remaining_frame.pack(side="right", fill="x", expand=True, padx=(5, 10), pady=10)
        
        ctk.CTkLabel(remaining_frame, text="Remaining", font=ctk.CTkFont(size=12)).pack()
        self.remaining_count_label = ctk.CTkLabel(
            remaining_frame, 
            text="0", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.remaining_count_label.pack()
        
        # Render existing todos
        self.render_todos()
        
        # Handle window close
        self.todo_sidebar.protocol("WM_DELETE_WINDOW", self.close_todo_sidebar)
        
    def add_todo(self):
        """Add a new todo item"""
        text = self.todo_input.get().strip()
        if text:
            # Get advanced options
            category = self.new_task_category.get()
            priority = self.new_task_priority.get()
            due_date = self.new_task_due_date.get().strip()
            estimated_time_str = self.new_task_estimated.get().strip()
            
            # Validate due date
            if due_date and not self.is_valid_date(due_date):
                messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format")
                return
                
            # Validate estimated time
            estimated_time = 0
            if estimated_time_str:
                try:
                    estimated_time = int(estimated_time_str)
                    if estimated_time < 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Invalid Time", "Please enter a valid number for estimated time")
                    return
            
            # Create todo item
            todo = TodoItem(
                text=text,
                category=category,
                priority=priority,
                due_date=due_date if due_date else None
            )
            todo.estimated_time = estimated_time
            
            self.todos.append(todo)
            self.save_todos()
            self.render_todos()
            self.update_sidebar_stats()
            
            # Clear input fields
            self.todo_input.delete(0, "end")
            self.new_task_due_date.delete(0, "end")
            self.new_task_estimated.delete(0, "end")
            
            # Show notification
            self.show_notification(f"Task added: {text}", "task_added")
            
            # Check for overdue tasks
            self.check_overdue_tasks()
        
    def is_valid_date(self, date_str):
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
            
    def filter_todos(self, *args):
        """Filter todos based on selected criteria"""
        self.render_todos()
        
    def check_overdue_tasks(self):
        """Check for overdue tasks and show notifications"""
        today = datetime.now().date()
        overdue_tasks = []
        
        for todo in self.todos:
            if not todo.completed and todo.due_date:
                try:
                    due_date = datetime.strptime(todo.due_date, "%Y-%m-%d").date()
                    if due_date < today:
                        overdue_tasks.append(todo)
                except ValueError:
                    continue
                    
        if overdue_tasks and self.settings["notifications"]:
            overdue_text = "\n".join([f"• {task.text}" for task in overdue_tasks[:3]])
            if len(overdue_tasks) > 3:
                overdue_text += f"\n... and {len(overdue_tasks) - 3} more"
                
            messagebox.showwarning(
                "Overdue Tasks", 
                f"You have {len(overdue_tasks)} overdue task(s):\n\n{overdue_text}"
            )
            
    def render_todos(self):
        # Clear existing todos
        for widget in self.todo_list_frame.winfo_children():
            widget.destroy()
            
        # Filter todos (simplified without filter UI for now)
        filtered_todos = []
        for todo in self.todos:
            # Show all todos for now
            filtered_todos.append(todo)
            
        # Sort todos: incomplete first, then by priority, then by due date
        def sort_key(todo):
            if todo.completed:
                return (1, 0, None)  # Completed tasks go last
            else:
                priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
                due_date = None
                if todo.due_date:
                    try:
                        due_date = datetime.strptime(todo.due_date, "%Y-%m-%d").date()
                    except ValueError:
                        pass
                return (0, priority_order.get(todo.priority, 2), due_date)
                
        filtered_todos.sort(key=sort_key)
        
        # Render todos
        for todo in filtered_todos:
            self.create_todo_widget(todo)
            
        # Update counts
        completed_count = sum(1 for todo in self.todos if todo.completed)
        remaining_count = len(self.todos) - completed_count
        
        if hasattr(self, 'completed_count_label'):
            self.completed_count_label.configure(text=str(completed_count))
        if hasattr(self, 'remaining_count_label'):
            self.remaining_count_label.configure(text=str(remaining_count))
        
    def create_todo_widget(self, todo):
        todo_frame = ctk.CTkFrame(self.todo_list_frame)
        todo_frame.pack(fill="x", pady=2)
        
        # Main content frame
        content_frame = ctk.CTkFrame(todo_frame)
        content_frame.pack(fill="x", padx=5, pady=5)
        
        # Top row: checkbox, text, delete button
        top_row = ctk.CTkFrame(content_frame)
        top_row.pack(fill="x", pady=2)
        
        # Checkbox
        completed_var = ctk.BooleanVar(value=todo.completed)
        checkbox = ctk.CTkCheckBox(
            top_row,
            text="",
            variable=completed_var,
            command=lambda: self.toggle_todo(todo.id, completed_var)
        )
        checkbox.pack(side="left", padx=(5, 5), pady=5)
        
        # Todo text
        text_color = "gray" if todo.completed else "white"
        text_label = ctk.CTkLabel(
            top_row,
            text=todo.text,
            text_color=text_color,
            anchor="w",
            wraplength=200
        )
        text_label.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            top_row,
            text="✕",
            width=25,
            height=25,
            command=lambda: self.delete_todo(todo.id)
        )
        delete_btn.pack(side="right", padx=(0, 5), pady=5)
        
        # Bottom row: metadata
        if not todo.completed:
            meta_row = ctk.CTkFrame(content_frame)
            meta_row.pack(fill="x", pady=2)
            
            # Category badge
            category_color = self.get_category_color(todo.category)
            category_label = ctk.CTkLabel(
                meta_row,
                text=todo.category,
                font=ctk.CTkFont(size=10),
                fg_color=category_color,
                corner_radius=10,
                width=60
            )
            category_label.pack(side="left", padx=(5, 2), pady=2)
            
            # Priority badge
            priority_color = self.get_priority_color(todo.priority)
            priority_label = ctk.CTkLabel(
                meta_row,
                text=todo.priority,
                font=ctk.CTkFont(size=10),
                fg_color=priority_color,
                corner_radius=10,
                width=50
            )
            priority_label.pack(side="left", padx=2, pady=2)
            
            # Due date
            if todo.due_date:
                due_date_label = ctk.CTkLabel(
                    meta_row,
                    text=f"Due: {todo.due_date}",
                    font=ctk.CTkFont(size=10),
                    text_color=self.get_due_date_color(todo.due_date)
                )
                due_date_label.pack(side="left", padx=(10, 2), pady=2)
                
            # Estimated time
            if todo.estimated_time > 0:
                time_label = ctk.CTkLabel(
                    meta_row,
                    text=f"Est: {todo.estimated_time}m",
                    font=ctk.CTkFont(size=10),
                    text_color="gray"
                )
                time_label.pack(side="right", padx=(2, 5), pady=2)
                
    def get_category_color(self, category):
        """Get color for category badge"""
        colors = {
            "Work": "#FF6B6B",
            "Study": "#4ECDC4", 
            "Personal": "#45B7D1",
            "Health": "#96CEB4",
            "Finance": "#FFEAA7",
            "General": "#DDA0DD"
        }
        return colors.get(category, "#DDA0DD")
        
    def get_priority_color(self, priority):
        """Get color for priority badge"""
        colors = {
            "Urgent": "#FF4757",
            "High": "#FF6B6B", 
            "Medium": "#FFA502",
            "Low": "#2ED573"
        }
        return colors.get(priority, "#FFA502")
        
    def get_due_date_color(self, due_date_str):
        """Get color for due date based on urgency"""
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            days_until = (due_date - today).days
            
            if days_until < 0:
                return "#FF4757"  # Red for overdue
            elif days_until == 0:
                return "#FFA502"  # Orange for today
            elif days_until <= 2:
                return "#FF6B6B"  # Light red for soon
            else:
                return "gray"     # Gray for far away
        except ValueError:
            return "gray"
            
    def show_task_stats(self):
        """Show task statistics in a new window"""
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Task Statistics")
        stats_window.geometry("400x500")
        stats_window.transient(self)
        stats_window.grab_set()
        
        # Calculate statistics
        total_tasks = len(self.todos)
        completed_tasks = sum(1 for todo in self.todos if todo.completed)
        pending_tasks = total_tasks - completed_tasks
        
        # Category breakdown
        category_stats = {}
        for todo in self.todos:
            category_stats[todo.category] = category_stats.get(todo.category, 0) + 1
            
        # Priority breakdown
        priority_stats = {}
        for todo in self.todos:
            priority_stats[todo.priority] = priority_stats.get(todo.priority, 0) + 1
            
        # Overdue tasks
        overdue_count = 0
        today = datetime.now().date()
        for todo in self.todos:
            if not todo.completed and todo.due_date:
                try:
                    due_date = datetime.strptime(todo.due_date, "%Y-%m-%d").date()
                    if due_date < today:
                        overdue_count += 1
                except ValueError:
                    continue
                    
        # Create content
        content_frame = ctk.CTkScrollableFrame(stats_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Overall stats
        ctk.CTkLabel(
            content_frame,
            text="Overall Statistics",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 10))
        
        stats_frame = ctk.CTkFrame(content_frame)
        stats_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(stats_frame, text=f"Total Tasks: {total_tasks}").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(stats_frame, text=f"Completed: {completed_tasks}").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(stats_frame, text=f"Pending: {pending_tasks}").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(stats_frame, text=f"Overdue: {overdue_count}").pack(anchor="w", padx=10, pady=2)
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            ctk.CTkLabel(
                stats_frame, 
                text=f"Completion Rate: {completion_rate:.1f}%"
            ).pack(anchor="w", padx=10, pady=2)
            
        # Category breakdown
        ctk.CTkLabel(
            content_frame,
            text="By Category",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))
        
        for category, count in category_stats.items():
            cat_frame = ctk.CTkFrame(content_frame)
            cat_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                cat_frame,
                text=category,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkLabel(
                cat_frame,
                text=str(count)
            ).pack(side="right", padx=10, pady=5)
            
        # Priority breakdown
        ctk.CTkLabel(
            content_frame,
            text="By Priority",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))
        
        for priority, count in priority_stats.items():
            pri_frame = ctk.CTkFrame(content_frame)
            pri_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                pri_frame,
                text=priority,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkLabel(
                pri_frame,
                text=str(count)
            ).pack(side="right", padx=10, pady=5)
        
    def toggle_todo(self, todo_id, completed_var):
        todo = next((t for t in self.todos if t.id == todo_id), None)
        if todo:
            todo.completed = completed_var.get()
            self.save_todos()
            self.render_todos()
            self.update_todo_count()
            
            # Update productivity data for completed tasks
            if todo.completed:
                self.productivity_data.update_daily_stats(0, 1)  # 0 focus time, 1 task completed
                self.save_productivity_data()
            
    def delete_todo(self, todo_id):
        self.todos = [t for t in self.todos if t.id != todo_id]
        self.save_todos()
        self.render_todos()
        self.update_todo_count()
        
    def update_todo_count(self):
        """Update todo count display"""
        count = len([t for t in self.todos if not t.completed])
        # Update sidebar stats instead of a separate count variable
        self.update_sidebar_stats()
        
    def handle_keyboard_shortcuts(self, event):
        # Space to toggle timer
        if event.keysym == "space":
            if self.is_running:
                self.pause_timer()
            else:
                self.start_timer()
        # R to reset
        elif event.keysym == "r":
            self.reset_timer()
        # S to open settings
        elif event.keysym == "s":
            self.open_settings()
        # T to toggle todo sidebar
        elif event.keysym == "t":
            self.toggle_todo_sidebar()
        # F11 or F to toggle fullscreen
        elif event.keysym in ["F11", "f"]:
            self.toggle_fullscreen()
        # M to toggle minimalist mode
        elif event.keysym == "m":
            self.toggle_minimalist_mode()
        # Escape to exit fullscreen
        elif event.keysym == "Escape" and self.is_fullscreen:
            self.toggle_fullscreen()
            
    def save_settings_to_file(self):
        try:
            with open(get_data_path("settings.json"), "w") as f:
                json.dump(self.settings, f)
        except:
            pass
            
    def load_settings(self):
        try:
            with open(get_data_path("settings.json"), "r") as f:
                loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
        except:
            pass
            
    def save_todos(self):
        try:
            todos_data = []
            for todo in self.todos:
                todos_data.append({
                    "id": todo.id,
                    "text": todo.text,
                    "completed": todo.completed,
                    "created_at": todo.created_at,
                    "category": todo.category,
                    "priority": todo.priority,
                    "due_date": todo.due_date,
                    "estimated_time": todo.estimated_time,
                    "actual_time": todo.actual_time
                })
            with open(get_data_path("todos.json"), "w") as f:
                json.dump(todos_data, f)
        except:
            pass
            
    def load_todos(self):
        try:
            with open(get_data_path("todos.json"), "r") as f:
                todos_data = json.load(f)
                self.todos = []
                for todo_data in todos_data:
                    todo = TodoItem(
                        todo_data["text"],
                        todo_data["completed"],
                        todo_data["created_at"],
                        todo_data["category"],
                        todo_data["priority"],
                        todo_data["due_date"]
                    )
                    todo.id = todo_data["id"]
                    todo.estimated_time = todo_data["estimated_time"]
                    todo.actual_time = todo_data["actual_time"]
                    self.todos.append(todo)
        except:
            pass
            
    def save_total_focus_time(self):
        try:
            with open(get_data_path("total_focus_time.json"), "w") as f:
                json.dump({"total_focus_time": self.total_focus_time}, f)
        except:
            pass
            
    def load_total_focus_time(self):
        try:
            with open(get_data_path("total_focus_time.json"), "r") as f:
                data = json.load(f)
                self.total_focus_time = data.get("total_focus_time", 0)
                self.update_total_time_display()
        except:
            pass

    def apply_theme(self):
        """Apply current theme and appearance mode"""
        # Set appearance mode
        ctk.set_appearance_mode(self.settings["appearance_mode"])
        
        # Set color theme
        ctk.set_default_color_theme(self.settings["theme"])
        
        # Update current theme
        self.current_theme = self.settings["theme"]
        
        # Update theme button
        if hasattr(self, 'theme_btn'):
            self.theme_btn.configure(text="🌙" if self.settings["appearance_mode"] == "dark" else "☀️")
            
        # Update progress ring if it exists
        if hasattr(self, 'progress_ring'):
            self.progress_ring.draw_ring()

    def show_motivational_quote(self):
        """Show a random motivational quote"""
        if self.settings["show_motivational_quotes"]:
            quote = random.choice(MOTIVATIONAL_QUOTES)
            # Show quote in a small popup or status bar
            self.after(2000, lambda: self.show_quote_popup(quote))
            
    def show_quote_popup(self, quote):
        """Show motivational quote in a popup"""
        quote_window = ctk.CTkToplevel(self)
        quote_window.title("Daily Motivation")
        quote_window.geometry("500x150")
        quote_window.transient(self)
        quote_window.grab_set()
        
        # Center the window
        quote_window.update_idletasks()
        x = (quote_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (quote_window.winfo_screenheight() // 2) - (150 // 2)
        quote_window.geometry(f"500x150+{x}+{y}")
        
        # Quote content
        ctk.CTkLabel(
            quote_window,
            text="💪 Daily Motivation",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            quote_window,
            text=quote,
            font=ctk.CTkFont(size=14),
            wraplength=450
        ).pack(pady=(0, 20))
        
        # Auto-close after 5 seconds
        quote_window.after(5000, quote_window.destroy)
        
    def update_activity(self, event=None):
        """Update last activity time for idle detection"""
        self.last_activity = datetime.now()
        
    def start_idle_monitoring(self):
        """Start monitoring for system idle time"""
        def check_idle():
            if self.settings["auto_pause_idle"] and self.is_running:
                idle_time = (datetime.now() - self.last_activity).total_seconds()
                if idle_time > self.settings["idle_threshold"]:
                    self.pause_timer()
                    self.show_notification("Timer paused due to inactivity", "idle")
            self.after(30000, check_idle)  # Check every 30 seconds
            
        self.after(30000, check_idle)
        
    def load_productivity_data(self):
        """Load productivity data from file"""
        try:
            with open(get_data_path("productivity_data.json"), "r") as f:
                data = json.load(f)
                self.productivity_data.focus_streak = data.get("focus_streak", 0)
                self.productivity_data.longest_streak = data.get("longest_streak", 0)
                self.productivity_data.daily_goals = data.get("daily_goals", self.productivity_data.daily_goals)
                self.productivity_data.achievements = data.get("achievements", [])
                self.productivity_data.daily_stats = defaultdict(lambda: {
                    "focus_sessions": 0,
                    "focus_time": 0,
                    "tasks_completed": 0,
                    "productivity_score": 0.0
                }, data.get("daily_stats", {}))
                self.productivity_data.weekly_stats = defaultdict(lambda: {
                    "focus_sessions": 0,
                    "focus_time": 0,
                    "tasks_completed": 0,
                    "productivity_score": 0.0
                }, data.get("weekly_stats", {}))
                self.productivity_data.monthly_stats = defaultdict(lambda: {
                    "focus_sessions": 0,
                    "focus_time": 0,
                    "tasks_completed": 0,
                    "productivity_score": 0.0
                }, data.get("monthly_stats", {}))
                self.productivity_data.best_hours = defaultdict(int, data.get("best_hours", {}))
        except:
            pass
            
    def save_productivity_data(self):
        """Save productivity data to file"""
        try:
            data = {
                "focus_streak": self.productivity_data.focus_streak,
                "longest_streak": self.productivity_data.longest_streak,
                "daily_goals": self.productivity_data.daily_goals,
                "achievements": self.productivity_data.achievements,
                "daily_stats": dict(self.productivity_data.daily_stats),
                "weekly_stats": dict(self.productivity_data.weekly_stats),
                "monthly_stats": dict(self.productivity_data.monthly_stats),
                "best_hours": dict(self.productivity_data.best_hours)
            }
            with open(get_data_path("productivity_data.json"), "w") as f:
                json.dump(data, f, indent=2)
        except:
            pass
            
    def show_productivity_dashboard(self):
        """Show comprehensive productivity dashboard"""
        dashboard_window = ctk.CTkToplevel(self)
        dashboard_window.title("Productivity Dashboard")
        dashboard_window.geometry("800x600")
        dashboard_window.transient(self)
        dashboard_window.grab_set()
        
        # Create notebook for tabs
        notebook = ctk.CTkTabview(dashboard_window)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Overview tab
        overview_tab = notebook.add("Overview")
        self.create_overview_tab(overview_tab)
        
        # Statistics tab
        stats_tab = notebook.add("Statistics")
        self.create_statistics_tab(stats_tab)
        
        # Achievements tab
        achievements_tab = notebook.add("Achievements")
        self.create_achievements_tab(achievements_tab)
        
        # Goals tab
        goals_tab = notebook.add("Goals")
        self.create_goals_tab(goals_tab)
        
    def create_overview_tab(self, parent):
        """Create overview tab content"""
        # Current streak
        streak_frame = ctk.CTkFrame(parent)
        streak_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            streak_frame,
            text="🔥 Current Focus Streak",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            streak_frame,
            text=f"{self.productivity_data.focus_streak} days",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0, 10))
        
        # Today's progress
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = self.productivity_data.daily_stats[today]
        
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            progress_frame,
            text="📊 Today's Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Progress bars
        self.create_progress_bar(progress_frame, "Focus Time", today_stats["focus_time"], 240, "minutes")
        self.create_progress_bar(progress_frame, "Sessions", today_stats["focus_sessions"], 8, "sessions")
        self.create_progress_bar(progress_frame, "Tasks", today_stats["tasks_completed"], 5, "tasks")
        
        # Productivity score
        score_frame = ctk.CTkFrame(parent)
        score_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            score_frame,
            text="🎯 Productivity Score",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        score = today_stats["productivity_score"]
        ctk.CTkLabel(
            score_frame,
            text=f"{score:.1f}/100",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.get_score_color(score)
        ).pack(pady=(0, 10))
        
    def create_progress_bar(self, parent, label, current, target, unit):
        """Create a progress bar widget"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5, 0))
        
        progress = min(1.0, current / target) if target > 0 else 0.0
        progress_bar = ctk.CTkProgressBar(frame)
        progress_bar.pack(fill="x", padx=10, pady=5)
        progress_bar.set(progress)
        
        ctk.CTkLabel(
            frame, 
            text=f"{current}/{target} {unit} ({progress*100:.1f}%)",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=10, pady=(0, 5))
        
    def get_score_color(self, score):
        """Get color for productivity score"""
        if score >= 80:
            return "#2ED573"  # Green
        elif score >= 60:
            return "#FFA502"  # Orange
        else:
            return "#FF4757"  # Red
            
    def create_statistics_tab(self, parent):
        """Create statistics tab content"""
        # Weekly stats
        week_key = datetime.now().strftime("%Y-W%U")
        week_stats = self.productivity_data.weekly_stats[week_key]
        
        weekly_frame = ctk.CTkFrame(parent)
        weekly_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            weekly_frame,
            text="📈 This Week",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        stats_text = f"""
        Focus Sessions: {week_stats['focus_sessions']}
        Focus Time: {week_stats['focus_time']} minutes
        Tasks Completed: {week_stats['tasks_completed']}
        Average Score: {week_stats['productivity_score']:.1f}/100
        """
        
        ctk.CTkLabel(
            weekly_frame,
            text=stats_text,
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
        
        # Best hours
        hours_frame = ctk.CTkFrame(parent)
        hours_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            hours_frame,
            text="⏰ Best Focus Hours",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Get top 3 hours
        sorted_hours = sorted(self.productivity_data.best_hours.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for hour, count in sorted_hours:
            ctk.CTkLabel(
                hours_frame,
                text=f"{hour:02d}:00 - {count} sessions",
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w", padx=10, pady=2)
            
    def create_achievements_tab(self, parent):
        """Create achievements tab content"""
        # Achievements list
        if self.productivity_data.achievements:
            for achievement in self.productivity_data.achievements:
                achievement_frame = ctk.CTkFrame(parent)
                achievement_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(
                    achievement_frame,
                    text=f"🏆 {achievement}",
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(pady=10)
        else:
            ctk.CTkLabel(
                parent,
                text="No achievements yet. Keep working to unlock them!",
                font=ctk.CTkFont(size=14)
            ).pack(pady=50)
            
    def create_goals_tab(self, parent):
        """Create goals tab content"""
        # Daily goals
        goals_frame = ctk.CTkFrame(parent)
        goals_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            goals_frame,
            text="🎯 Daily Goals",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Goal inputs
        goals = self.productivity_data.daily_goals
        
        # Focus sessions goal
        sessions_frame = ctk.CTkFrame(goals_frame)
        sessions_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(sessions_frame, text="Focus Sessions:").pack(side="left", padx=10, pady=10)
        sessions_entry = ctk.CTkEntry(sessions_frame, width=100)
        sessions_entry.pack(side="right", padx=10, pady=10)
        sessions_entry.insert(0, str(goals["focus_sessions"]))
        
        # Focus time goal
        time_frame = ctk.CTkFrame(goals_frame)
        time_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(time_frame, text="Focus Time (minutes):").pack(side="left", padx=10, pady=10)
        time_entry = ctk.CTkEntry(time_frame, width=100)
        time_entry.pack(side="right", padx=10, pady=10)
        time_entry.insert(0, str(goals["focus_time"]))
        
        # Tasks goal
        tasks_frame = ctk.CTkFrame(goals_frame)
        tasks_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(tasks_frame, text="Tasks Completed:").pack(side="left", padx=10, pady=10)
        tasks_entry = ctk.CTkEntry(tasks_frame, width=100)
        tasks_entry.pack(side="right", padx=10, pady=10)
        tasks_entry.insert(0, str(goals["tasks_completed"]))
        
        # Save button
        def save_goals():
            try:
                self.productivity_data.daily_goals["focus_sessions"] = int(sessions_entry.get())
                self.productivity_data.daily_goals["focus_time"] = int(time_entry.get())
                self.productivity_data.daily_goals["tasks_completed"] = int(tasks_entry.get())
                self.save_productivity_data()
                messagebox.showinfo("Success", "Goals saved successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
                
        ctk.CTkButton(
            goals_frame,
            text="Save Goals",
            command=save_goals
        ).pack(pady=10)
        
    def export_data(self, format_type="csv"):
        """Export productivity data"""
        if format_type == "csv":
            self.export_to_csv()
        else:
            messagebox.showinfo("Export", "PDF export coming soon!")
            
    def export_to_csv(self):
        """Export data to CSV file"""
        try:
            filename = f"pomodoro_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Date', 'Focus Sessions', 'Focus Time (min)', 'Tasks Completed', 'Productivity Score'])
                
                # Write daily stats
                for date, stats in self.productivity_data.daily_stats.items():
                    writer.writerow([
                        date,
                        stats['focus_sessions'],
                        stats['focus_time'],
                        stats['tasks_completed'],
                        f"{stats['productivity_score']:.1f}"
                    ])
                    
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
            
    def toggle_always_on_top(self):
        """Toggle always on top window state"""
        self.always_on_top = not self.always_on_top
        self.attributes('-topmost', self.always_on_top)
        self.settings["always_on_top"] = self.always_on_top
        self.save_settings_to_file()
        
    def set_window_transparency(self, transparency):
        """Set window transparency (0.0 to 1.0)"""
        self.window_transparency = max(0.1, min(1.0, transparency))
        self.attributes('-alpha', self.window_transparency)
        self.settings["window_transparency"] = self.window_transparency
        self.save_settings_to_file()

    def toggle_appearance_mode(self):
        """Toggle between dark and light appearance modes"""
        new_mode = "light" if self.settings["appearance_mode"] == "dark" else "dark"
        self.settings["appearance_mode"] = new_mode
        self.save_settings_to_file()
        self.apply_theme()
        
        # Update theme button
        self.theme_btn.configure(text="🌙" if new_mode == "dark" else "☀️")

    def toggle_minimalist_mode(self):
        """Toggle minimalist mode"""
        self.is_minimalist = not self.is_minimalist
        self.settings["minimalist_mode"] = self.is_minimalist
        self.save_settings_to_file()
        
        if self.is_minimalist:
            # Hide sidebar
            if hasattr(self, 'sidebar'):
                self.sidebar.grid_forget()
        else:
            # Show sidebar
            if hasattr(self, 'sidebar'):
                self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes('-fullscreen', self.is_fullscreen)
        
        if self.is_fullscreen:
            self.fullscreen_btn.configure(text="⛶")
        else:
            self.fullscreen_btn.configure(text="⛶")

    def on_resize(self, event):
        """Handle window resize events"""
        # This method can be used for responsive design adjustments
        pass

    def update_sidebar_stats(self):
        """Update sidebar statistics"""
        # Update focus time
        hours = self.total_focus_time // 60
        minutes = self.total_focus_time % 60
        time_str = f"{hours:02d}:{minutes:02d}"
        if hasattr(self, 'sidebar_focus_time'):
            self.sidebar_focus_time.configure(text=time_str)
        
        # Update sessions
        if hasattr(self, 'sidebar_sessions'):
            self.sidebar_sessions.configure(text=str(self.sessions))
        
        # Update tasks completed
        completed_tasks = sum(1 for todo in self.todos if todo.completed)
        if hasattr(self, 'sidebar_tasks'):
            self.sidebar_tasks.configure(text=str(completed_tasks))
        
        # Update streak
        if hasattr(self, 'streak_label'):
            self.streak_label.configure(text=f"{self.productivity_data.focus_streak} days")
            
    def update_total_time_display(self):
        # This method is now handled by update_sidebar_stats
        self.update_sidebar_stats()

if __name__ == "__main__":
    app = PomodoroStrike()
    app.mainloop() 