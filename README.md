# Clash Royale Match Analyzer

A Python-based tool for recording and analyzing Clash Royale matches from an Android emulator.

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
│   ├── windowing.py      # Window selection and enumeration
│   ├── vision.py         # Window recording and frame capture
│   ├── elixir/          # Elixir tracking modules
│   ├── tiles/           # Tile detection modules
│   └── units/           # Unit detection modules
├── recordings/          # Saved video recordings
├── .vscode/            # VS Code settings
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── DEPENDENCIES.txt   # Detailed dependency information
```

## Usage

### Record a Window

To select a window and start recording:

```powershell
python functions/vision.py
```

**Controls:**
- Number input to select window
- `q` - Stop recording
- `s` - Save current frame as image
- When done recording, choose to save as MP4 video

### Select Window Only

To just list and select windows without recording:

```powershell
python functions/windowing.py
```

## Dependencies

All dependencies are specified in `requirements.txt`:

- **opencv-python** - Computer vision and video encoding
- **mss** - Fast window/screen capture
- **numpy** - Array operations
- **pywin32** - Windows API integration for window management

See `DEPENDENCIES.txt` for more details.

## Troubleshooting

### "Module not found" errors
- Make sure virtual environment is activated: `.\venv\Scripts\Activate`
- Run `pip install -r requirements.txt` to reinstall packages

### Window recording shows wrong colors
- This is typically a BGR/RGB color space issue (already handled in the code)

### "Handle is invalid" warning during recording
- This is non-critical and recording will continue normally

### VS Code says imports can't be resolved
- Restart VS Code after installing packages
- Check that Python interpreter is set to `./.venv/Scripts/python.exe`

## Development

To add new dependencies:

1. Install with pip: `pip install package-name`
2. Add to `requirements.txt` with version: `pip freeze | grep package-name >> requirements.txt`
3. Update `DEPENDENCIES.txt` with description

## Contributing

Before committing changes:
- Ensure virtual environment is activated
- Test your changes
- Update README or DEPENDENCIES if adding new requirements
