# Configuration for Clash Royale Match Analyzer
import os
from dotenv import load_dotenv

load_dotenv()

# Window Capture Settings
WINDOW_NAME_PATTERNS = ["Android Device", "BlueStacks", "LDPlayer", "MuMu"]
RESIZE_WIDTH = 450
RESIZE_HEIGHT = 800

import json

# Load display configuration from unified config file
def _load_display_config():
    """Load display positions and grid settings from display_config.json."""
    config_file = "display_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    # Default fallback
    return {
        "grid": {
            "scale_x": 0.85,
            "scale_y": 0.67,
            "offset_x": 96.0,
            "offset_y": 88.0
        },
        "elixir_bar": {
            "x": 90,
            "y": 797,
            "width": 340,
            "height": 20
        }
    }

_display_config = _load_display_config()

# Region of Interest (ROI) Definitions
# Format: (x, y, width, height) - loaded from display_config.json
_elixir_cfg = _display_config.get("elixir_bar", {"x": 90, "y": 797, "width": 340, "height": 20})
ELIXIR_BAR_ROI = (_elixir_cfg["x"], _elixir_cfg["y"], _elixir_cfg["width"], _elixir_cfg["height"]) 

# Arena: Where cards are played (The main battlefield)
ARENA_ROI = (20, 100, 410, 500)

# Card Detection Settings
MATCH_CONFIDENCE = 0.8
DEBOUNCE_TIME = 3.0  # Seconds to ignore the same card

# Elixir Logic
ELIXIR_RECOVERY_RATE_SINGLE = 0.35  # Elixir per second
ELIXIR_RECOVERY_RATE_DOUBLE = 0.7
ELIXIR_MAX = 10.0
ELIXIR_START = 5.0

# Elixir Calibration
# Threshold for a single segment (1/10th of bar) to be considered "Active"
# 0.35 means at least 35% of the segment must be purple.
ELIXIR_SEGMENT_THRESHOLD = 0.35

# HSV Color Ranges for Purple Elixir
# OpenCV HSV ranges: H: 0-179, S: 0-255, V: 0-255
# Purple (Elixir) - Widened range to catch gradients/glows
PURPLE_LOWER = (115, 30, 30)
PURPLE_UPPER = (175, 255, 255)

# Grid Overlay Configuration
GRID_CONFIG_FILE = "grid_config.json"
SHADED_TILES_FILE = "shaded_tiles.json"

# Roboflow Model IDs
TROOP_MODEL_ID = os.getenv("TROOP_MODEL_ID", "clash-royale-xy2jw/2")
CARD_MODEL_ID = os.getenv("CARD_MODEL_ID", "cr-6ydc1/2")
