# Elixir Tracker - Testing Walkthrough

This walkthrough shows you how to test the elixir counting feature step-by-step.

## Prerequisites

- Android emulator running Clash Royale
- Emulator in **Portrait mode** (e.g., 900x1600)
- Window title is "Android Device"

## Setup (First Time Only)

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Windows PowerShell
.\venv\Scripts\Activate

# Windows CMD
venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install opencv-python mss numpy pywin32
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Testing the Elixir Counter

### 1. Start Clash Royale
- Open your emulator
- Launch Clash Royale
- **Important**: Start a match or training mode so the elixir bar is visible

### 2. Run the Debug Tool
```bash
python tools/debug_elixir.py
```

### 3. What You Should See

**Two Windows Will Appear:**

1. **"Main View (Green Box = ROI)"**
   - Shows your game screen
   - Green rectangle around the elixir bar
   - 10 vertical green lines dividing the bar into segments
   - Yellow text showing current elixir count (e.g., "Elixir: 7")

2. **"Elixir Mask (White = Detected)"**
   - Black and white mask
   - White areas = purple pixels detected
   - Should match the filled portion of your elixir bar

### 4. Verify Accuracy

**Test these scenarios:**

✅ **Empty Elixir (0)**:
- Use all your elixir in-game
- Counter should show **0**
- First segment should be mostly black in the mask

✅ **Half Full (5)**:
- Wait for elixir to reach 5
- Counter should show **5**
- About half the bar should be white in the mask

✅ **Full Elixir (10)**:
- Wait for full elixir
- Counter should show **10**
- Entire bar should be white in the mask

✅ **Incremental Counting**:
- Watch the counter go **1 → 2 → 3 → 4...**
- It should update smoothly as the bar fills

### 5. Exit
Press **'q'** to quit the debug tool.

## Troubleshooting

### Issue: "Waiting for window..."
**Solution:** 
- Make sure Clash Royale is running
- Check that your emulator window is titled "Android Device"
- If not, update `WINDOW_NAME_PATTERNS` in `src/config.py`

### Issue: Counter is stuck at 9
**Solution:**
- The threshold is too high
- Lower `ELIXIR_SEGMENT_THRESHOLD` in `src/config.py` (try `0.30`)

### Issue: Counter shows 1 when empty
**Solution:**
- First segment is too sensitive
- In `src/vision.py` line 68, increase `0.75` to `0.80`

### Issue: Green box is in the wrong place
**Solution:**
- Your resolution may be different
- Check the "Main View" window to see where the box is
- Adjust `ELIXIR_BAR_ROI` in `src/config.py`
  - Format: `(x, y, width, height)`
  - Current: `(90, 810, 340, 20)`

### Issue: "Warning: Window is Landscape"
**Solution:**
- Clash Royale must be in Portrait mode
- Change your emulator settings to 9:16 aspect ratio
- Example: 900x1600, 720x1280, etc.

## Advanced Configuration

If you need to tune the detection, edit `src/config.py`:

```python
# Location of the elixir bar
ELIXIR_BAR_ROI = (90, 810, 340, 20)  # (x, y, width, height)

# Color range for purple detection
PURPLE_LOWER = (115, 30, 30)
PURPLE_UPPER = (175, 255, 255)

# Sensitivity (lower = more sensitive)
ELIXIR_SEGMENT_THRESHOLD = 0.35
```

## Understanding the Segments

The elixir bar is divided into **10 segments**:
- **Segment 1** (leftmost): Double-width, requires 75% fill to count
- **Segments 2-10**: Standard width, require 35% fill to count

This design:
- Prevents false positives at 0 elixir (noise/numbers)
- Makes counting more reliable as the bar fills
- Accounts for animations and gradients

## Next Steps

Once you've verified the elixir counter works accurately:
1. Commit your changes if you tuned any settings
2. Push to the `elixi_tracker` branch
3. Ready to integrate with card detection and cycle tracking!
