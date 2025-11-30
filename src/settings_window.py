"""
Settings Window for Clash Royale Overlay
Provides GUI controls to toggle features on/off in real-time
"""

import tkinter as tk
from tkinter import ttk


class SettingsWindow:
    """Separate window with toggles for all overlay features"""
    
    def __init__(self):
        """Initialize settings window with feature toggles"""
        self.root = tk.Tk()
        self.root.title("Clash Royale Overlay - Settings")
        self.root.geometry("350x280")
        self.root.resizable(False, False)
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Feature states (default values)
        self.grid_enabled = tk.BooleanVar(value=True)
        self.elixir_enabled = tk.BooleanVar(value=True)
        self.towers_enabled = tk.BooleanVar(value=False)
        
        # Build UI
        self._build_ui()
        
        # Track if window is running
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)
    
    def _build_ui(self):
        """Build the settings window UI"""
        
        # Title
        title = ttk.Label(
            self.root,
            text="Overlay Features",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)
        
        # Separator
        sep1 = ttk.Separator(self.root, orient='horizontal')
        sep1.pack(fill='x', padx=10, pady=5)
        
        # Grid Overlay Toggle
        grid_frame = ttk.Frame(self.root)
        grid_frame.pack(fill='x', padx=20, pady=8, anchor='w')
        
        grid_check = ttk.Checkbutton(
            grid_frame,
            text="Grid Overlay",
            variable=self.grid_enabled,
            state='normal'
        )
        grid_check.pack(side='left', fill='x')
        
        grid_status = ttk.Label(grid_frame, text="Tile visualization", foreground="gray", font=("Arial", 8))
        grid_status.pack(side='right', padx=10)
        
        # Elixir Tracking Toggle
        elixir_frame = ttk.Frame(self.root)
        elixir_frame.pack(fill='x', padx=20, pady=8, anchor='w')
        
        elixir_check = ttk.Checkbutton(
            elixir_frame,
            text="Elixir Tracking",
            variable=self.elixir_enabled,
            state='normal'
        )
        elixir_check.pack(side='left', fill='x')
        
        elixir_status = ttk.Label(elixir_frame, text="Elixir count", foreground="gray", font=("Arial", 8))
        elixir_status.pack(side='right', padx=10)
        
        # Tower Detection Toggle
        towers_frame = ttk.Frame(self.root)
        towers_frame.pack(fill='x', padx=20, pady=8, anchor='w')
        
        towers_check = ttk.Checkbutton(
            towers_frame,
            text="Tower Detection",
            variable=self.towers_enabled,
            state='normal'
        )
        towers_check.pack(side='left', fill='x')
        
        towers_status = ttk.Label(towers_frame, text="Princess towers", foreground="gray", font=("Arial", 8))
        towers_status.pack(side='right', padx=10)
        
        # Separator
        sep2 = ttk.Separator(self.root, orient='horizontal')
        sep2.pack(fill='x', padx=10, pady=10)
        
        # Status info
        info_label = ttk.Label(
            self.root,
            text="✓ Changes apply immediately",
            foreground="green",
            font=("Arial", 9)
        )
        info_label.pack(pady=5)
    
    def _on_close_window(self):
        """Handle window close button"""
        self.running = False
        self.root.destroy()
    
    def is_grid_enabled(self):
        """Check if grid overlay is enabled"""
        try:
            return self.grid_enabled.get()
        except:
            return False
    
    def is_elixir_enabled(self):
        """Check if elixir tracking is enabled"""
        try:
            return self.elixir_enabled.get()
        except:
            return False
    
    def is_towers_enabled(self):
        """Check if tower detection is enabled"""
        try:
            return self.towers_enabled.get()
        except:
            return False
    
    def update_window(self):
        """Process window events (non-blocking)"""
        try:
            self.root.update()
        except tk.TclError:
            self.running = False
    
    def close(self):
        """Close the window"""
        try:
            self.running = False
            self.root.destroy()
        except:
            pass
