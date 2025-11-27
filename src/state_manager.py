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
    'Electro Giant': 8,
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


class StateManager:
    """
    Main state manager combining elixir tracking and card cycle.
    """
    
    def __init__(self):
        self.elixir_tracker = ElixirTracker()
        self.card_cycle = CardCycle()
        self.last_seen_boxes = {}  # Track last seen positions to prevent duplicates
        self.duplicate_threshold = 50  # pixels
        self.debounce_time = 3.0  # seconds
        
    def update(self, detections):
        """
        Process new detections and update state.
        
        Args:
            detections: List of dicts from RoboflowDetector.detect()
        """
        # Update elixir regeneration
        self.elixir_tracker.update()
        
        # Process each detection
        now = time.time()
        for det in detections:
            card_name = det['class']
            box = det['box']
            
            # Check if this is a duplicate (same card, same position)
            if self._is_duplicate(card_name, box, now):
                continue
            
            # New card detected!
            cost = self.elixir_tracker.spend(card_name)
            self.card_cycle.add_card(card_name)
            
            # Remember this detection
            self.last_seen_boxes[card_name] = {
                'box': box,
                'time': now
            }
            
            print(f"[DETECTION] {card_name} (Cost: {cost}, Elixir: {self.elixir_tracker.elixir:.1f})")
    
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
            'queue': list(self.card_cycle.queue)
        }
