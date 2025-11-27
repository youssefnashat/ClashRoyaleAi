# Configuration for Clash Royale AI - Roboflow Edition

# Window Capture Settings
WINDOW_NAME_PATTERNS = ["Android Device", "BlueStacks", "LDPlayer", "MuMu"]
RESIZE_WIDTH = 450
RESIZE_HEIGHT = 800

# Detection Settings
DETECTION_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to consider a detection
FPS_TARGET = 20  # Target frames per second for detection

# Roboflow Model (loaded from .env)
# ROBOFLOW_API_KEY - from .env
# ROBOFLOW_MODEL_ID - from .env (e.g., "clash-royale-xy2jw/2")
