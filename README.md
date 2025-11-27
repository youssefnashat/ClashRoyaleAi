# Clash Royale AI - Roboflow Edition

**Branch**: `feature/card-detection`

Real-time Clash Royale detection using **Roboflow Machine Learning** instead of template matching.

## What This Does

- ✅ **ML-powered detection** of troops, buildings, and spells
- ✅ **Elixir tracking** (opponent elixir estimation)
- ✅ **Card cycle tracking** (infers opponent deck and hand)
- ✅ **Real-time dashboard** showing detections and game state

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

3. **What you'll see:**
   ```
   ==================================================
   CLASH ROYALE AI - ROBOFLOW EDITION
   ==================================================

   Frame: 245
   Opponent Elixir: 7.3 / 10.0

   --- ACTIVE DETECTIONS ---
     • Hog Rider (0.92)
     • Knight (0.88)

   --- KNOWN OPPONENT CARDS ---
     4/8 cards discovered:
     • Fireball
     • Hog Rider
     • Knight
     • Musketeer

   Press Ctrl+C to quit
   ==================================================
   ```

4. **To stop:** Press `Ctrl+C`

## How It Works

### Detection Pipeline
1. **Capture** - Grabs frames from the emulator window
2. **Detect** - Runs Roboflow ML inference
3. **Track** - Updates elixir and card cycle
4. **Display** - Prints dashboard every 2 seconds

### Elixir Tracking
- Starts at 5.0 elixir
- Regenerates at 0.35/sec (0.70/sec in double elixir)
- Deducts costs when cards are detected
- Uses comprehensive card cost database

### Duplicate Prevention
- Tracks recently detected cards (position + time)
- Prevents counting the same troop multiple times
- 3-second debounce window
- 50-pixel position threshold

## Files

```
src/
├── capture.py       # Window capture logic
├── config.py        # Settings
├── detector.py      # Roboflow ML wrapper
└── state_manager.py # Elixir + cycle tracking

main.py              # Main application
.env                 # API credentials (create from .env.example)
```

## Configuration

Edit `src/config.py`:
- `WINDOW_NAME_PATTERNS` - Emulator window titles to search for
- `DETECTION_CONFIDENCE_THRESHOLD` - Minimum confidence (default: 0.5)
- `FPS_TARGET` - Target detection rate (default: 20 FPS)

Edit `src/state_manager.py`:
- `ELIXIR_REGEN_SINGLE` - Normal elixir regeneration (default: 0.35/sec)
- `duplicate_threshold` - Position similarity threshold (default: 50px)
- `debounce_time` - Duplicate prevention window (default: 3.0sec)

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
- Ensure emulator is in Portrait mode with good quality

### High CPU Usage
- Decrease `FPS_TARGET` in `config.py`
- Add delay in main loop (`time.sleep()`)

## Next Steps

- Train your own Roboflow model for better accuracy
- Add visualization (draw bounding boxes on screen)
- Implement double elixir mode detection
- Add logging and metrics

## Model Training Tips

If you want to train your own model:
1. Collect screenshots from matches
2. Annotate troops/buildings/spells in Roboflow
3. Use at least 200-300 images per class
4. Test with data augmentation
5. Export as "Object Detection" model
