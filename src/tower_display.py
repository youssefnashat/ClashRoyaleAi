"""
Tower Detection Module - Simplified wrapper for tower detection feature
"""

import cv2
import os
from dotenv import load_dotenv


class TowerDisplay:
    """Simplified tower detection display - wraps detector for consistent interface"""
    
    def __init__(self, frame_width=450, frame_height=800):
        """Initialize tower detection
        
        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
        """
        load_dotenv()
        
        # Import here to avoid circular imports
        try:
            from src.detector import RoboflowDetector
            from src.state_manager import StateManager
            
            self.detector = RoboflowDetector()
            self.state_manager = StateManager(frame_width, frame_height)
            self.frame_width = frame_width
            self.frame_height = frame_height
            self.confidence_threshold = 0.4
            self.detections_cache = []
            self.enabled = True
        except Exception as e:
            print(f"[WARNING] Tower detection initialization warning: {e}")
            self.enabled = False
    
    def update(self):
        """Update method for consistency with other modules"""
        pass
    
    def process_frame(self, frame):
        """Process frame for tower detection and visualization
        
        Args:
            frame: Input video frame
            
        Returns:
            Tuple of (display_frame, detections)
        """
        if not self.enabled or frame is None:
            return frame.copy() if frame is not None else None, []
        
        try:
            display_frame = frame.copy()
            
            # Get the Roboflow model ID from environment
            tower_model_id = os.getenv("ROBOFLOW_MODEL_ID")
            if not tower_model_id:
                return display_frame, []
            
            # Run tower detection
            detections = self.detector.detect_towers(frame)
            self.detections_cache = detections if detections else []
            
            # Update state
            if self.state_manager and detections:
                self.state_manager.update(detections)
            
            # Visualize towers on display frame
            display_frame = self._draw_towers(display_frame, detections)
            
            return display_frame, detections
            
        except Exception as e:
            print(f"[WARNING] Tower detection error: {e}")
            return frame.copy() if frame is not None else None, []
    
    def _draw_towers(self, frame, detections):
        """Draw tower detections on frame
        
        Args:
            frame: Frame to draw on
            detections: List of tower detections
            
        Returns:
            Frame with towers drawn
        """
        if not detections:
            return frame
        
        display = frame.copy()
        
        for det in detections:
            try:
                tower_class = det.get('class', '').lower()
                confidence = float(det.get('confidence', 0))
                
                # Filter for princess towers with confidence threshold
                if not ('princess' in tower_class and 'tower' in tower_class):
                    continue
                
                if confidence < self.confidence_threshold:
                    continue
                
                # Extract box coordinates
                box = det.get('box', [0, 0, 0, 0])
                x = float(box[0])
                y = float(box[1])
                width = float(box[2])
                height = float(box[3])
                
                # Convert center coordinates to corners
                x1 = int(x - width / 2)
                y1 = int(y - height / 2)
                x2 = int(x + width / 2)
                y2 = int(y + height / 2)
                
                # Draw bounding box
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Determine tower position
                side = "L" if x < self.frame_width / 2 else "R"
                owner = "E" if y < self.frame_height / 2 else "F"
                
                # Draw label
                label = f"{side}{owner} {confidence:.2f}"
                cv2.putText(display, label, (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
            except Exception as e:
                continue
        
        return display
    
    def get_tower_states(self):
        """Get current tower states"""
        if self.state_manager:
            try:
                return self.state_manager.get_tower_states()
            except:
                pass
        return {}
