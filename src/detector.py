import os
import requests
import base64
import cv2
from dotenv import load_dotenv

class RoboflowDetector:
    """
    Wrapper for Roboflow HTTP API (compatible with Python 3.13+).
    Detects Clash Royale troops and buildings using ML.
    """
    
    def __init__(self):
        """Initialize the Roboflow API with credentials from .env"""
        load_dotenv()
        
        api_key = os.getenv("ROBOFLOW_API_KEY")
        model_id = os.getenv("ROBOFLOW_MODEL_ID")
        
        if not api_key or not model_id:
            raise ValueError(
                "Missing required environment variables. "
                "Please create a .env file with ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID"
            )
        
        # Parse model ID (format: workspace/project/version)
        parts = model_id.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid MODEL_ID format. Expected 'project/version', got '{model_id}'")
        
        self.project_id = parts[0]
        self.version = parts[1]
        self.api_key = api_key
        
        # Build API endpoint
        self.api_url = f"https://detect.roboflow.com/{self.project_id}/{self.version}"
        
        print(f"Roboflow HTTP API initialized: {model_id}")
    
    def detect(self, frame):
        """
        Run object detection on a frame using HTTP API.
        
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
        
        # Encode frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Make API request
        try:
            response = requests.post(
                self.api_url,
                params={'api_key': self.api_key},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=img_base64,
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
            
            results = response.json()
            
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return []
        
        # Format results
        detections = []
        predictions = results.get('predictions', [])
        
        for pred in predictions:
            detections.append({
                'class': pred.get('class', 'Unknown'),
                'confidence': float(pred.get('confidence', 0)),
                'box': [
                    float(pred.get('x', 0)),
                    float(pred.get('y', 0)),
                    float(pred.get('width', 0)),
                    float(pred.get('height', 0))
                ]
            })
        
        return detections
