# Clash Royale AI - Princess Tower Detection

Real-time Clash Royale **princess tower detection** using **Roboflow Machine Learning** with visual popup window.

## Features

-  **ML-powered detection** of princess towers (left/right, enemy/friendly)
-  **Tower status tracking** (UP/DOWN states)
-  **Real-time visualization** with bounding boxes and state display
-  **Popup window** showing captured frame with detected towers

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

1. Create `.env` file in the root directory:
   ```env
   ROBOFLOW_API_KEY=your_api_key_here
   ROBOFLOW_MODEL_ID=clash-royale-xy2jw/2
   ```

2. Get your API key from [https://app.roboflow.com/settings/api](https://app.roboflow.com/settings/api)

## Usage

1. **Start Clash Royale** in your emulator (Portrait mode)

2. **Run the detection:**
   ```bash
   python main.py
   ```

3. **What you''ll see:**
   - A popup window showing the game screen
   - Green bounding boxes around detected towers
   - Tower state indicators at the top: `RE: LE: LF: RF:` (Right Enemy, Left Enemy, Left Friendly, Right Friendly)
   - Each state shows `True` (DOWN) or `False` (UP)

4. **To stop:** Press `Ctrl+C` in the terminal or `q` in the popup window

## How It Works

1. **Capture** - Grabs frames from the emulator window
2. **Detect** - Runs Roboflow ML inference on each frame
3. **Track** - Maintains tower state (UP/DOWN)
4. **Display** - Shows visualization with bounding boxes and states

## File Structure

```
src/
 capture.py       # Window capture logic
 detector.py      # Roboflow ML wrapper
 state_manager.py # Tower state tracking

main.py              # Main application
.env                 # API credentials
requirements.txt     # Python dependencies
```

## Tower State Codes

- **RE** = Right Enemy Tower
- **LE** = Left Enemy Tower  
- **LF** = Left Friendly Tower
- **RF** = Right Friendly Tower

State values:
- `True` = Tower is DOWN (destroyed)
- `False` = Tower is UP (active)
