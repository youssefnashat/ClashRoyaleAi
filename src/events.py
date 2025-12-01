"""
Game Events Handler
Manages game events (left/right friendly/enemy down) and tile state updates.
"""

import json
import os
import copy


class GameEvents:
    """Handles game events for Clash Royale arena."""
    
    def __init__(self):
        """Initialize game events handler."""
        self.shaded_tiles_file = "shaded_tiles.json"
        self.original_tile_states = self._load_original_tiles()
        self.current_tile_states = copy.deepcopy(self.original_tile_states)
        self.active_events = []
    
    def _load_original_tiles(self):
        """Load tile states from disk (fresh copy)."""
        if os.path.exists(self.shaded_tiles_file):
            try:
                with open(self.shaded_tiles_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys to tuples
                    states = {}
                    for key, value in data.items():
                        tile_tuple = tuple(map(int, key.split(',')))
                        states[tile_tuple] = value
                    return states
            except Exception as e:
                print(f"Error loading tile states: {e}")
                return {}
        return {}
    
    def reset_to_original(self):
        """Reset all tile states back to original (from shaded_tiles.json)."""
        self.original_tile_states = self._load_original_tiles()
        self.current_tile_states = copy.deepcopy(self.original_tile_states)
        self.active_events = []
    
    def get_current_tile_states(self):
        """Get the current tile states (for overlay display)."""
        return self.current_tile_states

    def trigger_event(self, char):
        print(f"Event triggered: {char}")
        self.active_events.append(char)

    def print_help(self):
        print("Controls:")
        print("  x: Reset all tiles")
        print("  [key]: Trigger event for key")


def apply_event_to_overlay(grid, events):
    """
    Applies active events to the grid overlay.
    """
    grid.tile_states = events.get_current_tile_states()
