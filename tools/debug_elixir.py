import cv2
import numpy as np
import sys
import os
import time

# Add the project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.capture import WindowCapture
from src.config import ELIXIR_BAR_ROI, PURPLE_LOWER, PURPLE_UPPER
from src.vision import get_user_elixir

def debug_elixir_view():
    cap = WindowCapture()
    print("Debug Mode: ON. Press 'q' to quit.")
    
    # Wait for window
    while not cap.hwnd:
        cap.find_window()
        if not cap.hwnd:
            print("Waiting for window...")
            time.sleep(1)

    while True:
        screenshot = cap.get_screenshot()
        if screenshot is None:
            continue

        # 1. Visualize the ROI (Draw a rectangle on the main screen)
        # ROI is (x, y, w, h)
        x, y, w, h = ELIXIR_BAR_ROI
        
        # Debug: Check bounds
        fh, fw = screenshot.shape[:2]
        if y + h > fh or x + w > fw:
            print(f"\rWarning: ROI {ELIXIR_BAR_ROI} is out of bounds for frame {fw}x{fh}", end="")
            # Draw red box to show where we tried to look
            debug_frame = screenshot.copy()
            # Draw visible part of ROI if possible, or just the frame border
            cv2.rectangle(debug_frame, (0, 0), (fw-1, fh-1), (0, 0, 255), 5)
            cv2.imshow("Main View (Green Box = ROI)", debug_frame)
            if cv2.waitKey(1) == ord('q'): break
            time.sleep(2) # Prevent spam
            continue

        # Draw green box where we THINK the elixir is
        debug_frame = screenshot.copy()
        cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 2. Extract and Mask
        # Crop to the ROI
        roi = screenshot[y:y+h, x:x+w]
        
        if roi.size == 0:
            print("\rWarning: Empty ROI extracted", end="")
            continue
            
        # Convert to HSV and Mask (just for visualization)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(PURPLE_LOWER), np.array(PURPLE_UPPER))

        # 3. Calculate Value using the ACTUAL function
        elixir_val = get_user_elixir(screenshot)
        
        # 4. Display Everything
        cv2.imshow("Main View (Green Box = ROI)", debug_frame)
        cv2.imshow("Elixir Mask (White = Detected)", mask)
        
        # Add text to the debug frame
        cv2.putText(debug_frame, f"Elixir: {elixir_val}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("Main View (Green Box = ROI)", debug_frame)

        print(f"\rElixir Estimate: {elixir_val}", end="")

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    debug_elixir_view()