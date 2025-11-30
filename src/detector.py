import os
import requests
import base64
import cv2
from dotenv import load_dotenv
from src.config import TROOP_MODEL_ID, CARD_MODEL_ID

class RoboflowDetector:
    """
    Wrapper for Roboflow HTTP API.
    Handles multiple models: troops (arena), cards (hand), and towers.
    Compatible with Python 3.14+
    """
    
    def __init__(self, tower_model_id=None):
        """Initialize the Roboflow API with credentials from .env"""
        load_dotenv()
        
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Missing required environment variable ROBOFLOW_API_KEY. "
                "Please create a .env file."
            )
        
        self.api_url_base = "https://detect.roboflow.com"
        self.tower_model_id = tower_model_id or os.getenv("ROBOFLOW_MODEL_ID")
        
        print(f"Roboflow HTTP API initialized.")
        print(f"Troop Model: {TROOP_MODEL_ID}")
        print(f"Card Model: {CARD_MODEL_ID}")
        if self.tower_model_id:
            print(f"Tower Model: {self.tower_model_id}")

    def _detect_with_model(self, frame, model_id):
        """
        Generic detection method using HTTP API.
        """
        if frame is None or not model_id:
            return []
            
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            url = f"{self.api_url_base}/{model_id}"
            response = requests.post(
                url,
                params={'api_key': self.api_key},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=img_base64,
                timeout=2
            )
            
            if response.status_code != 200:
                return []
            
            result = response.json()
            predictions = result.get('predictions', [])
            
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
            
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return []
        except Exception as e:
            print(f"Detection error: {e}")
            return []

    def detect_troops(self, frame):
        """
        Detect troops on the battlefield using TROOP_MODEL_ID.
        """
        return self._detect_with_model(frame, TROOP_MODEL_ID)

    def detect_hand_cards(self, frame):
        """
        Detect cards in the player's hand using CARD_MODEL_ID.
        """
        return self._detect_with_model(frame, CARD_MODEL_ID)

    def detect_towers(self, frame):
        """
        Detect princess towers using the tower model.
        """
        return self._detect_with_model(frame, self.tower_model_id)

    def detect(self, frame):
        """
        Generic detect method that detects troops (main detection for overlays).
        """
        return self.detect_troops(frame)