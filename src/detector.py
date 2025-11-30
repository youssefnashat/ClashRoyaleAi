import os
import cv2
import base64
import requests
import numpy as np
from dotenv import load_dotenv
from src.config import TROOP_MODEL_ID, CARD_MODEL_ID

class RoboflowDetector:
    """
    Wrapper for Roboflow API using direct HTTP requests.
    Handles dual models: one for troops (arena) and one for cards (hand).
    """
    
    def __init__(self):
        """Initialize the Roboflow API with credentials from .env"""
        load_dotenv()
        
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        self.base_url = "https://detect.roboflow.com"
        
        if not self.api_key:
            raise ValueError(
                "Missing required environment variable ROBOFLOW_API_KEY. "
                "Please create a .env file."
            )
            
        print(f"Roboflow Detector initialized (HTTP).")
        print(f"Troop Model: {TROOP_MODEL_ID}")
        print(f"Card Model: {CARD_MODEL_ID}")

    def _encode_image(self, frame):
        """Convert OpenCV frame to base64 string."""
        try:
            # Encode frame as JPEG
            retval, buffer = cv2.imencode('.jpg', frame)
            if not retval:
                return None
            # Convert to base64 string
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            return jpg_as_text
        except Exception as e:
            print(f"Image encoding failed: {e}")
            return None

    def _infer(self, frame, model_id):
        """Make HTTP POST request to Roboflow API."""
        if frame is None:
            return []
            
        encoded_image = self._encode_image(frame)
        if not encoded_image:
            return []

        # Construct URL
        # model_id format: workspace/project/version or project/version
        # API expects: https://detect.roboflow.com/project/version?api_key=...
        # If model_id has 3 parts (workspace/project/version), we might need to adjust.
        # Usually standard model_id works if appended.
        
        # Clean model ID if needed (remove workspace if present, though usually fine)
        # Let's try direct appending first.
        
        url = f"{self.base_url}/{model_id}"
        params = {
            "api_key": self.api_key,
            "confidence": 40, # Default confidence
            "overlap": 30,    # Default overlap
            "format": "json"
        }
        
        try:
            response = requests.post(
                url, 
                params=params, 
                data=encoded_image,
                headers={"Content-Type": "application/x-www-form-urlencoded"} 
            )
            
            if response.status_code != 200:
                print(f"API Error {response.status_code}: {response.text}")
                return []
                
            result = response.json()
            return result.get('predictions', [])
            
        except Exception as e:
            print(f"Inference request failed: {e}")
            return []

    def detect_troops(self, frame):
        """
        Detect troops on the battlefield using TROOP_MODEL_ID.
        """
        predictions = self._infer(frame, TROOP_MODEL_ID)
        
        detections = []
        for pred in predictions:
            # API returns x, y (center), width, height
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

    def detect_hand_cards(self, frame):
        """
        Detect cards in the player's hand using CARD_MODEL_ID.
        """
        predictions = self._infer(frame, CARD_MODEL_ID)
        
        detections = []
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
