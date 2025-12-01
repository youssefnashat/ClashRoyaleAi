import time
from collections import deque

# Card cost database for Clash Royale
CARD_COSTS = {
    # Troops
    'Knight': 3,
    'Archers': 3,
    'Goblins': 2,
    'Giant': 5,
    'P.E.K.K.A': 7,
    'Minions': 3,
    'Balloon': 5,
    'Witch': 5,
    'Barbarians': 5,
    'Golem': 8,
    'Skeletons': 1,
    'Valkyrie': 4,
    'Skeleton Army': 3,
    'Bomber': 2,
    'Musketeer': 4,
    'Baby Dragon': 4,
    'Prince': 5,
    'Wizard': 5,
    'Mini P.E.K.K.A': 4,
    'Hog Rider': 4,
    'Minion Horde': 5,
    'Ice Wizard': 3,
    'Royal Giant': 6,
    'Guards': 3,
    'Princess': 3,
    'Dark Prince': 4,
    'Three Musketeers': 9,
    'Lava Hound': 7,
    'Ice Spirit': 1,
    'Fire Spirit': 1,
    'Miner': 3,
    'Sparky': 6,
    'Bowler': 5,
    'Lumberjack': 4,
    'Battle Ram': 4,
    'Inferno Dragon': 4,
    'Ice Golem': 2,
    'Mega Minion': 3,
    'Dart Goblin': 3,
    'Goblin Gang': 3,
    'Electro Wizard': 4,
    'Elite Barbarians': 6,
    'Hunter': 4,
    'Executioner': 5,
    'Bandit': 3,
    'Royal Recruit': 7,
    'Night Witch': 4,
    'Bats': 2,
    'Royal Ghost': 3,
    'Ram Rider': 5,
    'Zappies': 4,
    'Rascals': 5,
    'Cannon Cart': 5,
    'Mega Knight': 7,
    'Skeleton Barrel': 3,
    'Flying Machine': 4,
    'Wall Breakers': 2,
    'Royal Hogs': 5,
    'Goblin Giant': 6,
    'Fisherman': 3,
    'Magic Archer': 4,
    'Electro Dragon': 5,
    'Firecracker': 3,
    'Elixir Golem': 3,
    'Battle Healer': 4,
    'Skeleton Dragons': 4,
    'Mother Witch': 4,
    'Electro Spirit': 1,
    'Electro Giant': 7,
    'Golden Knight': 4,
    'Archer Queen': 5,
    'Skeleton King': 4,
    'Mighty Miner': 4,
    'Phoenix': 4,
    'Monk': 5,
    'Little Prince': 3,
    
    # Spells
    'Fireball': 4,
    'Arrows': 3,
    'Rage': 2,
    'Rocket': 6,
    'Goblin Barrel': 3,
    'Freeze': 4,
    'Mirror': 0,  # Variable cost
    'Lightning': 6,
    'Zap': 2,
    'Poison': 4,
    'Graveyard': 5,
    'The Log': 2,
    'Tornado': 3,
    'Clone': 3,
    'Earthquake': 3,
    'Barbarian Barrel': 2,
    'Heal Spirit': 1,
    'Giant Snowball': 2,
    'Royal Delivery': 3,
    
    # Buildings
    'Cannon': 3,
    'Goblin Hut': 5,
    'Mortar': 4,
    'Inferno Tower': 5,
    'Bomb Tower': 4,
    'Barbarian Hut': 6,
    'Tesla': 4,
    'Elixir Collector': 6,
    'X-Bow': 6,
    'Tombstone': 3,
    'Furnace': 4,
    'Goblin Cage': 4,
    'Goblin Drill': 4,
}

# Elixir regeneration constants
ELIXIR_REGEN_SINGLE = 0.35  # Elixir per second in normal time
ELIXIR_REGEN_DOUBLE = 0.70  # Elixir per second in double elixir
ELIXIR_MAX = 10.0
ELIXIR_START = 5.0

# Tower sides - determined by X position
TOWER_SIDE_LEFT = 'left'
TOWER_SIDE_RIGHT = 'right'

# Tower ownership - determined by Y position
TOWER_OWNER_FRIENDLY = 'friendly'
TOWER_OWNER_ENEMY = 'enemy'


def determine_tower_side(x_position, frame_width=450):
    return TOWER_SIDE_LEFT if x_position < frame_width / 2 else TOWER_SIDE_RIGHT


def determine_tower_owner(y_position, frame_height=800):
    return TOWER_OWNER_ENEMY if y_position < frame_height / 2 else TOWER_OWNER_FRIENDLY


class ElixirTracker:
    """
    Tracks opponent's estimated elixir based on time and card usage.
    """
    
    def __init__(self):
        self.elixir = ELIXIR_START
        self.last_update = time.time()
        self.double_elixir_mode = False
        
    def update(self):
        """Update elixir based on time elapsed"""
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        
        # Regenerate elixir
        rate = ELIXIR_REGEN_DOUBLE if self.double_elixir_mode else ELIXIR_REGEN_SINGLE
        self.elixir += rate * dt
        
        # Clamp to max
        if self.elixir > ELIXIR_MAX:
            self.elixir = ELIXIR_MAX
    
    def spend(self, card_name):
        """Deduct elixir for a played card"""
        cost = CARD_COSTS.get(card_name, 4)  # Default to 4 if unknown
        self.elixir -= cost
        
        # Prevent negative elixir
        if self.elixir < 0:
            self.elixir = 0
        
        return cost


class CardCycle:
    """
    Tracks opponent's card cycle and known cards.
    """
    
    def __init__(self):
        self.known_cards = set()  # All unique cards seen (max 8)
        self.hand = []  # Estimated 4-card hand
        self.queue = deque(maxlen=4)  # 4-card queue
        
    def add_card(self, card_name):
        """Add a card to known cards and update cycle"""
        # Add to known deck
        self.known_cards.add(card_name)
        
        # If we know all 8 cards, track the cycle
        if len(self.known_cards) >= 8:
            # Add to queue
            self.queue.append(card_name)
            
            # If queue is full, oldest card goes to hand
            if len(self.queue) >= 4 and len(self.hand) < 4:
                self.hand.append(self.queue.popleft())


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
            'RE': False,
            'LE': False,
            'LF': False,
            'RF': False,
        }
        
        self.state_changes = {
            'RE': None,
            'LE': None,
            'LF': None,
            'RF': None,
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
            'RE': self._is_tower_down(towers_by_pos['enemy_right']),
            'LE': self._is_tower_down(towers_by_pos['enemy_left']),
            'LF': self._is_tower_down(towers_by_pos['friendly_left']),
            'RF': self._is_tower_down(towers_by_pos['friendly_right']),
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


# Objects to ignore (towers, non-playable cards)
IGNORED_OBJECTS = {
    'Princess Tower',
    'King Tower',
    'Crown Tower',
    'King',
    'Princess',  # Ambiguous - could be card or tower
}

class StateManager:
    """
    Main state manager combining elixir tracking, card cycle, and tower tracking.
    """
    
    def __init__(self, frame_width=450, frame_height=800):
        self.elixir_tracker = ElixirTracker()
        self.card_cycle = CardCycle()
        self.tower_tracker = PrincessTowerTracker(frame_width, frame_height)
        self.last_seen_boxes = {}  # Track last seen positions to prevent duplicates
        self.duplicate_threshold = 50  # pixels
        self.debounce_time = 3.0  # seconds
        self.frame_height = frame_height
        
    def update(self, detections):
        """
        Process new detections and update state.
        
        Args:
            detections: List of dicts from RoboflowDetector.detect()
        """
        # Update elixir regeneration
        self.elixir_tracker.update()
        
        # Update towers
        self.tower_tracker.update(detections)
        
        # Process each detection for troops/cards
        now = time.time()
        for det in detections:
            card_name = det['class']
            box = det['box']
            
            # FILTER 1: Ignore towers (handled by tower_tracker)
            if 'tower' in card_name.lower() or card_name in IGNORED_OBJECTS:
                continue
            
            # FILTER 2: Only track enemy troops (top half of screen)
            # In Clash Royale, enemy side is top half (y < frame_height/2)
            y_position = box[1]  # Center Y coordinate
            if y_position > self.frame_height / 2:
                # Bottom half = our troops, ignore
                continue
            
            # Check if this is a duplicate (same card, same position)
            if self._is_duplicate(card_name, box, now):
                continue
            
            # New ENEMY card detected!
            cost = self.elixir_tracker.spend(card_name)
            self.card_cycle.add_card(card_name)
            
            # Remember this detection
            self.last_seen_boxes[card_name] = {
                'box': box,
                'time': now
            }
            
            print(f"[ENEMY DETECTION] {card_name} (Cost: {cost}, Elixir: {self.elixir_tracker.elixir:.1f})")
    
    def _is_duplicate(self, card_name, box, now):
        """Check if detection is a duplicate of a recent one"""
        if card_name not in self.last_seen_boxes:
            return False
        
        last = self.last_seen_boxes[card_name]
        
        # Check time debounce
        if now - last['time'] < self.debounce_time:
            # Check position similarity
            last_box = last['box']
            distance = ((box[0] - last_box[0])**2 + (box[1] - last_box[1])**2)**0.5
            
            if distance < self.duplicate_threshold:
                return True  # Same card, same place, recent = duplicate
        
        return False
    
    def get_state(self):
        """Get current state for display"""
        return {
            'elixir': self.elixir_tracker.elixir,
            'known_cards': list(self.card_cycle.known_cards),
            'hand': self.card_cycle.hand,
            'queue': list(self.card_cycle.queue),
            'towers': self.tower_tracker.get_tower_states()
        }
    
    def get_tower_states(self):
        """Get current tower states (proxy to tower_tracker)"""
        return self.tower_tracker.get_tower_states()
