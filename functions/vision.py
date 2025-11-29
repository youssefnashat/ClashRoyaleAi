"""
Vision module for recording and capturing frames from selected window.
This module handles window selection, recording video frames, and applying grid overlays.
"""

import cv2
import numpy as np
import mss
import win32gui  # type: ignore
import win32con  # type: ignore
from datetime import datetime
import os
import json


# ============================================================================
# WINDOW SELECTION FUNCTIONS (from windowing.py)
# ============================================================================

def get_all_windows():
    """
    Enumerate all visible windows on the system.
    
    Returns:
        list: List of tuples (hwnd, title) for each visible window
    """
    windows = []
    
    def callback(hwnd, extra):
        """Callback function for EnumWindows."""
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Only include windows with titles
                windows.append((hwnd, title))
    
    win32gui.EnumWindows(callback, None)
    return windows


def display_windows(windows):
    """
    Display available windows in a numbered list.
    
    Args:
        windows (list): List of tuples (hwnd, title) from get_all_windows()
    """
    print(f"\nFound {len(windows)} visible windows:\n")
    print("-" * 80)
    for i, (hwnd, title) in enumerate(windows, 1):
        # Handle Unicode characters that might not be encodable
        try:
            print(f"{i:3d}. {title}")
        except UnicodeEncodeError:
            title_safe = title.encode('utf-8', errors='replace').decode('utf-8')
            print(f"{i:3d}. {title_safe}")
    print("-" * 80)


def select_window(windows):
    """
    Prompt user to select a window from the list.
    
    Args:
        windows (list): List of tuples (hwnd, title) from get_all_windows()
    
    Returns:
        tuple: (hwnd, title) of the selected window, or (None, None) if cancelled
    """
    while True:
        try:
            choice = input("\nEnter the window number to select (or 'q' to cancel): ").strip()
            
            if choice.lower() == 'q':
                print("Selection cancelled.")
                return None, None
            
            num = int(choice)
            if 1 <= num <= len(windows):
                hwnd, title = windows[num - 1]
                print(f"\n✓ Selected: {title}")
                return hwnd, title
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(windows)}")
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")


def list_and_select_window():
    """
    Main function to list all windows and allow user selection.
    
    Returns:
        tuple: (hwnd, title) of the selected window, or (None, None) if cancelled
    """
    print("=" * 80)
    print("WINDOW SELECTOR FOR RECORDING")
    print("=" * 80)
    
    windows = get_all_windows()
    
    if not windows:
        print("\nNo visible windows found on the system.")
        return None, None
    
    display_windows(windows)
    hwnd, title = select_window(windows)
    
    if hwnd:
        print(f"\nWindow handle (hwnd): {hwnd}")
        print("This window will be recorded by the vision module.")
    
    return hwnd, title


# ============================================================================
# WINDOW RECORDER CLASS
# ============================================================================

class WindowRecorder:
    """Records video frames from a selected window."""
    
    # Grid constants
    GRID_WIDTH = 18
    GRID_HEIGHT = 32
    GRID_CONFIG_FILE = "grid_config.json"
    SHADED_TILES_FILE = "shaded_tiles.json"
    
    # Tile states with BGR colors
    TILE_STATES = {
        'red': (0, 0, 255),
        'leftEnemyDown': (0, 255, 0),
        'rightEnemyDown': (255, 0, 0),
        'leftFriendlyDown': (0, 255, 255),
        'rightFriendlyDown': (255, 0, 255)
    }
    
    def __init__(self, hwnd, output_dir="recordings"):
        """
        Initialize the window recorder.
        
        Args:
            hwnd (int): Window handle from windowing.py
            output_dir (str): Directory to save recordings
        """
        self.hwnd = hwnd
        self.output_dir = output_dir
        self.sct = mss.mss()
        self.frames = []
        self.recording = False
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get window position and size
        self.window_rect = {}
        self.update_window_rect()
        
        # Load grid configuration and tile states from JSON files
        self.grid_config = self._load_grid_config()
        self.tile_states = self._load_tile_states()
    
    def _load_grid_config(self):
        """Load grid scale and offset from grid_config.json."""
        default_config = {
            'scale_x': 0.85,
            'scale_y': 0.85,
            'offset_x': 0.0,
            'offset_y': 0.0
        }
        
        if os.path.exists(self.GRID_CONFIG_FILE):
            try:
                with open(self.GRID_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Support both old (single scale) and new (scale_x/scale_y) formats
                    if 'scale_x' in config:
                        return config
                    else:
                        # Legacy format: convert single scale to scale_x/scale_y
                        scale = config.get('scale', 0.85)
                        return {
                            'scale_x': scale,
                            'scale_y': scale,
                            'offset_x': config.get('offset_x', 0.0),
                            'offset_y': config.get('offset_y', 0.0)
                        }
            except Exception as e:
                print(f"Warning: Could not load grid config: {e}. Using defaults.")
                return default_config
        
        return default_config
    
    def _load_tile_states(self):
        """Load tile states from shaded_tiles.json."""
        if os.path.exists(self.SHADED_TILES_FILE):
            try:
                with open(self.SHADED_TILES_FILE, 'r') as f:
                    data = json.load(f)
                    states = {}
                    for key, value in data.items():
                        tile_tuple = tuple(map(int, key.split(',')))
                        states[tile_tuple] = value
                    return states
            except Exception as e:
                print(f"Warning: Could not load tile states: {e}")
                return {}
        return {}
    
    def _draw_grid_overlay(self, frame):
        """
        Draw grid overlay on frame using saved configuration.
        
        Args:
            frame (np.ndarray): Input frame (BGR format)
        
        Returns:
            np.ndarray: Frame with grid overlay
        """
        overlay = frame.copy()
        frame_height, frame_width = frame.shape[:2]
        
        # Calculate tile dimensions
        tile_width = frame_width / self.GRID_WIDTH
        tile_height = frame_height / self.GRID_HEIGHT
        
        # Apply scale and offset from config
        scale_x = self.grid_config.get('scale_x', 0.85)
        scale_y = self.grid_config.get('scale_y', 0.85)
        offset_x = self.grid_config.get('offset_x', 0.0)
        offset_y = self.grid_config.get('offset_y', 0.0)
        
        scaled_tile_width = tile_width * scale_x
        scaled_tile_height = tile_height * scale_y
        
        # Draw shaded tiles (filled rectangles with state colors)
        for (tile_x, tile_y), state in self.tile_states.items():
            color = self.TILE_STATES.get(state, (0, 0, 255))
            x1 = int(offset_x + tile_x * scaled_tile_width)
            y1 = int(offset_y + tile_y * scaled_tile_height)
            x2 = int(offset_x + (tile_x + 1) * scaled_tile_width)
            y2 = int(offset_y + (tile_y + 1) * scaled_tile_height)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        
        # Draw vertical lines
        for col in range(self.GRID_WIDTH + 1):
            x = int(offset_x + col * scaled_tile_width)
            if 0 <= x < frame_width:
                cv2.line(overlay, (x, 0), (x, frame_height), (0, 255, 0), 1)
        
        # Draw horizontal lines
        for row in range(self.GRID_HEIGHT + 1):
            y = int(offset_y + row * scaled_tile_height)
            if 0 <= y < frame_height:
                cv2.line(overlay, (0, y), (frame_width, y), (0, 255, 0), 1)
        
        # Blend with original frame (33% opacity)
        result = cv2.addWeighted(overlay, 0.33, frame, 0.67, 0)
        return result
    
    def update_window_rect(self):
        """Get the current window rectangle (x, y, width, height)."""
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            left, top, right, bottom = rect
            self.window_rect = {
                'left': left,
                'top': top,
                'width': right - left,
                'height': bottom - top
            }
            print(f"Window dimensions: {self.window_rect['width']}x{self.window_rect['height']}")
        except Exception as e:
            print(f"Error getting window rect: {e}")
            self.window_rect = None
    
    def capture_frame(self):
        """
        Capture a single frame from the selected window.
        
        Returns:
            np.ndarray: Frame as BGR image, or None if capture failed
        """
        if not self.window_rect:
            return None
        
        try:
            # Try to bring window to foreground (not critical if it fails)
            try:
                win32gui.SetForegroundWindow(self.hwnd)
            except Exception:
                # Silently ignore - capture can still work without this
                pass
            
            # Capture using mss
            monitor = {
                'left': self.window_rect['left'],
                'top': self.window_rect['top'],
                'width': self.window_rect['width'],
                'height': self.window_rect['height']
            }
            
            screenshot = self.sct.grab(monitor)
            frame = np.array(screenshot)
            
            # Convert RGBA to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            
            return frame
        except Exception as e:
            print(f"Error capturing frame: {e}")
            # Try to update window rect in case it moved
            self.update_window_rect()
            return None
    
    def start_recording(self, fps=30):
        """
        Start recording frames from the window with grid overlay.
        
        Args:
            fps (int): Frames per second for recording
        """
        if not self.window_rect:
            print("Error: Could not get window dimensions")
            return None
            
        print(f"\nStarting recording at {fps} FPS...")
        print("-" * 80)
        
        self.recording = True
        frame_count = 0
        window_name = f"LIVE RECORDING - {self.window_rect.get('width', 'unknown')}x{self.window_rect.get('height', 'unknown')}"
        
        # Create window
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        
        while self.recording:
            frame = self.capture_frame()
            
            if frame is None:
                print("Failed to capture frame. Stopping...")
                break
            
            # Apply tile overlay with saved transformations
            display_frame = frame.copy()
            display_frame = self._draw_grid_overlay(display_frame)
            
            # Save frame with overlay to video
            self.frames.append(display_frame)
            frame_count += 1
            
            # Scale frame to 50% for display
            display_frame = cv2.resize(display_frame, None, fx=0.5, fy=0.5)
            
            # Convert BGR to RGB for correct colors
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Display the frame in popup window
            cv2.imshow(window_name, display_frame)
            
            # Wait for frame duration or Ctrl+C to stop
            key = cv2.waitKey(int(1000 / fps)) & 0xFF
            if key == ord('q'):
                print("Recording stopped by user (q pressed).")
                self.recording = False
        
        cv2.destroyAllWindows()
        return self.frames
    
    def save_video(self, filename=None):
        """
        Save all recorded frames as a video file.
        
        Args:
            filename (str): Output video filename (optional)
        
        Returns:
            str: Path to saved video file
        """
        if not self.frames:
            print("No frames to save.")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Get frame dimensions
        height, width = self.frames[0].shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # type: ignore
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))
        
        print(f"\nSaving video to {output_path}...")
        for frame in self.frames:
            out.write(frame)
        
        out.release()
        print(f"Video saved successfully: {output_path}")
        
        return output_path
    
    def clear_frames(self):
        """Clear recorded frames from memory."""
        self.frames = []
        print("Frames cleared from memory.")


def main():
    """Main function to run the window recorder."""
    print("=" * 80)
    print("WINDOW RECORDER - VISION MODULE")
    print("=" * 80)
    
    # Let user select a window
    hwnd, title = list_and_select_window()
    
    if not hwnd:
        print("No window selected. Exiting.")
        return
    
    # Create recorder and start recording
    recorder = WindowRecorder(hwnd)
    
    try:
        frames = recorder.start_recording(fps=30)
        
        if frames:
            # Ask if user wants to save the recording
            save = input("\nSave recording as video? (y/n): ").lower()
            if save == 'y':
                recorder.save_video()
    
    except KeyboardInterrupt:
        print("\n\nRecording interrupted by user.")
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
