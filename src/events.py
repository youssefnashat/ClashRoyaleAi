"""
Game Events Handler
Manages game events (left/right friendly/enemy down) and tile state updates.
Events are triggered by keystrokes and update the grid overlay live.
Always loads from fresh shaded_tiles.json - no persistent state changes.
"""

import json
import os
import copy


class GameEvents:
    """Handles game events for Clash Royale arena."""
    
    # Keystroke bindings for events
    KEYSTROKES = {
        'l': 'leftEnemyDown',      # L key - Left Enemy Down
        'r': 'rightEnemyDown',     # R key - Right Enemy Down
        'f': 'leftFriendlyDown',   # F key - Left Friendly Down
        'd': 'rightFriendlyDown'   # D key - Right Friendly Down (D for friendly)
    }
    
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
    
    def trigger_event(self, keystroke):
        """
        Trigger a game event based on keystroke.
        
        Args:
            keystroke (str): Single character keystroke
        
        Returns:
            bool: True if event was triggered, False otherwise
        """
        keystroke_lower = keystroke.lower()
        
        if keystroke_lower not in self.KEYSTROKES:
            return False
        
        event_type = self.KEYSTROKES[keystroke_lower]
        self._clear_event_tiles(event_type)
        return True
    
    def _clear_event_tiles(self, event_type):
        """
        Clear all tiles of a specific event type (set them to 'empty').
        
        Args:
            event_type (str): Type of event ('leftEnemyDown', 'rightEnemyDown', 
                                            'leftFriendlyDown', 'rightFriendlyDown')
        """
        count = 0
        for tile_pos, state in self.current_tile_states.items():
            if state == event_type:
                self.current_tile_states[tile_pos] = 'empty'
                count += 1
        
        if count > 0:
            print(f"✓ Event triggered: {event_type} - Cleared {count} tiles")
    
    def print_help(self):
        """Print keystroke help information."""
        print("\nGame Events - Keystroke Controls:")
        print("-" * 50)
        for key, event in self.KEYSTROKES.items():
            print(f"  {key.upper()}  -> {event}")
        print("  X  -> Reset all tiles to original state")
        print("  Q  -> Quit")
        print("-" * 50)


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
