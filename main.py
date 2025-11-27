import cv2
import time
import os
from src.capture import WindowCapture
from src.vision import get_user_elixir, ElixirTracker
from src.detector import CardDetector
from src.tracker import OpponentState
from src.config import RESIZE_WIDTH, RESIZE_HEIGHT

def main():
    print("Initializing Clash Royale Match Analyzer...")
    
    # Initialize Modules
    cap = WindowCapture()
    elixir_tracker = ElixirTracker()
    card_detector = CardDetector()
    opponent_state = OpponentState()
    
    print("Waiting for window...")
    while not cap.hwnd:
        cap.find_window()
        time.sleep(1)
        
    print("Window found! Starting loop...")
    
    try:
        while True:
            loop_start = time.time()
            
            # 1. Capture
            frame = cap.get_screenshot()
            if frame is None:
                print("Failed to capture frame.")
                time.sleep(0.5)
                continue
                
            # 2. Vision (User Elixir)
            user_elixir = get_user_elixir(frame)
            
            # 3. Update Opponent Elixir (Time-based)
            elixir_tracker.update()
            
            # 4. Detect Cards
            detected = card_detector.detect(frame)
            for card in detected:
                # Assume average cost of 4 for now if we don't have a cost DB
                # Ideally, CardDetector should return (name, cost) or we look it up
                cost = 4 
                elixir_tracker.spend_elixir(cost)
                opponent_state.on_card_played(card, cost)
                print(f"!!! Opponent played {card} (Est. Elixir: {elixir_tracker.opponent_elixir:.1f})")

            # 5. Display Dashboard (Console for now)
            # We can also draw on the frame
            display_frame = frame.copy()
            
            # Draw info
            cv2.putText(display_frame, f"My Elixir: {user_elixir}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.putText(display_frame, f"Opp Elixir: {elixir_tracker.opponent_elixir:.1f}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show Hand
            hand_str = "Hand: " + ", ".join(opponent_state.hand)
            cv2.putText(display_frame, hand_str, (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Clash Royale Analyzer", display_frame)
            
            # FPS Control
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # Optional: limit FPS
            # time.sleep(0.05) 
            
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
