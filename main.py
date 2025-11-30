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
    
    if settings.is_grid_enabled():
        systems['grid'] = GridOverlay(frame_width, frame_height)
        systems['events'] = GameEvents()
        print("[OK] Grid overlay initialized")
        print_grid_info(systems['grid'])
    
    if settings.is_elixir_enabled():
        systems['elixir'] = ElixirDisplay()
        print("[OK] Elixir tracking initialized")
    
    if settings.is_towers_enabled() and TOWER_DETECTION_AVAILABLE:
        try:
            systems['towers'] = TowerDisplay(frame_width, frame_height)
            print("[OK] Tower detection initialized")
        except Exception as e:
            print(f"[ERROR] Tower detection failed: {e}")
            import traceback
            traceback.print_exc()
            systems['towers'] = None
    
    return systems


def print_grid_info(grid):
    """Print grid configuration information"""
    print("\n" + "=" * 80)
    print("GRID INITIALIZATION VERIFICATION:")
    print("=" * 80)
    print("Grid Configuration (from display_config.json):")
    print(f"  scale_x: {grid.grid_config.get('scale_x')}")
    print(f"  scale_y: {grid.grid_config.get('scale_y')}")
    print(f"  offset_x: {grid.grid_config.get('offset_x')}")
    print(f"  offset_y: {grid.grid_config.get('offset_y')}")
    
    tile_state_counts = {}
    for tile_coord, tile_state_value in grid.tile_states.items():
        tile_state_counts[tile_state_value] = tile_state_counts.get(tile_state_value, 0) + 1
    
    print(f"\nTile States Loaded from JSON (shaded_tiles.json):")
    print(f"  Total tiles: {len(grid.tile_states)}")
    print(f"  Breakdown:")
    for state_name in ['red', 'leftEnemyDown', 'rightEnemyDown', 'leftFriendlyDown', 'rightFriendlyDown', 'empty']:
        count = tile_state_counts.get(state_name, 0)
        if count > 0:
            print(f"    {state_name}: {count}")
    print("=" * 80 + "\n")


def main():
    """Main application loop with settings window"""
    
    print("=" * 80)
    print("CLASH ROYALE OVERLAY SYSTEM")
    print("=" * 80)
    print("\nInitializing Settings Window...")
    
    # Initialize settings window (non-blocking)
    settings = SettingsWindow()
    print("[OK] Settings window created")
    
    print("\nInitializing Capture...")
    
    # Find and connect to game window
    cap = WindowCapture()
    while not cap.hwnd:
        cap.find_window()
        if not cap.hwnd:
            print("Waiting for window 'Android Device'...")
            time.sleep(1)
    
    print(f"[OK] Found window: Android Device")
    
    # Get initial frame
    screenshot = cap.get_screenshot()
    if screenshot is None:
        print("Error: Could not capture initial frame")
        return
    
    frame_h, frame_w = screenshot.shape[:2]
    print(f"[OK] Frame size: {frame_w}x{frame_h}")
    
    # Initialize all systems
    systems = initialize_systems(frame_w, frame_h, settings)
    
    # Print feature status
    print("\n" + "-" * 80)
    print("FEATURES ENABLED:")
    print(f"  Grid Overlay: {settings.is_grid_enabled()}")
    print(f"  Elixir Tracking: {settings.is_elixir_enabled()}")
    print(f"  Tower Detection: {settings.is_towers_enabled() and systems['towers'] is not None}")
    print("-" * 80)
    
    if systems['events']:
        systems['events'].print_help()
    
    print("Press 'q' to quit | Settings window shows toggles for all features")
    print("-" * 80 + "\n")
    
    frame_count = 0
    last_state = {
        'grid': settings.is_grid_enabled(),
        'elixir': settings.is_elixir_enabled(),
        'towers': settings.is_towers_enabled()
    }
    
    try:
        while True:
            # Update settings window
            settings.update_window()
            
            # Check if feature states have changed
            current_state = {
                'grid': settings.is_grid_enabled(),
                'elixir': settings.is_elixir_enabled(),
                'towers': settings.is_towers_enabled()
            }
            
            if current_state != last_state:
                print("\n[INFO] Feature state changed, reinitializing systems...")
                systems = initialize_systems(frame_w, frame_h, settings)
                print(f"  Grid: {current_state['grid']}")
                print(f"  Elixir: {current_state['elixir']}")
                print(f"  Towers: {current_state['towers']}")
                last_state = current_state.copy()
            
            screenshot = cap.get_screenshot()
            if screenshot is None:
                continue
            
            display_frame = screenshot.copy()
            
            # Apply grid overlay
            if systems['grid']:
                apply_event_to_overlay(systems['grid'], systems['events'])
                display_frame = systems['grid'].draw_overlay(display_frame)
            
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
            if frame_count % 30 == 0 and settings.is_elixir_enabled():
                print(f"Frame {frame_count}")
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuitting...")
                break
            elif key != 255 and systems['events']:  # 255 means no key pressed
                char = chr(key)
                if char.lower() == 'x':
                    systems['events'].reset_to_original()
                    print("[OK] All tiles reset to original state")
                else:
                    systems['events'].trigger_event(char)
    
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
