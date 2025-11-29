# Clash Royale Match Analyzer

A Python-based tool for recording and analyzing Clash Royale matches from an Android emulator with an interactive 18×32 tile grid overlay.

## Quick Start

### First Time Setup (After Cloning)

Follow these steps **once** when you first clone the repository:

#### 1. Create Virtual Environment
```powershell
python -m venv .venv
```

#### 2. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate
```

You should see `(.venv)` at the start of your terminal prompt.

#### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

#### 4. Post-Install Configuration (for pywin32)
```powershell
python -m pip install --upgrade pywin32
```

### Every Time You Open the Project

Simply activate the virtual environment:

```powershell
.\.venv\Scripts\Activate
```

## Project Structure

```
ClashRoyaleAi/
├── functions/
│   ├── vision.py         # Main: Window recording with grid overlay (includes windowing)
│   ├── tiles.py          # Optional: Interactive tile grid editor
│   ├── __init__.py       # Package initialization
│   └── __pycache__/      # Compiled Python bytecode (auto-generated)
├── recordings/           # Saved video recordings
├── grid_config.json      # Saved grid scale and offset settings
├── shaded_tiles.json     # Saved tile state definitions
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .venv/              # Virtual environment (auto-created)
```

## Usage

### Record a Window with Grid Overlay

To select a window and start recording with the grid overlay:

```powershell
python functions/vision.py
```

**Features:**
- Automatically lists all visible windows
- Number input to select which window to record
- Loads saved grid configuration (scale, offset) from `grid_config.json`
- Displays 18×32 tile grid overlay with saved tile state colors
- `q` - Stop recording
- Option to save recording as MP4 video
- Recordings saved with overlay applied

### Grid Configuration

The grid configuration is stored in JSON files:

- **`grid_config.json`** - Grid scale and position
  ```json
  {
    "scale_x": 0.85,
    "scale_y": 0.85,
    "offset_x": 62.925,
    "offset_y": 162.945
  }
  ```

- **`shaded_tiles.json`** - Tile state definitions and colors
  - Tiles can be in states: `red`, `leftEnemyDown`, `rightEnemyDown`, `leftFriendlyDown`, `rightFriendlyDown`
  - Persist between recording sessions

### Interactive Tile Editor (Optional)

To interactively edit tile states:

```powershell
python functions/tiles.py
```

**Controls:**
- **LEFT CLICK** - Cycle tile through states
- **RIGHT CLICK** - Clear tile
- **'c'** - Clear all tiles
- **ESC** - Exit and save

## Dependencies

All dependencies are specified in `requirements.txt`:

- **opencv-python** - Computer vision and video encoding
- **mss** - Fast window/screen capture
- **numpy** - Array operations
- **pywin32** - Windows API integration for window management

## Troubleshooting

### "Module not found" errors
- Make sure virtual environment is activated: `.\venv\Scripts\Activate`
- Run `pip install -r requirements.txt` to reinstall packages

### Window recording shows wrong colors
- This is typically a BGR/RGB color space issue (already handled in the code)

### "Handle is invalid" warning during recording
- This is non-critical and recording will continue normally

### Grid overlay not appearing
- Check that `grid_config.json` exists in the project root
- Check that `shaded_tiles.json` exists for tile definitions
- Both files should be auto-created after first interactive grid adjustment

### VS Code says imports can't be resolved
- Restart VS Code after installing packages
- Check that Python interpreter is set to `./.venv/Scripts/python.exe`

## Development

To add new dependencies:

1. Install with pip: `pip install package-name`
2. Update `requirements.txt`: `pip freeze > requirements.txt`

## Notes

- The grid overlay is semi-transparent (33% opacity) to allow seeing the underlying content
- Grid is always centered and scaled to 85% by default to prevent distortion
- All grid settings persist between recording sessions via JSON files
- The `tiles.py` module is optional; `vision.py` works independently using only JSON data
