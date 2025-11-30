"""
Unified Overlay Window
Displays video feed with toggle controls at the bottom
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2


class OverlayWindow:
    """Main overlay window with video feed and integrated toggle controls"""
    
    def __init__(self, width=960, height=720):
        """Initialize overlay window with video display and controls"""
        self.root = tk.Tk()
        self.root.title("Clash Royale Overlay")
        
        # Window dimensions (account for controls at bottom)
        self.video_width = width
        self.video_height = height - 60  # Leave room for controls
        self.control_height = 60
        
        self.root.geometry(f"{self.video_width}x{self.video_height + self.control_height}")
        self.root.resizable(False, False)
        
        # Feature states
        self.grid_enabled = tk.BooleanVar(value=True)
        self.elixir_enabled = tk.BooleanVar(value=True)
        self.towers_enabled = tk.BooleanVar(value=False)
        
        # Video display
        self.video_label = tk.Label(self.root, bg='black')
        self.video_label.pack(fill='both', expand=True)
        
        # Control panel at bottom
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side='bottom', fill='x', padx=10, pady=8)
        
        # Grid Overlay Toggle
        grid_check = ttk.Checkbutton(
            control_frame,
            text="Grid",
            variable=self.grid_enabled,
            state='normal'
        )
        grid_check.pack(side='left', padx=5)
        
        # Elixir Tracking Toggle
        elixir_check = ttk.Checkbutton(
            control_frame,
            text="Elixir",
            variable=self.elixir_enabled,
            state='normal'
        )
        elixir_check.pack(side='left', padx=5)
        
        # Tower Detection Toggle
        towers_check = ttk.Checkbutton(
            control_frame,
            text="Towers",
            variable=self.towers_enabled,
            state='normal'
        )
        towers_check.pack(side='left', padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="Ready",
            relief='sunken'
        )
        self.status_label.pack(side='right', padx=5)
        
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)
        
        # PhotoImage reference (keep alive)
        self.photo = None
    
    def _on_close_window(self):
        """Handle window close button"""
        self.running = False
        self.root.destroy()
    
    def display_frame(self, frame):
        """Display a frame in the video label"""
        if not self.running:
            return
        
        try:
            # Resize frame to fit window
            resized = cv2.resize(frame, (self.video_width, self.video_height))
            
            # Convert BGR to RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.video_label.config(image=self.photo)
        except Exception as e:
            print(f"[ERROR] Failed to display frame: {e}")
    
    def update_status(self, text):
        """Update status label"""
        try:
            self.status_label.config(text=text)
        except:
            pass
    
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
