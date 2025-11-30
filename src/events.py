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
    
    def get_current_tile_states(self):
        """Get the current tile states (for overlay display)."""
        return self.current_tile_states


# Utility function to apply events to GridOverlay
def apply_event_to_overlay(grid_overlay, event_handler):
    """
    Temporarily override grid overlay's tile states with event handler's states.
    Call this in the main loop before drawing.
    
    Args:
        grid_overlay: GridOverlay instance
        event_handler: GameEvents instance
    """
    grid_overlay.tile_states = event_handler.get_current_tile_states()

