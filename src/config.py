# Configuration for Clash Royale Match Analyzer

# Window Capture Settings
WINDOW_NAME_PATTERNS = ["CR-Bot"]
RESIZE_WIDTH = 450
RESIZE_HEIGHT = 800  # Approximate aspect ratio, will be calculated dynamically if needed

# Region of Interest (ROI) Definitions
# Format: (x, y, width, height) based on 450px width
# These are placeholders and may need tuning based on the actual game layout on 450px width.

# Elixir Bar: Bottom area where the purple bar is
# Assuming standard 9:16 aspect ratio, 450x800
ELIXIR_BAR_ROI = (100, 750, 250, 20) 

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

# HSV Color Ranges for Purple Elixir
# OpenCV HSV ranges: H: 0-179, S: 0-255, V: 0-255
PURPLE_LOWER = (125, 50, 50)
PURPLE_UPPER = (155, 255, 255)
