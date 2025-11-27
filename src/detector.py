import os
from dotenv import load_dotenv
from inference import get_model

class RoboflowDetector:
    """
    Wrapper for Roboflow inference API.
    Detects Clash Royale troops and buildings using ML.
    """
    
    def __init__(self):
        """Initialize the Roboflow model with credentials from .env"""
        load_dotenv()
        
        api_key = os.getenv("ROBOFLOW_API_KEY")
        model_id = os.getenv("ROBOFLOW_MODEL_ID")
        
        if not api_key or not model_id:
            raise ValueError(
                "Missing required environment variables. "
                "Please create a .env file with ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID"
            )
        
        print(f"Loading Roboflow model: {model_id}")
        self.model = get_model(model_id=model_id, api_key=api_key)
        print("Model loaded successfully!")
    
    def detect(self, frame):
        """
        Run object detection on a frame.
        
        Args:
            frame (numpy.ndarray): BGR image from OpenCV/WindowCapture
        
        Returns:
            list[dict]: Detected objects with format:
                [
                    {
                        'class': 'Hog Rider',
                        'confidence': 0.88,
                        'box': [x, y, width, height]  # center coords + dimensions
                    },
                    ...
                ]
        """
        if frame is None:
            return []
        
        # Run inference
        results = self.model.infer(frame)
        
        # Format results
        detections = []
        predictions = results.get('predictions', []) if isinstance(results, dict) else results
        
        for pred in predictions:
            detections.append({
                'class': pred.get('class', pred.get('class_name', 'Unknown')),
                'confidence': float(pred.get('confidence', 0)),
                'box': [
                    float(pred.get('x', 0)),
                    float(pred.get('y', 0)),
                    float(pred.get('width', 0)),
                    float(pred.get('height', 0))
                ]
            })
        
        return detections
