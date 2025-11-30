import cv2
import numpy as np
import mss
import win32gui
import ctypes
from .config import WINDOW_NAME_PATTERNS, RESIZE_WIDTH, RESIZE_HEIGHT

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

class WindowCapture:
    def __init__(self):
        self.hwnd = None
        self.find_window()

    def find_window(self):
        """Finds the emulator window by checking known titles"""
        self.hwnd = None
        
        def callback(hwnd, extra):
            if self.hwnd: return
            title = win32gui.GetWindowText(hwnd)
            for pattern in WINDOW_NAME_PATTERNS:
                if pattern.lower() in title.lower():
                    self.hwnd = hwnd
                    print(f"Found window: {title}")
                    return

        win32gui.EnumWindows(callback, None)
        return self.hwnd is not None

    def get_screenshot(self):
        """Captures the window and returns a numpy array"""
        if not self.hwnd:
            if not self.find_window():
                return None

        try:
            left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
            w = right - left
            h = bottom - top
            
            top_left = win32gui.ClientToScreen(self.hwnd, (0, 0))
            x, y = top_left
            
            if w == 0 or h == 0:
                return None

            monitor = {"top": y, "left": x, "width": w, "height": h}

            with mss.mss() as sct:
                img = np.array(sct.grab(monitor))

            img = img[:, :, :3]
            aspect_ratio = h / w
            target_height = int(RESIZE_WIDTH * aspect_ratio)
            resized = cv2.resize(img, (RESIZE_WIDTH, target_height))
            return resized

        except Exception as e:
            self.hwnd = None
            return None
