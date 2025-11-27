# Clash Royale Match Analyzer - Walkthrough

## Prerequisites
- **Emulator**: BlueStacks, LDPlayer, or similar running Clash Royale.
- **Python Environment**: Ensure dependencies are installed (`pip install -r requirements.txt` or via the provided venv).
# 1. Create the virtual environment
python -m venv venv

# 2. Activate it (PowerShell specific command)
.\venv\Scripts\Activate

# 3. Install your libraries
pip install opencv-python mss numpy pywin32

## Step 1: Asset Generation
Before the bot can detect cards, it needs templates.

1.  Open your emulator and start a **Training Match** or **Replay**.
2.  Run the asset capture tool:
    ```bash
    python tools/capture_assets.py
    ```
3.  The tool will wait for the emulator window. Once found, it will show the "Arena ROI".
4.  When a card is played and clearly visible on the arena:
    - Press **'s'** to save a snapshot to `assets/cards_raw/`.
5.  **Crop the Cards**:
    - Open the saved images in `assets/cards_raw/`.
    - Crop out *just* the card sprite (e.g., the Hog Rider or Log).
    - Save the cropped image to `assets/cards/` with the card name (e.g., `hog_rider.png`, `log.png`).

## Step 2: Configuration (Optional)
If the bot isn't detecting things correctly, check `src/config.py`:
- **WINDOW_NAME_PATTERNS**: Add your emulator's window title if not listed.
- **ELIXIR_BAR_ROI**: Adjust if the elixir bar isn't being read correctly (purple detection).
- **HSV Ranges**: If elixir detection is flaky, tweak `PURPLE_LOWER` and `PURPLE_UPPER`.

## Step 3: Running the Analyzer
1.  Start a match in Clash Royale.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  A dashboard window will appear showing:
    - **My Elixir**: Estimated from the bottom bar.
    - **Opp Elixir**: Calculated based on time and card usage.
    - **Hand**: The predicted opponent hand.

## Troubleshooting
- **Window Not Found**: Ensure the emulator is running and not minimized. Check the window title against `config.py`.
- **Elixir Always 0**: The ROI might be wrong. Use `tools/capture_assets.py` to debug the view or adjust `ELIXIR_BAR_ROI` in `config.py`.
- **False Positive Cards**: Increase `MATCH_CONFIDENCE` in `config.py`.
