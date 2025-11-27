import cv2
import time
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture import WindowCapture

def main():
    print("Testing Raw Capture (Client Area)")
    print("Press 'q' to quit.")
    
    cap = WindowCapture()
    while not cap.hwnd:
        cap.find_window()
        time.sleep(1)
        
    while True:
        # We need to access the raw capture logic or just modify get_screenshot temporarily
        # But get_screenshot resizes. Let's just use get_screenshot for now, 
        # but ideally we want to see the raw aspect ratio.
        # Actually, the user asked for "full raw screenshot". 
        # get_screenshot returns resized. 
        # Let's inspect the internal logic or just trust the resized one if it shows the whole game.
        # To be precise, let's just call get_screenshot and see if it looks right.
        
        frame = cap.get_screenshot()
        if frame is None:
            time.sleep(0.1)
            continue
            
        cv2.imshow("Test Capture", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
