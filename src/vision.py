import cv2
import numpy as np
import time
from .config import (
    ELIXIR_BAR_ROI, ELIXIR_RECOVERY_RATE_SINGLE, ELIXIR_RECOVERY_RATE_DOUBLE,
    ELIXIR_MAX, ELIXIR_START, PURPLE_LOWER, PURPLE_UPPER, ELIXIR_SEGMENT_THRESHOLD
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
    
    # 5. Calculate Elixir using Segment Logic
    # User Request: First box is double the length of the others.
    # Total units = 2 (first) + 9 (others) = 11 units.
    unit_width = w / 11.0
    elixir_count = 0
    
    for i in range(10):
        # Define segment boundaries
        if i == 0:
            start_x = 0
            end_x = int(2 * unit_width)
        else:
            # i=1 starts at 2 units, i=2 starts at 3 units, etc.
            start_x = int((2 + (i - 1)) * unit_width)
            end_x = int((2 + i) * unit_width)
            
        # Clamp end_x to width to avoid rounding errors
        if i == 9:
            end_x = w
        
        # Extract segment mask
        segment_mask = mask[:, start_x:end_x]
        
        # Count pixels in this segment
        seg_purple = cv2.countNonZero(segment_mask)
        seg_w = end_x - start_x
        seg_total = seg_w * h
        
        if seg_total > 0:
            ratio = seg_purple / seg_total
            
            # User Request: First box needs to be "fully filled" to count.
            # It often shows 1 when empty due to noise/numbers.
            # So we use a stricter threshold for the first segment.
            threshold = 0.85 if i == 0 else ELIXIR_SEGMENT_THRESHOLD
            
            if ratio >= threshold:
                elixir_count += 1
                
    return elixir_count

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
