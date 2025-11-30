# Clash Royale AI Overlay

A modular Python application that overlays real-time game information on Clash Royale using computer vision and machine learning.

## Features

- ✅ **Grid Overlay** - Interactive 18×32 arena grid with adjustable opacity (0-100%)
- ✅ **Elixir Tracking** - Real-time elixir detection displayed at bottom of screen in green
- ✅ **Tower Detection** - ML-based princess tower detection using Roboflow
- ✅ **Real-time Controls** - Toggle features on/off via settings window
- ✅ **Modular Architecture** - Clean, separate feature modules for easy extension

## System Requirements

- **Python 3.14** (uses HTTP-based Roboflow API, not SDK)
- **Android Emulator** running Clash Royale
  - Window must be named "Android Device"
  - Portrait mode (450×826 or similar)
  - In an active match or training mode

## Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/youssefnashat/ClashRoyaleAi.git
   cd ClashRoyaleAi
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate Virtual Environment**:
   ```bash
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   
   # Windows CMD
   .venv\Scripts\activate.bat
   
   # macOS/Linux
   source .venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` File**:
   ```bash
   # Edit .env and add your Roboflow API key
   ROBOFLOW_API_KEY=your_actual_api_key_here
   TROOP_MODEL_ID=your_troop_model_id
   CARD_MODEL_ID=your_card_model_id
   ROBOFLOW_MODEL_ID=your_tower_detection_model_id
   ```

## Usage

```bash
python main.py
```

### Controls

- **Settings Window**: Adjust features in real-time
  - Grid Overlay: 0-100% opacity slider (default 20%)
  - Elixir Tracking: On/Off toggle
  - Tower Detection: On/Off toggle
- **Close Application**: Press `Q` in the game overlay window or click X on settings window

## Project Structure

```
src/
  ├── main.py                    # Application orchestrator
  ├── capture.py                 # Game window capture
  ├── config.py                  # Configuration & feature flags
  ├── vision.py                  # Grid overlay rendering
  ├── elixir_tracker_module.py   # Elixir detection & display
  ├── tower_display.py           # Tower detection wrapper
  ├── detector.py                # Roboflow API integration
  ├── state_manager.py           # Tower state tracking
  ├── settings_window.py         # Settings UI
  ├── events.py                  # Keyboard event handling
  └── __pycache__/
assets/
  ├── cards_raw/                 # Card image assets
  └── shaded_tiles.json          # Grid tile state definitions
```

## Configuration

### `.env` File (Required)

```
ROBOFLOW_API_KEY=your_api_key
TROOP_MODEL_ID=model_id
CARD_MODEL_ID=model_id
ROBOFLOW_MODEL_ID=tower_detection_model
```

### `display_config.json` (Auto-generated)

Contains grid positioning parameters (scale, offset). Generated automatically on first run with defaults.

### `shaded_tiles.json`

Defines tile states (red, empty, tower destroyed, etc.) loaded on startup. 576 tiles per frame.

## Features In Detail

### Grid Overlay
- Adjustable opacity via slider (0-100%, default 20%)
- 18×32 tile grid showing arena state
- Color-coded tiles (red, tower positions, etc.)
- Grid lines constrained to grid boundaries
- 100% opacity shows grid fully opaque

### Elixir Tracking
- Green text display ("E = " format with value)
- Black background for visibility
- Positioned at bottom fifth of screen
- Detects elixir from ROI-based analysis

### Tower Detection
- Roboflow ML model integration
- Real-time tower position tracking
- Automatic destruction detection
- State deduplication to prevent duplicates

## Troubleshooting

**Issue**: Tower detection not working - Ensure valid Roboflow API key in `.env` and model IDs are correct

**Issue**: Window not found - Make sure Android Device window is open and in portrait mode

**Issue**: Grid lines extending beyond grid - Fixed; lines now constrain to grid boundaries

## Development

### Adding New Features

1. Create new module in `src/`
2. Implement feature class with `update()` method
3. Add feature flag to `config.py`
4. Integrate into `main.py` loop
5. Add toggle to `settings_window.py` if needed

### Code Style

- Use clear, descriptive variable names
- Add docstrings to classes and methods
- Keep modules focused and modular
- Use error handling for external API calls

## License

This project is part of the ClashRoyaleAi repository.

## Notes

- Python 3.14 required for HTTP-based API (SDK not compatible)
- All overlays drawn via OpenCV (cv2)
- Settings window uses Tkinter
- Modular architecture allows easy feature toggling
- `.env` file is persistent locally and not tracked by git
