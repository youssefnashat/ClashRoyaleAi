import cv2
import numpy as np
import sys
import os

# Add the project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.capture import WindowCapture
from src.config import ELIXIR_BAR_ROI, PURPLE_LOWER, PURPLE_UPPER

def debug_elixir_view():
    cap = WindowCapture()
    print("Debug Mode: ON. Press 'q' to quit.")
    
    # Wait for window
    while not cap.hwnd:
        cap.find_window()
        if not cap.hwnd:
            print("Waiting for window...")
            cv2.waitKey(1000)

    while True:
        screenshot = cap.get_screenshot()
        if screenshot is None:
            continue

        # 2. Extract and Mask
        # Crop to the ROI
        roi = screenshot[y:y+h, x:x+w]
        
        if roi.size == 0:
            print("\rWarning: Empty ROI extracted", end="")
            continue
            
        # Convert to HSV and Mask
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(PURPLE_LOWER), np.array(PURPLE_UPPER))

        # 3. Calculate Value
        pixel_count = cv2.countNonZero(mask)
        total_pixels = w * h
        if total_pixels > 0:
            percentage = pixel_count / total_pixels
        else:
            percentage = 0
            
        elixir_val = percentage * 10  # Rough estimate logic

        # 4. Display Everything
        cv2.imshow("Main View (Green Box = ROI)", debug_frame)
        cv2.imshow("Elixir Mask (White = Detected)", mask)

        print(f"\rElixir Estimate: {elixir_val:.2f} | Pixels: {pixel_count}", end="")

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    debug_elixir_view()