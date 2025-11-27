from collections import deque

class OpponentState:
    def __init__(self):
        # Standard Clash Royale Deck is 8 cards
        # We start knowing nothing.
        self.known_cards = set() # All unique cards seen so far (max 8)
        
        # The Cycle
        self.hand = [] # Max 4 cards (estimated)
        self.queue = deque() # Cards waiting to come back to hand
        
        # If we don't know the full deck, we assume played cards come from "Unknown"
        # until we see 8 unique cards.

    def on_card_played(self, card_name, cost=0):
        """
        Updates the cycle when a card is played.
        """
        # 1. Add to known cards if new
        self.known_cards.add(card_name)
        
        # 2. Remove from Hand (if present)
        if card_name in self.hand:
            self.hand.remove(card_name)
        else:
            # If not in hand, it might be a card we hadn't tracked yet 
            # or we lost track. We assume it was in their hand.
            pass

        # 3. Add to Queue (Back of line)
        self.queue.append(card_name)
        
        # 4. Cycle Logic: 
        # If Queue has more than 4 cards, the front card moves to Hand.
        # (In CR, you have 4 in hand, 4 in queue. When you play 1, 
        # it goes to queue, and the one waiting longest comes to hand).
        if len(self.queue) > 4:
            returning_card = self.queue.popleft()
            self.hand.append(returning_card)
            
        # Debug print
        self.print_state()

    def print_state(self):
        print(f"Hand: {self.hand}")
        print(f"Queue: {list(self.queue)}")
