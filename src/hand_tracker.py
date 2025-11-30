import cv2
from src.detector import RoboflowDetector

class HandTracker:
    """
    Manages the detection of cards in the player's hand.
    Uses RoboflowDetector with the specific CARD_MODEL_ID.
    """
    
    def __init__(self, detector=None):
        """
        Args:
            detector (RoboflowDetector): Shared detector instance. If None, creates a new one.
        """
        if detector:
            self.detector = detector
        else:
            try:
                self.detector = RoboflowDetector()
            except Exception as e:
                print(f"HandTracker failed to init detector: {e}")
                self.detector = None

    def _get_slot_rois(self, frame_shape):
        """
        Calculate the ROIs for the 4 card slots with offsets.
        """
        height, width = frame_shape[:2]
        
        # Vertical: Move down by same amount we shrunk (approx 3%)
        # Previous: Height 13%, Y at 80%
        # New: Height 13%, Y at 83%?
        
        hand_height = int(height * 0.13) 
        hand_y = int(height * 0.83)      
        
        # Horizontal: Start 22%, End 98%
        start_x = int(width * 0.22)
        end_x = int(width * 0.98)
        
        available_width = end_x - start_x
        slot_width = available_width // 4
        
        # Margin 2%
        margin = int(slot_width * 0.02)
        
        rois = []
        for i in range(4):
            x = start_x + (i * slot_width) + margin
            w = slot_width - (2 * margin)
            rois.append((x, hand_y, w, hand_height))
            
        return rois

    def get_debug_frame(self, frame):
        """
        Draws debug visualization of the 4 slots.
        """
        if frame is None:
            return None
            
        debug_frame = frame.copy()
        rois = self._get_slot_rois(debug_frame.shape)
        
        for i, (x, y, w, h) in enumerate(rois):
            # Draw Cyan Rectangle
            cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
            
            # Label
            label = f"Slot {i+1}"
            cv2.putText(debug_frame, label, (x + 5, y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
        return debug_frame

    def get_hand_cards(self, frame):
        """
        Identifies cards in the 4 slots using separate API calls.
        
        Returns:
            list of strings: Names of cards in slots 1-4.
        """
        if frame is None or self.detector is None:
            return ["Unknown"] * 4
            
        rois = self._get_slot_rois(frame.shape)
        slot_cards = []
        
        for x, y, w, h in rois:
            crop = frame[y:y+h, x:x+w]
            
            # Detect cards in this specific slot crop
            detections = self.detector.detect_hand_cards(crop)
            
            if not detections:
                slot_cards.append("Empty")
                continue
                
            # If multiple detections in one slot, take the highest confidence
            best_det = max(detections, key=lambda d: d['confidence'])
            slot_cards.append(best_det['class'])
            
        return slot_cards
