import cv2
import time
from src.capture import WindowCapture
from src.detector import RoboflowDetector
from src.state_manager import StateManager

def main():
    """
    Main application loop for Clash Royale AI
    """
    print("=" * 50)
    print("Clash Royale AI - Roboflow Edition")
    print("=" * 50)
    print()
    
    # Initialize components
    print("[1/3] Initializing window capture...")
    cap = WindowCapture()
    
    print("[2/3] Loading Roboflow model...")
    try:
        detector = RoboflowDetector()
    except ValueError as e:
        print(f"\n ERROR: {e}")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your ROBOFLOW_API_KEY from https://app.roboflow.com/settings/api")
        print("3. Verify ROBOFLOW_MODEL_ID is correct (currently: clash-royale-xy2jw/2)")
        return
    
    print("[3/3] Initializing state tracker...")
    state = StateManager()
    
    # Wait for window
    print("\nWaiting for game window...")
    while not cap.hwnd:
        cap.find_window()
        time.sleep(1)
    
    print("Window found! Starting detection loop...")
    print("Press 'q' to quit\n")
    print("=" * 50)
    
    # Main loop
    frame_count = 0
    last_print = time.time()
    
    try:
        while True:
            # Capture frame
            frame = cap.get_screenshot()
            if frame is None:
                time.sleep(0.1)
                continue
            
            # Run detection every frame
            detections = detector.detect(frame)
            
            # Update state
            state.update(detections)
            
            # Print dashboard every 2 seconds
            now = time.time()
            if now - last_print >= 2.0:
                print_dashboard(state, detections, frame_count)
                last_print = now
            
            frame_count += 1
            
            # Small delay to prevent 100% CPU usage
            time.sleep(0.05)
            
            # Check for quit (this won't work without a cv2.imshow window)
            # You could add a cv2.imshow here if you want visual feedback
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    

def print_dashboard(state, detections, frame_count):
    """Print a simple text dashboard"""
    import os
    
    # Clear console (Windows)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    current_state = state.get_state()
    
    print("=" * 50)
    print("CLASH ROYALE AI - ROBOFLOW EDITION")
    print("=" * 50)
    print()
    print(f"Frame: {frame_count}")
    print(f"Opponent Elixir: {current_state['elixir']:.1f} / 10.0")
    print()
    
    print("--- ACTIVE DETECTIONS ---")
    if detections:
        for det in detections:
            print(f"  • {det['class']} ({det['confidence']:.2f})")
    else:
        print("  (none)")
    print()
    
    print("--- KNOWN OPPONENT CARDS ---")
    if current_state['known_cards']:
        print(f"  {len(current_state['known_cards'])}/8 cards discovered:")
        for card in sorted(current_state['known_cards']):
            print(f"  • {card}")
    else:
        print("  (none)")
    print()
    
    print("Press Ctrl+C to quit")
    print("=" * 50)


if __name__ == "__main__":
    main()
