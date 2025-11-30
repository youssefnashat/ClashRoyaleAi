class GameEvents:
    """
    Manages game events and state for the overlay.
    """
    def __init__(self):
        self.active_events = []

    def print_help(self):
        print("Controls:")
        print("  x: Reset all tiles")
        print("  [key]: Trigger event for key")

    def reset_to_original(self):
        self.active_events = []

    def trigger_event(self, char):
        print(f"Event triggered: {char}")
        self.active_events.append(char)

def apply_event_to_overlay(grid, events):
    """
    Applies active events to the grid overlay.
    """
    # Stub implementation - does nothing for now
    pass
