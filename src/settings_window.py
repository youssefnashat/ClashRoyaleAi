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
        self.root.geometry("280x200")
        self.root.resizable(False, False)
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Feature states (default values)
        self.grid_opacity = tk.DoubleVar(value=20.0)
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
            font=("Arial", 12, "bold")
        )
        title.pack(pady=8)
        
        # Separator
        sep1 = ttk.Separator(self.root, orient='horizontal')
        sep1.pack(fill='x', padx=10, pady=5)
        
        # Grid Opacity Slider
        grid_frame = ttk.Frame(self.root)
        grid_frame.pack(fill='x', padx=10, pady=8)
        
        grid_label = ttk.Label(grid_frame, text="Grid Opacity:")
        grid_label.pack(side='left', padx=5)
        
        grid_slider = ttk.Scale(
            grid_frame,
            from_=0,
            to=100,
            variable=self.grid_opacity,
            orient='horizontal',
            length=150
        )
        grid_slider.pack(side='left', padx=5, fill='x', expand=True)
        
        self.grid_opacity_label = ttk.Label(grid_frame, text="20%", width=4)
        self.grid_opacity_label.pack(side='left', padx=5)
        
        # Bind slider change to update label
        self.grid_opacity.trace('w', self._update_opacity_label)
        
        # Separator
        sep2 = ttk.Separator(self.root, orient='horizontal')
        sep2.pack(fill='x', padx=10, pady=5)
        
        # Elixir Tracking Toggle
        elixir_check = ttk.Checkbutton(
            self.root,
            text="Elixir Tracking",
            variable=self.elixir_enabled,
            state='normal'
        )
        elixir_check.pack(fill='x', padx=20, pady=4, anchor='w')
        
        # Tower Detection Toggle
        towers_check = ttk.Checkbutton(
            self.root,
            text="Tower Detection",
            variable=self.towers_enabled,
            state='normal'
        )
        towers_check.pack(fill='x', padx=20, pady=4, anchor='w')
    
    def _on_close_window(self):
        """Handle window close button"""
        self.running = False
        self.root.destroy()
    
    def _update_opacity_label(self, *args):
        """Update opacity label when slider changes"""
        opacity = int(self.grid_opacity.get())
        self.grid_opacity_label.config(text=f"{opacity}%")
    
    def get_grid_opacity(self):
        """Get grid opacity as a value from 0.0 to 1.0"""
        try:
            return self.grid_opacity.get() / 100.0
        except:
            return 1.0
    
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
