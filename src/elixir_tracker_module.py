"""Elixir tracking and display module"""
import cv2
from src.config import ELIXIR_BAR_ROI
from src.vision import get_user_elixir, ElixirTracker


class ElixirDisplay:
    """Handles elixir tracking and rendering"""
    
    def __init__(self):
        self.tracker = ElixirTracker()
    
    def update(self):
        """Update tracker state"""
        self.tracker.update()
    
    def render(self, display_frame, screenshot):
        """Render elixir display on frame
        
        Args:
            display_frame: Frame to render on
            screenshot: Original screenshot for elixir detection
        
        Returns:
            Frame with elixir display rendered
        """
        # Get elixir estimate
        elixir = get_user_elixir(screenshot)
        
        # Draw elixir bar ROI bounding box (green)
        x, y, w, h = ELIXIR_BAR_ROI
        cv2.rectangle(display_frame, (x + 4, y), (x + w + 4, y + h), (0, 255, 0), 3)
        
        # Display ROI coordinates for reference
        cv2.putText(display_frame, f"ROI: ({x}, {y}, {w}, {h})", (x + 4, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Add elixir info overlay at bottom quarter
        frame_height = display_frame.shape[0]
        bottom_quarter_y = int(frame_height * 3 / 4)
        cv2.putText(display_frame, f"Elixir: {elixir:.1f}", (10, bottom_quarter_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return display_frame, elixir
