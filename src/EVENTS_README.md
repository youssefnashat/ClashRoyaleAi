# Game Events System

The `src/events.py` module provides keystroke-triggered game events for testing the grid overlay system.

## Features

- **Real-time tile state updates** - Press keys to instantly update tile states
- **No persistent changes** - All updates are in-memory; restarting loads fresh `shaded_tiles.json`
- **Live overlay visualization** - See tile changes reflected immediately in the overlay

## Keystroke Controls

| Key | Event | Effect |
|-----|-------|--------|
| **L** | Left Enemy Down | Clears all `leftEnemyDown` tiles → `empty` |
| **R** | Right Enemy Down | Clears all `rightEnemyDown` tiles → `empty` |
| **F** | Left Friendly Down | Clears all `leftFriendlyDown` tiles → `empty` |
| **D** | Right Friendly Down | Clears all `rightFriendlyDown` tiles → `empty` |
| **X** | Reset | Restore all tiles to original `shaded_tiles.json` state |
| **Q** | Quit | Exit the application |

## Usage in Code

```python
from src.events import GameEvents, apply_event_to_overlay

# Initialize
events = GameEvents()

# In main loop:
events.trigger_event('l')  # Trigger left enemy down event
apply_event_to_overlay(grid, events)  # Update overlay with new states
```

## How It Works

1. **GameEvents** loads the original `shaded_tiles.json` on startup
2. When a keystroke is triggered, it searches for all tiles with that event type
3. Found tiles are set to `'empty'` state (which renders as transparent)
4. The overlay is updated with the new tile states
5. On next run, fresh `shaded_tiles.json` is loaded (no permanent changes)

## Implementation Details

- `tile_states` are stored as a dict with tuple keys: `(row, col) -> state`
- `current_tile_states` tracks runtime changes (in-memory only)
- `original_tile_states` preserves the disk state for reset functionality
- Events cleared: All tiles matching the event type become `'empty'`
