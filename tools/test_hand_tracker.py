import cv2
import sys
import os
import time

# Add project root to path so we can import src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.capture import WindowCapture
from src.hand_tracker import HandTracker
from src.detector import RoboflowDetector

def main():
    print("=" * 60)
    print("Hand Tracker Test Tool (Dual Model)")
    print("=" * 60)
    
    # Initialize components
    print("Initializing Detector...")
    try:
        detector = RoboflowDetector()
    except Exception as e:
        print(f"Error initializing detector: {e}")
        return

    print("Initializing HandTracker...")
    tracker = HandTracker(detector)
    
    print("Initializing WindowCapture...")
    cap = WindowCapture()
    
    # Wait for window
    while not cap.hwnd:
        cap.find_window()
        if not cap.hwnd:
            print("Waiting for window 'Android Device'...")
            time.sleep(1)
            
    print(f"[OK] Found window: Android Device")
    
    print("\nStarting test loop...")
    print("Press 'q' to quit")
    print("-" * 60)
    
    last_check_time = 0
    
    while True:
        frame = cap.get_screenshot()
        if frame is None:
            time.sleep(0.1)
            continue
            
        current_time = time.time()
        
        # Draw debug visualization
        debug_frame = tracker.get_debug_frame(frame)
        
        # Identify slots every 2 seconds
        if current_time - last_check_time >= 2.0:
            print("\nIdentifying hand cards...")
            cards = tracker.get_hand_cards(frame)
            
            # Print result
            hand_str = " ".join([f"[ {i+1}: {card} ]" for i, card in enumerate(cards)])
            print(f"[HAND]: {hand_str}")
            
            last_check_time = current_time
            
        # Show preview
        cv2.imshow("Hand Tracker Test", debug_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cv2.destroyAllWindows()
    print("\nTest finished.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\nError: {e}")
        cv2.destroyAllWindows()
