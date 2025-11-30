import cv2
import numpy as np
import time
import json
import os
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
            threshold = 0.75 if i == 0 else ELIXIR_SEGMENT_THRESHOLD
            
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


class GridOverlay:
    """
    18x32 tile grid overlay for Clash Royale arena with persistent configuration.
    Loads grid scale and tile states from JSON files.
    """
    
    GRID_WIDTH = 18
    GRID_HEIGHT = 32
    DISPLAY_CONFIG_FILE = "display_config.json"
    SHADED_TILES_FILE = "shaded_tiles.json"
    
    # Tile states with BGR colors
    TILE_STATES = {
        'red': (0, 0, 255),
        'leftEnemyDown': (0, 255, 0),
        'rightEnemyDown': (255, 0, 0),
        'leftFriendlyDown': (0, 255, 255),
        'rightFriendlyDown': (255, 0, 255),
        'empty': None  # Transparent, not drawn
    }
    
    def __init__(self, frame_width, frame_height):
        """Initialize grid overlay with frame dimensions."""
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.tile_width = frame_width / self.GRID_WIDTH
        self.tile_height = frame_height / self.GRID_HEIGHT
        
        # Load configuration and tile states from JSON
        self.grid_config = self._load_grid_config()
        
        # Auto-adjust offsets if they're out of bounds for this frame size
        self._validate_and_adjust_config()
        
        self.tile_states = self._load_tile_states()
    
    def _validate_and_adjust_config(self):
        """Validate and adjust config for current frame dimensions."""
        scale_x = self.grid_config.get('scale_x', 0.85)
        scale_y = self.grid_config.get('scale_y', 0.67)
        
        # Calculate centered X offset based on scale_x only
        grid_width = self.tile_width * self.GRID_WIDTH * scale_x
        centered_offset_x = (self.frame_width - grid_width) / 2.0
        
        # Keep the custom Y offset if provided, otherwise center
        current_offset_y = self.grid_config.get('offset_y', 0.0)
        
        # Always center horizontally
        self.grid_config['offset_x'] = centered_offset_x
        # Keep Y offset as specified (allows vertical translation)
        self.grid_config['offset_y'] = current_offset_y
    
    def _load_grid_config(self):
        """Load grid scale and offset from display_config.json."""
        default_config = {
            'scale_x': 0.85,
            'scale_y': 0.67,
            'offset_x': 96.0,
            'offset_y': 88.0
        }
        
        if os.path.exists(self.DISPLAY_CONFIG_FILE):
            try:
                with open(self.DISPLAY_CONFIG_FILE, 'r') as f:
                    config_data = json.load(f)
                    grid_config = config_data.get('grid', {})
                    if 'scale_x' in grid_config:
                        print(f"[INIT] Loaded grid config from {self.DISPLAY_CONFIG_FILE}")
                        return grid_config
                    print(f"[INIT] No grid config in {self.DISPLAY_CONFIG_FILE}, using defaults")
                    return default_config
            except Exception as e:
                print(f"[INIT] Error loading {self.DISPLAY_CONFIG_FILE}: {e}, using defaults")
                return default_config
        else:
            print(f"[INIT] {self.DISPLAY_CONFIG_FILE} not found, using default config")
        return default_config
    
    def _load_tile_states(self):
        """Load tile states from shaded_tiles.json."""
        if os.path.exists(self.SHADED_TILES_FILE):
            try:
                with open(self.SHADED_TILES_FILE, 'r') as f:
                    data = json.load(f)
                    states = {}
                    for key, value in data.items():
                        tile_tuple = tuple(map(int, key.split(',')))
                        states[tile_tuple] = value
                    print(f"[INIT] Loaded {len(states)} tile states from {self.SHADED_TILES_FILE}")
                    return states
            except Exception as e:
                print(f"[INIT] Error loading {self.SHADED_TILES_FILE}: {e}")
                return {}
        else:
            print(f"[INIT] {self.SHADED_TILES_FILE} not found, starting with empty tile states")
        return {}
    
    def draw_overlay(self, frame):
        """
        Draw grid overlay on frame with shaded tiles.
        
        Args:
            frame (np.ndarray): Input frame (BGR format)
        
        Returns:
            np.ndarray: Frame with grid overlay applied
        """
        overlay = frame.copy()
        
        # Get scale and offset from config
        scale_x = self.grid_config.get('scale_x', 0.85)
        scale_y = self.grid_config.get('scale_y', 0.85)
        offset_x = self.grid_config.get('offset_x', 0.0)
        offset_y = self.grid_config.get('offset_y', 0.0)
        
        scaled_tile_width = self.tile_width * scale_x
        scaled_tile_height = self.tile_height * scale_y
        
        # Draw shaded tiles
        for (tile_x, tile_y), state in self.tile_states.items():
            if state == 'empty':  # Skip empty tiles - keep transparent
                continue
            color = self.TILE_STATES.get(state, (0, 0, 255))
            x1 = int(offset_x + tile_x * scaled_tile_width)
            y1 = int(offset_y + tile_y * scaled_tile_height)
            x2 = int(offset_x + (tile_x + 1) * scaled_tile_width)
            y2 = int(offset_y + (tile_y + 1) * scaled_tile_height)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        
        # Draw grid lines
        for col in range(self.GRID_WIDTH + 1):
            x = int(offset_x + col * scaled_tile_width)
            if 0 <= x < self.frame_width:
                cv2.line(overlay, (x, 0), (x, self.frame_height), (0, 255, 0), 1)
        
        for row in range(self.GRID_HEIGHT + 1):
            y = int(offset_y + row * scaled_tile_height)
            if 0 <= y < self.frame_height:
                cv2.line(overlay, (0, y), (self.frame_width, y), (0, 255, 0), 1)
        
        # Return overlay without blending (opacity controlled by main.py slider)
        return overlay
