# Clash Royale Match Analyzer

A real-time Python application that analyzes a running Clash Royale emulator window to track the opponent's Elixir and Card Cycle using Computer Vision.

## Features
- **Elixir Tracking**:
  - **User**: Estimates user elixir visually from the bottom bar.
  - **Opponent**: Calculates opponent elixir based on generation rates (Single/Double Elixir) and card usage.
- **Card Detection**: Uses Template Matching to detect when cards are played on the arena.
- **Cycle Tracking**: Tracks the opponent's Hand, Deck, and Queue.

## Prerequisites
- **Emulator**: BlueStacks, LDPlayer, or similar running Clash Royale.
- **Python 3.10+**

## Installation

1.  **Clone/Download** this repository.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Dependencies: `opencv-python`, `mss`, `numpy`, `pywin32`*

## Configuration
Check `src/config.py` to adjust settings:
- `WINDOW_NAME_PATTERNS`: Add your emulator's window title if it's not detected (default: "BlueStacks", "LDPlayer", "Clash Royale").
- `ELIXIR_BAR_ROI`: Region of Interest for the elixir bar.
- `ARENA_ROI`: Region of Interest for the arena (card detection).

## Usage

### 1. Generate Card Assets
Before the bot can detect cards, you need to create templates.

1.  Run the asset capture tool:
    ```bash
    python tools/capture_assets.py
    ```
2.  When the emulator window is found, play a match or replay.
3.  Press **'s'** to save a snapshot of the arena when a card is visible.
4.  Images are saved to `assets/cards_raw/`.
5.  **Manual Step**: Crop these images to just the card sprite and save them to `assets/cards/` as `.png` files (e.g., `hog_rider.png`).

### 2. Run the Analyzer
1.  Start a match.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  A dashboard will appear showing Elixir stats and the predicted opponent hand.
4.  Press **'q'** to quit.

## Troubleshooting
- **Window Not Found**: Ensure the emulator is not minimized. Check `src/config.py` window titles.
- **High DPI Issues**: The app attempts to handle High DPI automatically. If screenshots look zoomed in, check your Windows Display Scaling settings.
- **Elixir Detection**: If "My Elixir" is inaccurate, verify the `ELIXIR_BAR_ROI` in `config.py` matches your screen resolution (the app resizes captures to 450px width).
