"""
Vision module for recording and capturing frames from selected window.
This module records video frames from the window selected by windowing.py
and provides frame-by-frame analysis capabilities.
"""

import cv2
import numpy as np
import mss
import win32gui  # type: ignore
import win32con  # type: ignore
from datetime import datetime
import os
from windowing import list_and_select_window


class WindowRecorder:
    """Records video frames from a selected window."""
    
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
        Start recording frames from the window.
        
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
            
            self.frames.append(frame)
            frame_count += 1
            
            # Scale frame to 50% for display
            display_frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
            
            # Convert BGR to RGB for correct colors
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Display the frame in popup window
            cv2.imshow(window_name, display_frame)
            
            # Update display every frame (no keyboard input)
            cv2.waitKey(int(1000 / fps))
        
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
