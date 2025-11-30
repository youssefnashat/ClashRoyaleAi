"""
State Manager for Princess Tower Detection and Tracking
Tracks tower health, position, and state changes
"""

import time

# Tower sides - determined by X position
TOWER_SIDE_LEFT = 'left'
TOWER_SIDE_RIGHT = 'right'

# Tower ownership - determined by Y position
TOWER_OWNER_FRIENDLY = 'friendly'
TOWER_OWNER_ENEMY = 'enemy'


def determine_tower_side(x_position, frame_width=450):
    """
    Determine if tower is on left or right side based on X coordinate.
    
    Args:
        x_position: Center X coordinate of tower
        frame_width: Width of frame (default 450 from config)
    
    Returns:
        'left' or 'right'
    """
    return TOWER_SIDE_LEFT if x_position < frame_width / 2 else TOWER_SIDE_RIGHT


def determine_tower_owner(y_position, frame_height=800):
    """
    Determine if tower is friendly or enemy based on Y coordinate.
    
    Args:
        y_position: Center Y coordinate of tower
        frame_height: Height of frame (default 800 from config)
    
    Returns:
        'friendly' or 'enemy'
    """
    # Enemy towers are in top half (y < frame_height/2)
    # Friendly towers are in bottom half (y >= frame_height/2)
    return TOWER_OWNER_ENEMY if y_position < frame_height / 2 else TOWER_OWNER_FRIENDLY


class PrincessTower:
    """Represents a single princess tower"""
    
    def __init__(self, tower_id, x, y, confidence, frame_width=450, frame_height=800):
        self.id = tower_id
        self.x = x
        self.y = y
        self.confidence = confidence
        self.side = determine_tower_side(x, frame_width)
        self.owner = determine_tower_owner(y, frame_height)
        self.status = 'active'
        self.last_seen = time.time()
    
    def update(self, x, y, confidence):
        """Update tower with new detection"""
        self.x = x
        self.y = y
        self.confidence = confidence
        self.last_seen = time.time()


class PrincessTowerTracker:
    """
    Tracks princess towers only, categorized by left/right and friendly/enemy.
    """
    
    def __init__(self, frame_width=450, frame_height=800):
        self.towers = {}
        self.tower_id_counter = 0
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.debounce_threshold = 100
        self.last_update = time.time()
        
        self.previous_states = {
            'rightEnemyDown': False,
            'leftEnemyDown': False,
            'leftFriendlyDown': False,
            'rightFriendlyDown': False,
        }
        
        self.state_changes = {
            'rightEnemyDown': None,
            'leftEnemyDown': None,
            'leftFriendlyDown': None,
            'rightFriendlyDown': None,
        }
    
    def update(self, detections):
        """Process new detections and update princess tower tracking"""
        now = time.time()
        self.last_update = now
        self._cleanup_old_towers(now)
        
        seen_positions = {}
        deduped_detections = []
        
        for det in detections:
            tower_class = det['class'].lower()
            if not ('princess' in tower_class and 'tower' in tower_class):
                continue
            
            box = det['box']
            x, y = box[0], box[1]
            pos_key = (round(x / 10) * 10, round(y / 10) * 10)
            
            if pos_key not in seen_positions:
                seen_positions[pos_key] = det
                deduped_detections.append(det)
        
        for det in deduped_detections:
            confidence = det['confidence']
            box = det['box']
            x, y = box[0], box[1]
            
            matched_tower_id = self._find_matching_tower(x, y, now)
            
            if matched_tower_id is not None:
                self.towers[matched_tower_id].update(x, y, confidence)
            else:
                self.tower_id_counter += 1
                self.towers[self.tower_id_counter] = PrincessTower(
                    self.tower_id_counter, x, y, confidence,
                    self.frame_width, self.frame_height
                )
        
        self._cleanup_old_towers(now)
    
    def _find_matching_tower(self, x, y, now):
        """Find if detection matches an existing tower"""
        best_match = None
        best_distance = self.debounce_threshold
        
        for tower_id, tower in self.towers.items():
            # Must be same side and owner
            if tower.side != determine_tower_side(x, self.frame_width):
                continue
            if tower.owner != determine_tower_owner(y, self.frame_height):
                continue
            
            # Find closest tower of this type
            distance = ((x - tower.x)**2 + (y - tower.y)**2)**0.5
            if distance < best_distance:
                best_distance = distance
                best_match = tower_id
        
        return best_match
    
    def _cleanup_old_towers(self, now, timeout=1.0):
        """Mark towers as destroyed if not detected recently"""
        for tid, t in self.towers.items():
            if now - t.last_seen > timeout and t.status != 'destroyed':
                t.status = 'destroyed'
    
    def _is_tower_down(self, tower_list):
        """Check if any tower in the list is down"""
        for tower in tower_list:
            if tower.status == 'destroyed':
                return True
        return False
    
    def get_towers_by_position(self):
        """Get towers organized by position"""
        return {
            'enemy_left': [t for t in self.towers.values()
                          if t.owner == TOWER_OWNER_ENEMY and t.side == TOWER_SIDE_LEFT],
            'enemy_right': [t for t in self.towers.values()
                           if t.owner == TOWER_OWNER_ENEMY and t.side == TOWER_SIDE_RIGHT],
            'friendly_left': [t for t in self.towers.values()
                             if t.owner == TOWER_OWNER_FRIENDLY and t.side == TOWER_SIDE_LEFT],
            'friendly_right': [t for t in self.towers.values()
                              if t.owner == TOWER_OWNER_FRIENDLY and t.side == TOWER_SIDE_RIGHT],
        }
    
    def get_tower_states(self):
        """Get the 4 tower states as booleans (True if tower is down)"""
        towers_by_pos = self.get_towers_by_position()
        
        current_states = {
            'rightEnemyDown': self._is_tower_down(towers_by_pos['enemy_right']),
            'leftEnemyDown': self._is_tower_down(towers_by_pos['enemy_left']),
            'leftFriendlyDown': self._is_tower_down(towers_by_pos['friendly_left']),
            'rightFriendlyDown': self._is_tower_down(towers_by_pos['friendly_right']),
        }
        
        for key in self.state_changes:
            self.state_changes[key] = None
        
        for state_key, current_value in current_states.items():
            previous_value = self.previous_states.get(state_key, False)
            if current_value and not previous_value:
                self.state_changes[state_key] = 'down'
            elif not current_value and previous_value:
                self.state_changes[state_key] = 'up'
        
        self.previous_states = current_states.copy()
        return current_states


class StateManager:
    """Main state manager for tower detection"""
    
    def __init__(self, frame_width=450, frame_height=800):
        self.tower_tracker = PrincessTowerTracker(frame_width, frame_height)
    
    def update(self, detections):
        """Update state with new detections"""
        self.tower_tracker.update(detections)
    
    def get_tower_states(self):
        """Get current tower states"""
        return self.tower_tracker.get_tower_states()
