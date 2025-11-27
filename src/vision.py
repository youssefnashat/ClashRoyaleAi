import cv2
import numpy as np
import time
from .config import (
    ELIXIR_BAR_ROI, ELIXIR_RECOVERY_RATE_SINGLE, ELIXIR_RECOVERY_RATE_DOUBLE,
    ELIXIR_MAX, ELIXIR_START, PURPLE_LOWER, PURPLE_UPPER
)

def get_user_elixir(frame):
    """
    Estimates user elixir based on purple pixel count in the elixir bar ROI.
    Returns a float between 0.0 and 10.0.
    """
    if frame is None:
        return 0.0

    # 1. Define ROI (Imported from config)
    x, y, w, h = ELIXIR_BAR_ROI
    
    # Safety check for frame bounds
    if y+h > frame.shape[0] or x+w > frame.shape[1]:
        # ROI is outside frame, return 0 or log warning
        return 0.0

    roi = frame[y:y+h, x:x+w]
    
    # 2. Convert to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # 3. Create Mask for Purple
    # PURPLE_LOWER/UPPER are defined in config.py
    mask = cv2.inRange(hsv, PURPLE_LOWER, PURPLE_UPPER)
    
    # 4. Count Purple Pixels
    purple_pixels = cv2.countNonZero(mask)
    total_pixels = w * h
    
    if total_pixels == 0:
        return 0.0
        
    # 5. Calculate Elixir
    # We assume the ROI perfectly encapsulates the fillable area of the bar.
    percentage = purple_pixels / total_pixels
    
    # Map 0-100% to 0-10 Elixir
    elixir = percentage * 10.0
    
    return round(elixir, 1)

class ElixirTracker:
    """
    Tracks the opponent's estimated elixir.
    """
    def __init__(self):
        self.opponent_elixir = ELIXIR_START
        self.last_update = time.time()
        self.double_elixir_mode = False 

    def update(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        
        rate = ELIXIR_RECOVERY_RATE_DOUBLE if self.double_elixir_mode else ELIXIR_RECOVERY_RATE_SINGLE
        
        self.opponent_elixir += rate * dt
        if self.opponent_elixir > ELIXIR_MAX:
            self.opponent_elixir = ELIXIR_MAX

    def spend_elixir(self, amount):
        self.opponent_elixir -= amount
