# Full Overlay - Testing Walkthrough

This walkthrough shows you how to test the combined elixir tracking and grid overlay features step-by-step.

## Prerequisites

- Android emulator running Clash Royale
- Emulator in **Portrait mode** (e.g., 450×827)
- Window title is "Android Device"
- **In a match or training mode** (elixir bar visible)

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

## Testing the Full Overlay

### 1. Start Clash Royale
- Open your emulator
- Launch Clash Royale
- **Important**: Start a match or training mode so the elixir bar is visible

### 2. Run the Main Application
```bash
python main.py
```

### 3. What You Should See

**One Window With Multiple Overlays:**

1. **Game Screen**
   - Shows your game window

2. **Grid Overlay**
   - Semi-transparent 18×32 grid displayed on the arena
   - Horizontally centered
   - Vertically compressed to fit gameplay area

3. **Green Bounding Box**
   - Rectangle around the elixir bar at the bottom of the screen

4. **Yellow Text Overlays** (top-left):
   - `Your Elixir: X.X` - Your current elixir (0.0-10.0)
   - `Opponent Est: X.X` - Estimated opponent elixir (0.0-10.0)
   - `Frame XXX` - Frame counter (updates every 30 frames)

### 4. Verify Accuracy

**Test Your Elixir Detection:**

✅ **Empty Elixir (0)**:
- Use all your elixir in-game
- Counter should show **0.0** or **1.0** (depending on timing)

✅ **Half Full (5)**:
- Wait for elixir to reach 5
- Counter should show values in the **4.0-6.0** range

✅ **Full Elixir (10)**:
- Wait for full elixir
- Counter should show **10.0**
- Should reach this and stay until you spend elixir

✅ **Incremental Counting**:
- Watch the counter increment smoothly as the bar fills
- May update a few times per second

**Test Opponent Tracking:**

✅ **Recovery Pattern**:
- Watch "Opponent Est" value
- It should increase over time (opponent elixir recovering)
- Pattern should show logical recovery (0.7 per 30 frames in double elixir, 0.35 in single)

✅ **Grid Overlay**:
- Should be visible and not obscure gameplay
- Grid lines should align reasonably with the arena
- Should maintain aspect ratio and centering

### 5. Exit
Press **'q'** in the OpenCV window to quit the application.

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
