import cv2
import numpy as np
import mss
import win32gui
import ctypes
from .config import WINDOW_NAME_PATTERNS, RESIZE_WIDTH, RESIZE_HEIGHT

# 1. High DPI Fix
try:
    # PROCESS_PER_MONITOR_DPI_AWARE = 2
    # This ensures we get real physical pixel coordinates even if the window is on a secondary monitor
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        # Fallback for older Windows
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

class WindowCapture:
    def __init__(self):
        self.hwnd = None
        self.find_window()

    def find_window(self):
        """Finds the emulator window by checking known titles."""
        self.hwnd = None
        
        def callback(hwnd, extra):
            if self.hwnd: return # Already found
            title = win32gui.GetWindowText(hwnd)
            for pattern in WINDOW_NAME_PATTERNS:
                if pattern.lower() in title.lower():
                    self.hwnd = hwnd
                    return

        win32gui.EnumWindows(callback, None)
        return self.hwnd is not None

    def get_screenshot(self):
        """Captures the window, resizes it, and returns a numpy array."""
        if not self.hwnd:
            if not self.find_window():
                return None

        try:
            # Get client area dimensions (content only, no borders)
            left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
            w = right - left
            h = bottom - top
            
            # Convert client top-left (0,0) to screen coordinates
            # ClientToScreen expects a point (x, y)
            top_left = win32gui.ClientToScreen(self.hwnd, (0, 0))
            x, y = top_left
            
            # Debug: Print dimensions to verify
            # print(f"Client Area: {w}x{h} at ({x},{y})")
            
            if w > h:
                print(f"Warning: Window is Landscape ({w}x{h}). Clash Royale requires Portrait!")
                print("Please rotate the emulator or change resolution to 900x1600.")
            
            if w == 0 or h == 0:
                return None

            # mss requires a dict
            monitor = {"top": y, "left": x, "width": w, "height": h}

            # Capture using context manager to avoid threading/state issues
            with mss.mss() as sct:
                img = np.array(sct.grab(monitor))

            # Drop Alpha channel (BGRA -> BGR)
            img = img[:, :, :3]

            # Resize to standard width
            # Calculate height to maintain aspect ratio
            aspect_ratio = h / w
            target_height = int(RESIZE_WIDTH * aspect_ratio)
            
            resized = cv2.resize(img, (RESIZE_WIDTH, target_height))
            return resized

        except Exception as e:
            # Only print error if it's not a known "window closed" issue
            print(f"Capture error: {e}")
            self.hwnd = None # Force re-find
            return None
