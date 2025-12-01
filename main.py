import cv2
import time
import sys
import os
import threading
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.capture import WindowCapture
from src.vision import GridOverlay
from src.events import GameEvents, apply_event_to_overlay
from src.config import ENABLE_TOWER_DETECTION, ENABLE_GRID_OVERLAY, ENABLE_ELIXIR_TRACKING
from src.elixir_tracker_module import ElixirDisplay
from src.settings_window import SettingsWindow
from src.detector import RoboflowDetector
from src.hand_tracker import HandTracker

# Conditional imports
try:
    from src.tower_display import TowerDisplay
    TOWER_DETECTION_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Tower detection unavailable: {e}")
    TOWER_DETECTION_AVAILABLE = False


# Global state for threaded detection
latest_cards = ["Unknown"] * 4
is_detecting = False

def detect_cards_thread(tracker, frame):
    global latest_cards, is_detecting
    try:
        # Run detection (this takes time)
        cards = tracker.get_hand_cards(frame)
        latest_cards = cards
        print(f"\n[HAND]: [ 1: {cards[0]} ] [ 2: {cards[1]} ] [ 3: {cards[2]} ] [ 4: {cards[3]} ]")
    except Exception as e:
        print(f"Detection error: {e}")
    finally:
        is_detecting = False


def initialize_systems(frame_width, frame_height, settings):
    """Initialize enabled subsystems based on settings window state"""
    systems = {
        'grid': None,
        'events': None,
        'elixir': None,
        'towers': None,
        'hand': None
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

    # Initialize Hand Tracker (Always on for now, or could add a setting)
    try:
        detector = RoboflowDetector()
        systems['hand'] = HandTracker(detector)
        print("[OK] Hand Tracker initialized")
    except Exception as e:
        print(f"[WARNING] Hand Tracker failed to init: {e}")
        systems['hand'] = None
    
    return systems


def main():
    """Main application loop with settings window"""
    global is_detecting, latest_cards
    
    print("DPI Mode: Per-Monitor Aware (2)")
    print("="*80)
    print("CLASH ROYALE AI - ROBOFLOW EDITION")
    print("="*80)
    
    # Initialize settings window (non-blocking)
    settings = SettingsWindow()
    
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
        print("Error: Could not capture screenshot.")
        return
    
    frame_h, frame_w = screenshot.shape[:2]
    print(f"[OK] Frame size: {frame_w}x{frame_h}")
    
    # Initialize all systems
    systems = initialize_systems(frame_w, frame_h, settings)
    
    last_card_check = time.time()
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
                # Re-init systems if needed (though ideally we'd just toggle them)
                # For now, we'll just update the existing systems or re-create if simple
                # Re-creating might be heavy, but let's stick to the pattern for now
                # Actually, let's just update the flags we can, or re-init if critical
                # The original code re-initialized. Let's keep it safe.
                # BUT, re-initializing HandTracker is expensive (loads model). 
                # Let's preserve hand tracker if possible.
                old_hand = systems.get('hand')
                systems = initialize_systems(frame_w, frame_h, settings)
                if old_hand:
                    systems['hand'] = old_hand # Reuse loaded model
                last_state = current_state.copy()
            
            screenshot = cap.get_screenshot()
            if screenshot is None:
                continue
            
            display_frame = screenshot.copy()
            
            # --- Hand Card Detection (Threaded) ---
            if systems['hand'] and (time.time() - last_card_check > 2.0) and not is_detecting:
                is_detecting = True
                last_card_check = time.time()
                # Start detection in background thread
                t = threading.Thread(target=detect_cards_thread, args=(systems['hand'], screenshot.copy()))
                t.daemon = True 
                t.start()

            # --- Draw Overlays ---

            # Apply grid overlay with opacity
            if systems['grid']:
                apply_event_to_overlay(systems['grid'], systems['events'])
                grid_frame = systems['grid'].draw_overlay(display_frame.copy())
                opacity = settings.get_grid_opacity()
                # Blend grid frame with original based on opacity
                display_frame = cv2.addWeighted(grid_frame, opacity, display_frame, 1 - opacity, 0)
            
            # Apply tower detection
            if systems['towers']:
                systems['towers'].update()
                display_frame, _ = systems['towers'].process_frame(display_frame)
            
            # Apply elixir tracking
            if systems['elixir']:
                systems['elixir'].update()
                display_frame, elixir = systems['elixir'].render(display_frame, screenshot)
            
            # Apply Hand Tracker Overlay
            if systems['hand']:
                display_frame = systems['hand'].get_debug_frame(display_frame)

            # Display frame
            cv2.imshow("Clash Royale AI Overlay", display_frame)
            
            # Frame counter and logging
            frame_count += 1
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
            elif key != 255: # Key pressed
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
