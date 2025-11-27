import cv2
import os
import time
import sys

# Add parent dir to path to import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capture import WindowCapture
from src.config import ARENA_ROI

def main():
    print("Asset Capture Tool")
    print("Press 's' to save the current Arena ROI as a template candidate.")
    print("Press 'q' to quit.")
    
    cap = WindowCapture()
    while not cap.hwnd:
        cap.find_window()
        time.sleep(1)
        
    save_dir = "assets/cards_raw"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    count = 0
    
    while True:
        frame = cap.get_screenshot()
        if frame is None:
            print("Waiting for window...")
            time.sleep(1)
            continue
            
        x, y, w, h = ARENA_ROI
        roi = frame[y:y+h, x:x+w]
        
        cv2.imshow("Arena ROI", roi)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = os.path.join(save_dir, f"capture_{count}.png")
            cv2.imwrite(filename, roi)
            print(f"Saved {filename}")
            count += 1
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
