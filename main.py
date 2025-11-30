"""
Full Overlay - Combined Elixir Tracking + Grid Overlay
Combines functionality from elixi_tracker and tile_overlay branches.
"""

import cv2
import sys
import os
import time
import win32gui

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.capture import WindowCapture
from src.config import ELIXIR_BAR_ROI
from src.vision import get_user_elixir, ElixirTracker, GridOverlay
from src.events import GameEvents, apply_event_to_overlay


def main():
    """Main application combining elixir tracking and grid overlay."""
    
    print("=" * 80)
    print("FULL OVERLAY - Elixir Tracking + Grid Overlay")
    print("=" * 80)
    print("\nInitializing...")
    
    # Find window
    cap = WindowCapture()
    
    while not cap.hwnd:
        cap.find_window()
        if not cap.hwnd:
            print("Waiting for window 'Android Device'...")
            time.sleep(1)
    
    print(f"[OK] Found window: Android Device")
    
    # Get frame to initialize grid overlay
    screenshot = cap.get_screenshot()
    if screenshot is None:
        print("Error: Could not capture initial frame")
        return
    
    frame_h, frame_w = screenshot.shape[:2]
    print(f"[OK] Frame size: {frame_w}x{frame_h}")
    
    # Initialize grid overlay and elixir tracker
    grid = GridOverlay(frame_w, frame_h)
    tracker = ElixirTracker()
    events = GameEvents()
    
    print("[OK] Grid overlay initialized")
    print("[OK] Elixir tracker initialized")
    print("[OK] Game events initialized")
    print("\n" + "-" * 80)
    print("Starting live overlay. Press 'q' to quit.")
    events.print_help()
    print("-" * 80 + "\n")
    
    frame_count = 0
    
    while True:
        screenshot = cap.get_screenshot()
        if screenshot is None:
            continue
        
        # Get elixir estimate
        elixir = get_user_elixir(screenshot)
        
        # Update tracker
        tracker.update()
        
        # Apply event-based tile state updates to overlay
        apply_event_to_overlay(grid, events)
        
        # Apply grid overlay
        display_frame = grid.draw_overlay(screenshot)
        
        # Draw elixir bar ROI bounding box (green)
        x, y, w, h = ELIXIR_BAR_ROI
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
        # Display ROI coordinates for reference
        cv2.putText(display_frame, f"ROI: ({x}, {y}, {w}, {h})", (x, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Add elixir info overlay
        cv2.putText(display_frame, f"Your Elixir: {elixir:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(display_frame, f"Opponent Est: {tracker.opponent_elixir:.1f}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Display
        cv2.imshow("Full Overlay", display_frame)
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Frame {frame_count} | Your Elixir: {elixir:.1f} | Opponent Est: {tracker.opponent_elixir:.1f}")
        
        # Check for quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nQuitting...")
            break
        elif key != 255:  # 255 means no key pressed
            char = chr(key)
            if char.lower() == 'x':
                events.reset_to_original()
                print("[OK] All tiles reset to original state")
            else:
                events.trigger_event(char)
    
    cv2.destroyAllWindows()
    print("Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()
