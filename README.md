# Clash Royale Elixir Tracker

**Branch**: `elixi_tracker`

This branch contains a **real-time elixir counter** for Clash Royale. It uses computer vision to detect and count your elixir bar with high accuracy.

## What This Branch Does

- ✅ **Captures** your game window (Android emulator)
- ✅ **Detects** the purple elixir bar at the bottom of the screen
- ✅ **Counts** elixir using a **10-segment detection** system (0-10)
- ✅ **Displays** the current elixir count in real-time

## Prerequisites

- **Emulator**: Android emulator running Clash Royale
  - Window must be named "Android Device" (MuMu Player, BlueStacks, etc.)
  - **Portrait mode required** (e.g., 900x1600 resolution)
- **Python 3.10+**

## Installation

1. **Clone/Download** this repository and switch to the `elixi_tracker` branch:
   ```bash
   git checkout elixi_tracker
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

## Usage

1. **Start Clash Royale** in your emulator (must be in Portrait mode)

2. **Run the debug tool**:
   ```bash
   python tools/debug_elixir.py
   ```

3. **What you'll see**:
   - **Main View**: Your game screen with a green box around the elixir bar
   - **Vertical Lines**: 10 segments dividing the elixir bar (first segment is double-width)
   - **Yellow Text**: Current elixir count (0-10)
   - **Elixir Mask Window**: Purple pixel detection (white = detected)

4. **Press 'q'** to quit

## How It Works

The elixir bar is divided into **11 equal units**:
- **First box** = 2 units (represents 1 elixir, requires 75% fill)
- **Other 9 boxes** = 1 unit each (requires 35% fill)

Each box that passes the threshold adds 1 to the elixir count.

## Configuration

If the detection is inaccurate, check `src/config.py`:

- **`ELIXIR_BAR_ROI`**: Coordinates of the elixir bar `(x, y, width, height)`
  - Current: `(90, 810, 340, 20)`
- **`PURPLE_LOWER` / `PURPLE_UPPER`**: HSV color range for purple detection
  - Current: `(115, 30, 30)` to `(175, 255, 255)`
- **`ELIXIR_SEGMENT_THRESHOLD`**: Minimum % of purple pixels to count as "filled"
  - Current: `0.35` (35%)

## Troubleshooting

- **Window Not Found**: Ensure your emulator window is titled "Android Device"
- **Stuck on 9**: Threshold may be too high, lower `ELIXIR_SEGMENT_THRESHOLD` in `config.py`
- **Shows 1 when empty**: First segment threshold too low, increase the `0.75` value in `src/vision.py` line 68
- **Landscape Warning**: Rotate your emulator to Portrait mode (9:16 aspect ratio)

## Files in This Branch

```
src/
├── __init__.py     # Python package marker (empty)
├── capture.py      # Screen capture logic
├── config.py       # Settings and thresholds
└── vision.py       # Elixir detection algorithm

tools/
└── debug_elixir.py # Test/debug tool
```

## Next Steps

This branch is complete and tested. For the full application:
- **Card Detection**: See `feature/card-detection` branch
- **Cycle Logic**: See `feature/cycle-logic` branch
- **Integration**: These will be merged into `main`
