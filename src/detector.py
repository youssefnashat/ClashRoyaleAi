import cv2
import numpy as np
import os
import time
from .config import ARENA_ROI, MATCH_CONFIDENCE, DEBOUNCE_TIME

class CardDetector:
    def __init__(self, assets_dir="assets/cards"):
        self.templates = {}
        self.last_seen = {} # {card_name: timestamp}
        self.load_templates(assets_dir)

    def load_templates(self, assets_dir):
        if not os.path.exists(assets_dir):
            print(f"Warning: Assets directory {assets_dir} not found.")
            return

        for filename in os.listdir(assets_dir):
            if filename.endswith(".png"):
                name = os.path.splitext(filename)[0]
                path = os.path.join(assets_dir, filename)
                img = cv2.imread(path)
                if img is not None:
                    self.templates[name] = img
                else:
                    print(f"Failed to load {filename}")

    def detect(self, frame):
        """
        Scans the arena ROI for card templates.
        Returns a list of detected card names.
        """
        detected_cards = []
        if frame is None:
            return detected_cards

        x, y, w, h = ARENA_ROI
        if y+h > frame.shape[0] or x+w > frame.shape[1]:
            return detected_cards

        roi = frame[y:y+h, x:x+w]
        
        now = time.time()

        for name, template in self.templates.items():
            # Check debounce
            if name in self.last_seen:
                if now - self.last_seen[name] < DEBOUNCE_TIME:
                    continue

            # Template Matching
            # Ensure template is smaller than ROI
            if template.shape[0] > roi.shape[0] or template.shape[1] > roi.shape[1]:
                continue

            res = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            if max_val > MATCH_CONFIDENCE:
                detected_cards.append(name)
                self.last_seen[name] = now
                print(f"Detected {name} ({max_val:.2f})")

        return detected_cards
