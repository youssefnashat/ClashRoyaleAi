# Clash Royale AI Overlay - Walkthrough

This walkthrough covers the modular overlay system with grid, elixir, and tower detection features.

## Prerequisites

- Android emulator running Clash Royale
- Emulator in **Portrait mode** (e.g., 450×827)
- Window title is "Android Device"
- **In a match or training mode** (elixir bar visible)
- Python 3.14+

## Setup (First Time Only)

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` File
Create a `.env` file in the project root with your Roboflow API key:
```
ROBOFLOW_API_KEY=your_api_key_here
TROOP_MODEL_ID=clash-royale-xy2jw/2
CARD_MODEL_ID=clash-cards-vt0gf/1
ROBOFLOW_MODEL_ID=clash-royale-xy2jw/2
```

**Note**: The `.env` file will persist locally and won't be tracked by git.

## Testing the Overlay System

### 1. Start Clash Royale
- Open your emulator
- Launch Clash Royale
- **Important**: Start a match or training mode so the elixir bar is visible

### 2. Run the Main Application
```bash
python main.py
```

### 3. What You Should See

#### Game Overlay Window
- Your game feed with overlay applied
- Grid tiles with adjustable opacity
- Green elixir text "E = X.X" at the bottom
- Red bounding box around detected towers (when enabled)

#### Settings Window
- **Grid Opacity**: Slider from 0% to 100% (default 20%)
- **Elixir Tracking**: Toggle on/off
- **Tower Detection**: Toggle on/off

### 4. Testing Features

#### Grid Overlay
1. Keep slider at 20% default
2. Slowly move slider right to see grid fade in
3. At 100%, grid should be fully opaque
4. Move slider back to 20% to verify opacity control

#### Elixir Tracking
1. Toggle "Elixir Tracking" ON in settings
2. Look at bottom fifth of game screen
3. Should see green "E = X.X" text with black background
4. Value updates in real-time as elixir changes
5. Toggle OFF to hide elixir display

#### Tower Detection
1. Toggle "Tower Detection" ON in settings
2. Game should detect princess towers
3. Red bounding boxes appear around detected towers
4. Boxes update in real-time
5. **Note**: Requires valid Roboflow API key in `.env`

#### Keyboard Controls
- Press `Q` to quit the application

### 5. Real-time Feature Toggling
1. Toggle features on/off in settings window
2. Notice console output shows feature state changes
3. Systems reinitialize when features are toggled
4. No need to restart application

## Verifying Initialization

On startup, you should see console output showing:

```
===========================================================================
CLASH ROYALE OVERLAY SYSTEM
===========================================================================

Initializing Settings Window...
[OK] Settings window created

Initializing Capture...
Found window: Android Device
[OK] Found window: Android Device
[OK] Frame size: 450x826

[OK] Grid overlay initialized

===========================================================================
GRID INITIALIZATION VERIFICATION:
===========================================================================
Grid Configuration (from display_config.json):
  scale_x: 0.85
  scale_y: 0.67
  offset_x: 33.75
  offset_y: 88.0

Tile States Loaded from JSON (shaded_tiles.json):
  Total tiles: 576
  ...

[OK] Elixir tracking initialized

FEATURES ENABLED:
  Grid Overlay: 20%
  Elixir Tracking: True
  Tower Detection: False
```

This confirms all systems initialized correctly.

## Troubleshooting

**Grid not visible**: 
- Check opacity slider is above 0%
- Verify grid.json loads correctly (check console for tile counts)

**Elixir not showing**:
- Ensure "Elixir Tracking" toggle is ON
- Check you're in a match with elixir bar visible
- Verify elixir bar ROI is correct in config

**Tower detection not working**:
- Ensure "Tower Detection" toggle is ON
- Check `.env` has valid ROBOFLOW_API_KEY
- Verify model IDs are correct
- Check network connection (API calls required)

**Window not found**:
- Ensure emulator is running
- Check window title is exactly "Android Device"
- Verify emulator is in portrait mode

**Settings window won't open**:
- Check no other overlay windows are open
- Try restarting application
- Verify tkinter is installed (should be with Python)

## Understanding Feature State

Each feature can be independently toggled:

1. **Grid Overlay**: Always renders but opacity controlled by slider
2. **Elixir Tracking**: Only processes and displays when enabled
3. **Tower Detection**: Only processes detections when enabled

Toggling a feature OFF will:
- Stop processing that feature
- Remove display elements
- Free up CPU resources
- Show in console as reinitializing

## Performance Notes

- Grid rendering is lightweight
- Elixir detection uses ROI-based analysis (fast)
- Tower detection uses ML inference (slower, ~1-2 FPS impact)
- Disabling unused features improves performance
- Default settings (20% grid, elixir ON, towers OFF) balanced for performance

## Next Steps

- Adjust grid opacity slider to your preference
- Try different opacity levels to find sweet spot
- Enable tower detection and verify towers are detected correctly
- Use keyboard shortcuts to interact with the grid
- Monitor console for any errors or warnings
