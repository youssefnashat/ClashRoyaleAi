import cv2
import time
import numpy as np
import threading
from src.capture import WindowCapture
from src.vision import GridOverlay, get_user_elixir, ElixirTracker
from src.events import GameEvents
from src.config import WINDOW_NAME_PATTERNS, RESIZE_WIDTH, RESIZE_HEIGHT, ELIXIR_BAR_ROI
from src.detector import RoboflowDetector
from src.hand_tracker import HandTracker

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

def main():
    global is_detecting, latest_cards
    
    print("DPI Mode: Per-Monitor Aware (2)")
    print("="*80)
    print("FULL OVERLAY - Elixir Tracking + Grid + Hand Cards")
    print("="*80)
    print("\nInitializing...")
    
    # Initialize Window Capture
    wincap = WindowCapture()
    
    # Wait for window
    while True:
        if wincap.hwnd:
            break
        else:
            print("Waiting for window 'Android Device'...")
            time.sleep(1)
    
    print(f"[OK] Found window: Android Device")
    
    # Get frame to initialize grid overlay
    screenshot = wincap.get_screenshot()
    if screenshot is None:
        print("Error: Could not capture screenshot.")
        return
    
    frame_h, frame_w = screenshot.shape[:2]
    print(f"[OK] Frame size: {frame_w}x{frame_h}")
    
    # Initialize components
    grid = GridOverlay(frame_w, frame_h)
    elixir_tracker = ElixirTracker()
    events = GameEvents()
    
    # Initialize Hand Tracker
    try:
        detector = RoboflowDetector()
        hand_tracker = HandTracker(detector)
        print("[OK] Hand Tracker initialized")
    except Exception as e:
        print(f"[WARNING] Hand Tracker failed to init: {e}")
        hand_tracker = None
    
    print("[OK] Grid overlay initialized")
    print("[OK] Elixir tracker initialized")
    print("[OK] Game events initialized")
    print("\n" + "-" * 80)
    print("Starting live overlay. Press 'q' to quit.")
    events.print_help()
    print("-" * 80 + "\n")
    
    last_card_check = time.time()
    frame_count = 0
    
    while True:
        # 1. Capture Frame
        screenshot = wincap.get_screenshot()
        if screenshot is None:
            continue
        
        # 2. Process Elixir
        user_elixir = get_user_elixir(screenshot)
        elixir_tracker.update()
        
        # 3. Process Hand Cards (Threaded)
        # Check every 2 seconds, but only if not currently detecting
        if hand_tracker and (time.time() - last_card_check > 2.0) and not is_detecting:
            is_detecting = True
            last_card_check = time.time()
            # Start detection in background thread
            t = threading.Thread(target=detect_cards_thread, args=(hand_tracker, screenshot.copy()))
            t.daemon = True # Ensure thread dies if main program quits
            t.start()
        
        # 4. Draw Overlays
        # Grid Overlay
        final_frame = grid.draw_overlay(screenshot)
        
        # Hand Tracker Overlay (Draws the *latest* known cards/boxes)
        # Note: get_debug_frame might need to know the cards? 
        # Actually HandTracker.get_debug_frame just draws the boxes. 
        # If we want to show labels, we might need to pass them, but for now it draws the boxes.
        if hand_tracker:
            final_frame = hand_tracker.get_debug_frame(final_frame)
        
        # Elixir Info & UI (Restored to Top-Left)
        est_elixir = elixir_tracker.opponent_elixir
        
        # Draw Elixir Bar ROI (Green Box)
        ex, ey, ew, eh = ELIXIR_BAR_ROI
        cv2.rectangle(final_frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        
        # Draw Text Info at Top Left
        cv2.putText(final_frame, f"Your Elixir: {user_elixir:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(final_frame, f"Opponent Est: {est_elixir:.1f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Print status to terminal periodically
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Frame {frame_count} | Your Elixir: {user_elixir:.1f} | Opponent Est: {est_elixir:.1f}")
            
        # 5. Display
        cv2.imshow("Clash Royale AI Overlay", final_frame)
        
        # 6. Input Handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key != 255: # Key pressed
            char = chr(key)
            if char.lower() == 'x':
                events.reset_to_original()
                print("[OK] All tiles reset to original state")
            else:
                events.trigger_event(char)
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
