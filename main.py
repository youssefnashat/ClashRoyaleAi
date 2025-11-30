import cv2
import time
from src.capture import WindowCapture
from src.detector import RoboflowDetector
from src.state_manager import StateManager

def main():
    """Main application loop for tower detection with popup visualization"""
    print("Initializing Clash Royale Princess Tower Detection...")
    
    cap = WindowCapture()
    
    try:
        detector = RoboflowDetector()
    except ValueError as e:
        print(f"ERROR: {e}")
        return
    
    state = StateManager()
    
    print("Waiting for game window...")
    while not cap.hwnd:
        cap.find_window()
        time.sleep(1)
    
    print("Window found! Tower detection started...")
    
    try:
        while True:
            frame = cap.get_screenshot()
            if frame is None:
                continue
            
            detections = detector.detect(frame)
            state.update(detections)
            visualize_towers(frame, detections, state)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        cv2.destroyAllWindows()


def visualize_towers(frame, detections, state):
    """Display frame with highlighted towers and their positions"""
    display_frame = frame.copy()
    
    # Get tower positions from state
    towers_by_pos = state.tower_tracker.get_towers_by_position()
    
    for det in detections:
        tower_class = det['class'].lower()
        
        # Only draw boxes for actual towers
        if 'princess' in tower_class and 'tower' in tower_class:
            box = det['box']
            x, y, width, height = box[0], box[1], box[2], box[3]
            
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)
            
            # Draw green box around tower
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Determine tower position based on coordinates
            side = "Left" if x < 225 else "Right"
            owner = "Enemy" if y < 400 else "Friendly"
            
            label = f"{side} {owner}"
            cv2.putText(display_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.imshow('Clash Royale - Tower Detection', display_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        raise KeyboardInterrupt()


if __name__ == "__main__":
    main()


