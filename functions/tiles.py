"""
Clash Royale grid overlay system.
Generates an 18x32 tile grid for the arena with multi-state tile shading.
"""

import cv2
import numpy as np
import json
import os


class TileGrid:
    """
    Represents an 18x32 Clash Royale arena grid overlay with multi-state tiles.
    
    Tile States:
    - red: Permanently marked tiles (Red)
    - leftEnemyDown: Green
    - rightEnemyDown: Blue
    - leftFriendlyDown: Cyan
    - rightFriendlyDown: Magenta
    """
    
    GRID_WIDTH = 18
    GRID_HEIGHT = 32
    SHADED_TILES_FILE = "shaded_tiles.json"
    
    # Tile states with their BGR colors
    TILE_STATES = {
        'red': (0, 0, 255),                    # Red
        'leftEnemyDown': (0, 255, 0),          # Green
        'rightEnemyDown': (255, 0, 0),         # Blue
        'leftFriendlyDown': (0, 255, 255),     # Cyan
        'rightFriendlyDown': (255, 0, 255)     # Magenta
    }
    
    STATE_ORDER = ['red', 'leftEnemyDown', 'rightEnemyDown', 'leftFriendlyDown', 'rightFriendlyDown']
    
    def __init__(self, frame_width, frame_height, tile_width=None, tile_height=None, 
                 alpha=0.3, grid_color=(0, 255, 0)):
        """
        Initialize the grid overlay.
        
        Args:
            frame_width (int): Width of the video frame in pixels
            frame_height (int): Height of the video frame in pixels
            tile_width (float): Width of each tile in pixels (auto-calculated if None)
            tile_height (float): Height of each tile in pixels (auto-calculated if None)
            alpha (float): Overlay transparency (0.0-1.0)
            grid_color (tuple): BGR color for grid lines
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.alpha = np.clip(alpha, 0.0, 1.0)
        self.grid_color = grid_color
        
        # Auto-calculate tile dimensions
        if tile_width is None:
            self.tile_width = frame_width / self.GRID_WIDTH
        else:
            self.tile_width = tile_width
            
        if tile_height is None:
            self.tile_height = frame_height / self.GRID_HEIGHT
        else:
            self.tile_height = tile_height
        
        # Store defaults
        self._default_tile_width = self.tile_width
        self._default_tile_height = self.tile_height
        self._default_alpha = self.alpha
        
        # Load tile states: {(tile_x, tile_y): 'state_name'}
        self.tile_states = self._load_tile_states()
    
    def _load_tile_states(self):
        """Load tile states from persistent storage."""
        if os.path.exists(self.SHADED_TILES_FILE):
            try:
                with open(self.SHADED_TILES_FILE, 'r') as f:
                    data = json.load(f)
                    states = {}
                    for key, value in data.items():
                        tile_tuple = tuple(map(int, key.split(',')))
                        states[tile_tuple] = value
                    return states
            except:
                return {}
        return {}
    
    def _save_tile_states(self):
        """Save tile states to persistent storage."""
        data = {f"{x},{y}": state for (x, y), state in self.tile_states.items()}
        with open(self.SHADED_TILES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def set_tile_state(self, tile_x, tile_y, state):
        """
        Set a tile to a specific state.
        
        Args:
            tile_x (int): Tile X coordinate (0-17)
            tile_y (int): Tile Y coordinate (0-31)
            state (str): State name from TILE_STATES
        
        Returns:
            bool: True if successful
        """
        if tile_x < 0 or tile_x >= self.GRID_WIDTH or tile_y < 0 or tile_y >= self.GRID_HEIGHT:
            return False
        
        if state not in self.TILE_STATES:
            return False
        
        self.tile_states[(tile_x, tile_y)] = state
        self._save_tile_states()
        return True
    
    def cycle_tile_state(self, tile_x, tile_y):
        """
        Cycle a tile through states (red -> leftEnemyDown -> ... -> unshaded -> red).
        
        Args:
            tile_x (int): Tile X coordinate (0-17)
            tile_y (int): Tile Y coordinate (0-31)
        
        Returns:
            str: New state name or None if unshaded
        """
        if tile_x < 0 or tile_x >= self.GRID_WIDTH or tile_y < 0 or tile_y >= self.GRID_HEIGHT:
            return None
        
        tile = (tile_x, tile_y)
        
        if tile not in self.tile_states:
            new_state = self.STATE_ORDER[0]
        else:
            current_state = self.tile_states[tile]
            try:
                current_idx = self.STATE_ORDER.index(current_state)
                if current_idx < len(self.STATE_ORDER) - 1:
                    new_state = self.STATE_ORDER[current_idx + 1]
                else:
                    new_state = self.STATE_ORDER[0]
            except ValueError:
                new_state = self.STATE_ORDER[0]
        
        self.tile_states[tile] = new_state
        self._save_tile_states()
        return new_state
    
    def clear_tile(self, tile_x, tile_y):
        """Clear a tile (remove its state)."""
        if tile_x < 0 or tile_x >= self.GRID_WIDTH or tile_y < 0 or tile_y >= self.GRID_HEIGHT:
            return False
        
        tile = (tile_x, tile_y)
        if tile in self.tile_states:
            del self.tile_states[tile]
            self._save_tile_states()
            return True
        return False
    
    def clear_all_tiles(self):
        """Clear all tile states."""
        self.tile_states.clear()
        self._save_tile_states()
    
    def draw_grid(self, frame):
        """
        Draw grid overlay with shaded tiles.
        
        Args:
            frame (np.ndarray): Input frame (BGR format)
        
        Returns:
            np.ndarray: Frame with grid overlay
        """
        overlay = frame.copy()
        
        # Draw shaded tiles (filled rectangles with state colors)
        for (tile_x, tile_y), state in self.tile_states.items():
            color = self.TILE_STATES.get(state, (0, 0, 255))
            x1 = int(tile_x * self.tile_width)
            y1 = int(tile_y * self.tile_height)
            x2 = int((tile_x + 1) * self.tile_width)
            y2 = int((tile_y + 1) * self.tile_height)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        
        # Draw vertical lines
        for col in range(self.GRID_WIDTH + 1):
            x = int(col * self.tile_width)
            x = min(x, self.frame_width - 1)
            cv2.line(overlay, (x, 0), (x, self.frame_height), self.grid_color, 1)
        
        # Draw horizontal lines
        for row in range(self.GRID_HEIGHT + 1):
            y = int(row * self.tile_height)
            y = min(y, self.frame_height - 1)
            cv2.line(overlay, (0, y), (self.frame_width, y), self.grid_color, 1)
        
        # Blend with original frame
        result = cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0)
        return result
    
    def adjust_tile_size(self, delta_x, delta_y=None):
        """Adjust tile dimensions."""
        if delta_y is None:
            delta_y = delta_x
        self.tile_width = max(2.0, self.tile_width + delta_x)
        self.tile_height = max(2.0, self.tile_height + delta_y)
    
    def adjust_alpha(self, delta):
        """Adjust overlay transparency."""
        self.alpha = np.clip(self.alpha + delta, 0.0, 1.0)
    
    def reset_to_defaults(self):
        """Reset grid parameters to defaults."""
        self.tile_width = self._default_tile_width
        self.tile_height = self._default_tile_height
        self.alpha = self._default_alpha
    
    def get_tile_at_pixel(self, pixel_x, pixel_y):
        """Get grid tile coordinates from pixel position."""
        if pixel_x < 0 or pixel_x >= self.frame_width or pixel_y < 0 or pixel_y >= self.frame_height:
            return None
        
        tile_x = int(pixel_x / self.tile_width)
        tile_y = int(pixel_y / self.tile_height)
        
        tile_x = min(tile_x, self.GRID_WIDTH - 1)
        tile_y = min(tile_y, self.GRID_HEIGHT - 1)
        
        return (tile_x, tile_y)
    
    def get_pixel_at_tile(self, tile_x, tile_y):
        """Get pixel coordinates of tile center."""
        if tile_x < 0 or tile_x >= self.GRID_WIDTH or tile_y < 0 or tile_y >= self.GRID_HEIGHT:
            return None
        
        pixel_x = int((tile_x + 0.5) * self.tile_width)
        pixel_y = int((tile_y + 0.5) * self.tile_height)
        
        return (pixel_x, pixel_y)
    
    def get_grid_info(self):
        """Get current grid configuration."""
        return {
            'grid_width': self.GRID_WIDTH,
            'grid_height': self.GRID_HEIGHT,
            'frame_width': self.frame_width,
            'frame_height': self.frame_height,
            'tile_width': self.tile_width,
            'tile_height': self.tile_height,
            'alpha': self.alpha,
            'tile_states': dict(self.tile_states)
        }


# Global grid instance for mouse callback
_grid_instance = None


def _mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks on the grid."""
    global _grid_instance
    if _grid_instance:
        tile = _grid_instance.get_tile_at_pixel(x, y)
        if tile:
            if event == cv2.EVENT_LBUTTONDOWN:
                # Left click: cycle through states
                new_state = _grid_instance.cycle_tile_state(tile[0], tile[1])
                print(f"Tile {tile} -> {new_state}")
            elif event == cv2.EVENT_RBUTTONDOWN:
                # Right click: clear tile
                _grid_instance.clear_tile(tile[0], tile[1])
                print(f"Tile {tile} cleared")


def interactive_grid_overlay(frame, grid_color=(0, 255, 0)):
    """
    Display frame with interactive grid overlay.
    
    Mouse Controls:
    - LEFT CLICK   : Cycle through tile states (red -> leftEnemyDown -> ... -> red)
    - RIGHT CLICK  : Clear tile shading
    
    Keyboard Controls:
    - 'c'          : Clear all shaded tiles
    - 'ESC'        : Exit
    
    Args:
        frame (np.ndarray): Input frame (BGR format)
        grid_color (tuple): Color for grid lines (BGR)
    
    Returns:
        dict: Final grid parameters
    """
    global _grid_instance
    
    height, width = frame.shape[:2]
    grid = TileGrid(width, height, grid_color=grid_color)
    _grid_instance = grid
    
    window_name = "Clash Royale 18x32 Grid - Click to cycle states, ESC to exit"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, _mouse_callback)
    
    running = True
    while running:
        display_frame = grid.draw_grid(frame)
        
        state_counts = {}
        for state in grid.STATE_ORDER:
            count = sum(1 for s in grid.tile_states.values() if s == state)
            state_counts[state] = count
        
        info_text = f"Total: {len(grid.tile_states)} | "
        info_text += " | ".join([f"{s}:{state_counts[s]}" for s in grid.STATE_ORDER])
        cv2.putText(display_frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        cv2.imshow(window_name, display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            print("Exiting grid adjustment...")
            running = False
        elif key == ord('c'):
            grid.clear_all_tiles()
            print("All tiles cleared")
    
    cv2.destroyAllWindows()
    _grid_instance = None
    
    return grid.get_grid_info()


def overlay_grid_on_video(video_path, output_path=None, grid_color=(0, 255, 0), alpha=0.3):
    """Overlay grid on an existing video file."""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return None
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    grid = TileGrid(frame_width, frame_height, alpha=alpha, grid_color=grid_color)
    
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_with_grid = grid.draw_grid(frame)
        
        if writer:
            writer.write(frame_with_grid)
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Processed {frame_count}/{total_frames} frames ({100*frame_count/total_frames:.1f}%)")
    
    cap.release()
    if writer:
        writer.release()
        print(f"Output video saved to {output_path}")
    
    return grid.get_grid_info()


if __name__ == '__main__':
    print("Testing 18x32 Clash Royale grid with multi-state tiles...")
    
    test_frame = np.zeros((960, 540, 3), dtype=np.uint8)
    test_frame[:] = (50, 50, 50)
    
    print("\nStarting interactive grid overlay...")
    print("Click tiles to cycle through states:")
    for state in TileGrid.STATE_ORDER:
        print(f"  - {state}")
    print()
    
    result = interactive_grid_overlay(test_frame)
    
    print(f"\nGrid: {result['grid_width']}x{result['grid_height']}")
    print(f"Tile size: {result['tile_width']:.1f}x{result['tile_height']:.1f}")
    print(f"Tile states: {result['tile_states']}")
