# Clash Royale AI - Roboflow Edition

**Branch**: `feature/card-detection`

Real-time Clash Royale detection using **Roboflow Machine Learning** instead of template matching.

## What This Does

- ✅ **ML-powered detection** of troops, buildings, and spells
- ✅ **Elixir tracking** (opponent elixir estimation)
- ✅ **Card cycle tracking** (infers opponent deck and hand)
- ✅ **Real-time dashboard** showing detections and game state
- ✅ **Grid Overlay** - Interactive 18×32 arena grid with adjustable opacity
- ✅ **Tower Detection** - ML-based princess tower detection

## Prerequisites

- **Emulator**: Android emulator running Clash Royale (Portrait mode)
- **Python 3.10+**
- **Roboflow Account**: Free tier available at [roboflow.com](https://roboflow.com)
- **Trained Model**: A Clash Royale object detection model on Roboflow

## Setup

### 1. Install Dependencies

```bash
# Create/activate virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows PowerShell

# Install requirements
pip install -r requirements.txt
```

### 2. Configure API Keys

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   ROBOFLOW_API_KEY=your_api_key_here
   ROBOFLOW_MODEL_ID=clash-royale-xy2jw/2
   TROOP_MODEL_ID=clash-royale-xy2jw/2
   HAND_CARDS_MODEL_ID=clash-cards-vt0gf/1
   ```

   **Get your API key:**
   - Go to [https://app.roboflow.com/settings/api](https://app.roboflow.com/settings/api)
   - Copy your API key

   **Model ID format:** `workspace/project/version`

## Usage

1. **Start Clash Royale** in your emulator (Portrait mode)

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Controls:**
   - **Settings Window**: Adjust features in real-time
     - Grid Overlay: 0-100% opacity slider
     - Elixir Tracking: On/Off toggle
     - Tower Detection: On/Off toggle
   - **Close Application**: Press `Q` in the game overlay window or click X on settings window

## How It Works

### Detection Pipeline
1. **Capture** - Grabs frames from the emulator window
2. **Detect** - Runs Roboflow ML inference (Troops & Hand Cards)
3. **Track** - Updates elixir and card cycle
4. **Display** - Overlays information on the game stream

### Elixir Tracking
- Starts at 5.0 elixir
- Regenerates at 0.35/sec (0.70/sec in double elixir)
- Deducts costs when cards are detected

### Duplicate Prevention
- Tracks recently detected cards (position + time)
- Prevents counting the same troop multiple times
- 3-second debounce window

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
  ├── hand_tracker.py            # Hand card detection
  ├── state_manager.py           # Tower state tracking
  ├── settings_window.py         # Settings UI
  ├── events.py                  # Keyboard event handling
  └── __pycache__/
assets/
  ├── cards_raw/                 # Card image assets
  └── shaded_tiles.json          # Grid tile state definitions
```

## Troubleshooting

### "Missing required environment variables"
- Make sure you created `.env` file (copy from `.env.example`)
- Verify your API key is correct

### "Window Not Found"
- Ensure emulator is running and not minimized
- Check window title matches `WINDOW_NAME_PATTERNS` in `config.py`

### Low Accuracy
- Increase `DETECTION_CONFIDENCE_THRESHOLD` in `config.py`
- Check your Roboflow model's performance metrics

## License

This project is part of the ClashRoyaleAi repository.
