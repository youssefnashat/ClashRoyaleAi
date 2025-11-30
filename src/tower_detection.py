"""Tower detection module - optional feature for detecting princess towers"""
import cv2
from src.detector import RoboflowDetector
from src.state_manager import StateManager


class TowerDetectionOverlay:
    """Handles tower detection and visualization with state tracking"""
    
    def __init__(self, frame_width=450, frame_height=800):
        """Initialize tower detection
        
        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
        """
        try:
            self.detector = RoboflowDetector()
            self.state_manager = StateManager(frame_width, frame_height)
            self.confidence_threshold = 0.4
            self.detections_cache = []
            self.frame_width = frame_width
            self.frame_height = frame_height
        except Exception as e:
            print(f"[ERROR] Failed to initialize TowerDetectionOverlay: {e}")
            raise
    
    def process_frame(self, frame):
        """Process frame for tower detection
        
        Args:
            frame: Input video frame
        
        Returns:
            Tuple of (detections list, display frame with towers highlighted)
        """
        if frame is None:
            return [], frame.copy() if frame is not None else None
        
        try:
            # Run tower detection using the detector's detect_towers method
            detections = self.detector.detect_towers(frame)
            self.detections_cache = detections if detections else []
            
            # Update state with new detections
            if self.state_manager and detections:
                self.state_manager.update(detections)
            
            # Visualize towers
            display_frame = self._visualize_towers(frame.copy(), detections if detections else [])
            
            return detections if detections else [], display_frame
        except Exception as e:
            print(f"[ERROR] Tower detection processing failed: {e}")
            return [], frame.copy()
    
    def get_tower_states(self):
        """Get current tower states (which towers are down)
        
        Returns:
            Dict with keys: LE (left enemy), RE (right enemy), 
                           LF (left friendly), RF (right friendly)
        """
        try:
            return self.state_manager.get_tower_states()
        except:
            return {}
    
    def _visualize_towers(self, frame, detections):
        """Draw tower bounding boxes and labels on frame
        
        Args:
            frame: Frame to draw on
            detections: List of detections from API
        
        Returns:
            Frame with towers highlighted
        """
        display_frame = frame.copy()
        
        if not detections:
            return display_frame
        
        for det in detections:
            try:
                tower_class = det.get('class', '').lower()
                confidence = float(det.get('confidence', 0))
                
                # Only draw boxes for actual towers with sufficient confidence
                if ('princess' in tower_class and 'tower' in tower_class and 
                    confidence >= self.confidence_threshold):
                    
                    box = det.get('box', [0, 0, 0, 0])
                    x = float(box[0]) if len(box) > 0 else 0
                    y = float(box[1]) if len(box) > 1 else 0
                    width = float(box[2]) if len(box) > 2 else 0
                    height = float(box[3]) if len(box) > 3 else 0
                    
                    x1 = int(x - width / 2)
                    y1 = int(y - height / 2)
                    x2 = int(x + width / 2)
                    y2 = int(y + height / 2)

                    # Draw green box around tower
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Determine tower position based on coordinates
                    side = "Left" if x < self.frame_width / 2 else "Right"
                    owner = "Enemy" if y < self.frame_height / 2 else "Friendly"

                    label = f"{side} {owner} ({confidence:.2f})"
                    cv2.putText(display_frame, label, (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            except Exception as e:
                print(f"[WARNING] Error drawing tower: {e}")
                continue
        
        return display_frame
