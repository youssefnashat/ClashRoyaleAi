# Clash Royale Full Overlay

**Branch**: `full_overlay`

This branch combines **real-time elixir tracking** with **arena grid overlay** for Clash Royale. It uses computer vision to detect your elixir and displays an interactive 18×32 grid overlay on top of your game board.

## What This Branch Does

- ✅ **Captures** your game window (Android emulator)
- ✅ **Detects** the purple elixir bar at the bottom of the screen
- ✅ **Counts** elixir using a **10-segment detection** system (0-10)
- ✅ **Tracks** opponent elixir with estimated recovery rates
- ✅ **Displays** a 18×32 grid overlay on the arena
- ✅ **Shows** both your and opponent's elixir in real-time

## Prerequisites

- **Emulator**: Android emulator running Clash Royale
  - Window must be named "Android Device" (MuMu Player, BlueStacks, etc.)
  - **Portrait mode required** (900 by 1600 REQUIRED)
  - Match or Training mode (elixir bar must be visible)
- **Python 3.10+**

## Installation

1. **Clone/Download** this repository and switch to the `full_overlay` branch:
   ```bash
   git checkout full_overlay
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows PowerShell
   .\venv\Scripts\Activate
   
   # Windows CMD
   venv\Scripts\activate.bat
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `display_config.json`** (Required for first run):
   ```bash
   cp display_config.json.example display_config.json
   ```
   Then adjust the values to match your screen:
   - `grid.offset_x`, `grid.offset_y`: Grid position
   - `elixir_bar.x`, `elixir_bar.y`: Elixir bar position
   - See [Configuration](#configuration) section below

## Usage

1. **Start Clash Royale** in your emulator (Portrait mode, in a match or training)

2. **Run the main application**:
   ```bash
   python main.py
   ```

3. **What you'll see**:
   - **Game Screen**: Your game window with overlays
   - **Grid Overlay**: 18×32 translucent grid on the arena
   - **Green Box**: Bounding box around the elixir bar at the bottom
   - **Yellow Text**: Real-time elixir values
     - "Your Elixir: X.X" (your current elixir)
     - "Opponent Est: X.X" (estimated opponent elixir based on tracker)
   - **Frame Counter**: Updates every 30 frames

4. **Press 'q'** to quit

## How It Works

### Elixir Tracking
The elixir bar is divided into **11 equal units**:
- **First box** = 2 units (represents 1 elixir, requires 75% fill)
- **Other 9 boxes** = 1 unit each (requires 35% fill)

Each box that passes the threshold adds 1 to the elixir count.

### Opponent Elixir Estimation
The opponent elixir tracker estimates elixir recovery based on time:
- **Single Elixir**: Recovers at ~0.35 elixir per 30 frames
- **Double Elixir**: Recovers at ~0.7 elixir per 30 frames

### Grid Overlay
The grid is a 18×32 tile overlay representing the Clash Royale arena. It is:
- **Horizontally centered** on the screen
- **Vertically compressed** (67% height) to fit gameplay area
- **Semi-transparent** (33% opacity) to not obstruct gameplay
- **Configurable** via `grid_config.json` and `shaded_tiles.json`

## Configuration

### Display Configuration (`display_config.json`)

**Important**: This file is **local to your machine** and controls the exact positioning of the grid and elixir bar. It's in `.gitignore` so each user must create their own.

**New users must create this file** by adjusting the default values to match your screen:

```json
{
  "grid": {
    "scale_x": 0.85,        // Horizontal scale (0.0-1.0)
    "scale_y": 0.67,        // Vertical scale (0.0-1.0)
    "offset_x": 96.0,       // Horizontal position (auto-centered if frame resizes)
    "offset_y": 88.0        // Vertical position in pixels
  },
  "elixir_bar": {
    "x": 94,                // Left edge position
    "y": 797,               // Top edge position
    "width": 340,           // Box width
    "height": 20            // Box height
  }
}
```

**How to find your correct values**:
1. Run `python main.py`
2. Look at the green bounding box around the elixir bar and grid position
3. Note the displayed ROI coordinates `(x, y, width, height)`
4. Update `display_config.json` accordingly
5. Restart to verify positioning is correct

### Elixir Detection (`src/config.py`)

- **`ELIXIR_BAR_ROI`**: Coordinates of the elixir bar `(x, y, width, height)`
  - Current: `(90, 797, 340, 20)`
- **`PURPLE_LOWER` / `PURPLE_UPPER`**: HSV color range for purple detection
  - Current: `(115, 30, 30)` to `(175, 255, 255)`
- **`ELIXIR_SEGMENT_THRESHOLD`**: Minimum % of purple pixels to count as "filled"
  - Current: `0.35` (35%)

### Grid Overlay Settings

Grid settings are now part of `display_config.json`:

- **`scale_x`**: Horizontal scaling factor (default: 0.85)
- **`scale_y`**: Vertical scaling factor (default: 0.67)
- **`offset_x`**: Horizontal offset (auto-centered, default: 96.0)
- **`offset_y`**: Vertical offset in pixels (default: 88.0)

### Tile States (`shaded_tiles.json`)

Defines which tiles are shaded and their appearance in the overlay.

## Troubleshooting

- **Window Not Found**: Ensure your emulator window is titled "Android Device"
- **Stuck on 9**: Threshold may be too high, lower `ELIXIR_SEGMENT_THRESHOLD` in `config.py`
- **Shows 1 when empty**: First segment threshold too low, increase the `0.75` value in `src/vision.py` line 68
- **Landscape Warning**: Rotate your emulator to Portrait mode (9:16 aspect ratio)

## Files in This Branch

```
src/
├── __init__.py           # Python package marker
├── capture.py            # Screen capture logic
├── config.py             # Configuration and thresholds
└── vision.py             # Elixir detection + grid overlay

main.py                    # Main application entry point
grid_config.json           # Grid transformation settings
shaded_tiles.json          # Tile state definitions
requirements.txt           # Python dependencies
README.md                  # This file
walkthrough.md             # Step-by-step testing guide
```

## Next Steps

This branch is complete and tested. For the full application:
- **Card Detection**: See `feature/card-detection` branch
- **Cycle Logic**: See `feature/cycle-logic` branch
- **Integration**: These will be merged into `main`
