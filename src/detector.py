import os
import requests
import base64
import cv2
from dotenv import load_dotenv

class RoboflowDetector:
    """Wrapper for Roboflow HTTP API for princess tower detection"""
    
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
        
        parts = model_id.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid MODEL_ID format. Expected 'project/version', got '{model_id}'")
        
        self.project_id = parts[0]
        self.version = parts[1]
        self.api_key = api_key
        self.api_url = f"https://detect.roboflow.com/{self.project_id}/{self.version}"
        
        print(f"Roboflow Tower Detection API initialized: {model_id}")
    
    def detect(self, frame):
        """Run princess tower detection on a frame"""
        if frame is None:
            return []
        
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        try:
            response = requests.post(
                self.api_url,
                params={'api_key': self.api_key},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=img_base64,
                timeout=2
            )
            
            if response.status_code != 200:
                return []
            
            results = response.json()
        except requests.RequestException:
            return []
        
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
