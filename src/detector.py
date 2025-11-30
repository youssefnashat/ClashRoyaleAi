import os
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
from src.config import TROOP_MODEL_ID, CARD_MODEL_ID

class RoboflowDetector:
    """
    Wrapper for Roboflow Inference SDK.
    Handles dual models: one for troops (arena) and one for cards (hand).
    """
    
    def __init__(self):
        """Initialize the Roboflow API with credentials from .env"""
        load_dotenv()
        
        self.api_key = os.getenv("ROBOFLOW_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Missing required environment variable ROBOFLOW_API_KEY. "
                "Please create a .env file."
            )
        
        try:
            self.client = InferenceHTTPClient(
                api_url="https://detect.roboflow.com",
                api_key=self.api_key
            )
            print(f"Roboflow SDK initialized.")
            print(f"Troop Model: {TROOP_MODEL_ID}")
            print(f"Card Model: {CARD_MODEL_ID}")
            
        except Exception as e:
            print(f"Failed to initialize InferenceHTTPClient: {e}")
            self.client = None

    def detect_troops(self, frame):
        """
        Detect troops on the battlefield using TROOP_MODEL_ID.
        """
        if frame is None or self.client is None:
            return []
            
        try:
            # inference_sdk returns a dict with 'predictions' list
            result = self.client.infer(frame, model_id=TROOP_MODEL_ID)
            
            # Handle batch response (list) vs single response (dict)
            if isinstance(result, list):
                result = result[0]
                
            predictions = result.get('predictions', [])
            
            # Format to match previous API if needed, or just return predictions
            # Previous API returned list of dicts with 'class', 'confidence', 'box'
            # SDK returns 'class', 'confidence', 'x', 'y', 'width', 'height'
            
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
            
        except Exception as e:
            print(f"Troop detection failed: {e}")
            return []

    def detect_hand_cards(self, frame):
        """
        Detect cards in the player's hand using CARD_MODEL_ID.
        """
        if frame is None or self.client is None:
            return []
            
        try:
            result = self.client.infer(frame, model_id=CARD_MODEL_ID)
            
            if isinstance(result, list):
                result = result[0]
                
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
            
        except Exception as e:
            print(f"Card detection failed: {e}")
            return []
