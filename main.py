"""
Clash Royale Overlay System
Modular architecture with optional features:
- Grid Overlay (tile state visualization)
- Elixir Tracking (ROI-based elixir detection)
- Tower Detection (ML-based princess tower detection)
"""

import cv2
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.capture import WindowCapture
from src.vision import GridOverlay
from src.events import GameEvents, apply_event_to_overlay
from src.config import ENABLE_TOWER_DETECTION, ENABLE_GRID_OVERLAY, ENABLE_ELIXIR_TRACKING
from src.elixir_tracker_module import ElixirDisplay
from src.settings_window import SettingsWindow

# Conditional imports
try:
    from src.tower_display import TowerDisplay
    TOWER_DETECTION_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Tower detection unavailable: {e}")
    TOWER_DETECTION_AVAILABLE = False


def initialize_systems(frame_width, frame_height, settings):
    """Initialize enabled subsystems based on settings window state"""
    systems = {
        'grid': None,
        'events': None,
        'elixir': None,
        'towers': None,
    }
    
    # Always initialize grid (opacity controls visibility)
    systems['grid'] = GridOverlay(frame_width, frame_height)
    systems['events'] = GameEvents()
    
    if settings.is_elixir_enabled():
        systems['elixir'] = ElixirDisplay()
    
    if settings.is_towers_enabled() and TOWER_DETECTION_AVAILABLE:
        try:
            systems['towers'] = TowerDisplay(frame_width, frame_height)
        except Exception as e:
            print(f"[ERROR] Tower detection failed: {e}")
            import traceback
            traceback.print_exc()
            systems['towers'] = None
    
    return systems


def print_grid_info(grid):
    """Print grid configuration information"""
    pass


def main():
    """Main application loop with settings window"""
    
    # Initialize settings window (non-blocking)
    settings = SettingsWindow()
    
    # Find and connect to game window
    cap = WindowCapture()
    while not cap.hwnd:
        cap.find_window()
        if not cap.hwnd:
            time.sleep(1)
    
    # Get initial frame
    screenshot = cap.get_screenshot()
    if screenshot is None:
        print("Error: Could not capture initial frame")
        return
    
    frame_h, frame_w = screenshot.shape[:2]
    
    # Initialize all systems
    systems = initialize_systems(frame_w, frame_h, settings)
    
    frame_count = 0
    last_state = {
        'grid_opacity': settings.get_grid_opacity(),
        'elixir': settings.is_elixir_enabled(),
        'towers': settings.is_towers_enabled()
    }
    
    try:
        while True:
            # Update settings window
            settings.update_window()
            
            # Check if feature states have changed
            current_state = {
                'grid_opacity': settings.get_grid_opacity(),
                'elixir': settings.is_elixir_enabled(),
                'towers': settings.is_towers_enabled()
            }
            
            if current_state != last_state:
                systems = initialize_systems(frame_w, frame_h, settings)
                last_state = current_state.copy()
            
            screenshot = cap.get_screenshot()
            if screenshot is None:
                continue
            
            display_frame = screenshot.copy()
            
            # Apply grid overlay with opacity
            if systems['grid']:
                apply_event_to_overlay(systems['grid'], systems['events'])
                grid_frame = systems['grid'].draw_overlay(display_frame.copy())
                opacity = settings.get_grid_opacity()
                # Blend grid frame with original based on opacity (100% = fully opaque grid)
                display_frame = cv2.addWeighted(grid_frame, opacity, display_frame, 1 - opacity, 0)
            
            # Apply tower detection
            if systems['towers']:
                systems['towers'].update()
                display_frame, _ = systems['towers'].process_frame(display_frame)
            
            # Apply elixir tracking
            if systems['elixir']:
                systems['elixir'].update()
                display_frame, elixir = systems['elixir'].render(display_frame, screenshot)
            
            # Display frame
            cv2.imshow("Clash Royale Overlay", display_frame)
            
            # Frame counter and logging
            frame_count += 1
            
            # Handle keyboard input (quit only, event triggers currently unassigned)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            settings.close()
        except:
            pass
        cv2.destroyAllWindows()
        print("Done!")


if __name__ == "__main__":
    main()
