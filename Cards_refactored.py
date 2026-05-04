# -*- coding: UTF-8 -*-
import random
from operator import itemgetter
from collections import defaultdict
from datetime import datetime
import json
from enum import Enum

# Constants
SUITS = ['Eicheln', 'Rosen', 'Schellen', 'Schilten']
PLAY_MODES = ['Eicheln', 'Rosen', 'Schellen', 'Schilten', 'Oben', 'Unten']
CARD_VALUES = {
    'Sechs': 1, 'Sieben': 2, 'Acht': 3, 'Neun': 4, 'Banner': 5,
    'Under': 6, 'Ober': 7, 'Koenig': 8, 'Ass': 9
}

# Per-rank attributes looked up by the 1-based `rank` index that `Play`
# initialises its `farben` grid from. Columns:
#   [name, rank, oben, unten, trumpf, w_oben, w_unten, w_trumpf, w_farbe]
# Index 0 is intentionally empty so that ranks 1..9 map directly to list
# positions (matches the 1-based rank numbering used throughout the codebase).
CARD_ATTRIBUTES = dict(enumerate([''] + [
    ['Sechs', 1, 9, 10, 0, 11, 0, 0],
    ['Sieben', 2, 8, 11, 0, 0, 0, 0],
    ['Acht', 3, 7, 12, 8, 8, 0, 0],
    ['Neun', 4, 6, 17, 0, 0, 14, 4],
    ['Banner', 5, 5, 13, 10, 10, 10, 10],
    ['Under', 6, 4, 18, 2, 2, 20, 2],
    ['Ober', 7, 3, 14, 3, 3, 3, 3],
    ['Koenig', 8, 2, 15, 4, 4, 4, 4],
    ['Ass', 9, 1, 16, 0, 11, 11, 11]
], 1))

class Card:
    """Base card class with common attributes and methods"""
    
    def __init__(self, rank, suit, oben=0, unten=0, trumpf=0, woben=0, wunten=0, wtrumpf=0, wfarbe=0):
        self.rank = rank
        self.suit = suit
        self.oben = oben
        self.unten = unten
        self.trumpf = trumpf
        self.woben = woben
        self.wunten = wunten
        self.wtrumpf = wtrumpf
        self.wfarbe = wfarbe

    def __eq__(self, other):
        return self.rank == other.rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __repr__(self):
        return "{__class__.__name__}(suit={suit!r}, rank={rank!r})".format(
            __class__=self.__class__, **self.__dict__)

    def __str__(self):
        return "{rank}{suit}".format(**self.__dict__)
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__class__.__name__)

    def to_jsons(self):
        return json.dumps(self, default=lambda o: (o.__class__.__name__, o.suit))


# Card type classes
class Ass(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=9, unten=1, trumpf=16, woben=11, wunten=0, wtrumpf=11, wfarbe=11)

class Koenig(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=8, unten=2, trumpf=15, woben=4, wunten=4, wtrumpf=4, wfarbe=4)

class Ober(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=7, unten=3, trumpf=14, woben=3, wunten=3, wtrumpf=3, wfarbe=3)

class Under(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=6, unten=4, trumpf=18, woben=2, wunten=2, wtrumpf=20, wfarbe=2)

class Banner(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=5, unten=5, trumpf=13, woben=10, wunten=10, wtrumpf=10, wfarbe=10)

class Neun(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=4, unten=6, trumpf=17, woben=0, wunten=0, wtrumpf=14, wfarbe=0)

class Acht(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=3, unten=7, trumpf=12, woben=8, wunten=8, wtrumpf=0, wfarbe=0)

class Sieben(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=2, unten=8, trumpf=11, woben=0, wunten=0, wtrumpf=0, wfarbe=0)

class Sechs(Card):
    def __init__(self, rank, suit):
        super().__init__(rank, suit, oben=1, unten=9, trumpf=10, woben=0, wunten=11, wtrumpf=0, wfarbe=0)


class Suit:
    """Represents a card suit with name and symbol"""
    
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    def __repr__(self):
        return self.symbol


# Define suit objects
Eicheln = Suit('Eicheln', '♣')
Rosen = Suit('Rosen', '♠')
Schellen = Suit('Schellen', '♥')
Schilten = Suit('Schilten', '♦')


def create_card(rank, suit):
    """Factory function to create the appropriate card class based on rank"""
    card_classes = {
        9: Ass,
        8: Koenig,
        7: Ober,
        6: Under,
        5: Banner,
        4: Neun,
        3: Acht,
        2: Sieben,
        1: Sechs
    }
    
    card_class = card_classes.get(rank, Card)
    return card_class(rank, suit)


class Deck(list):
    """Represents a deck of cards for the Schieber game"""
    
    def __init__(self):
        super().__init__(create_card(r + 1, s) for r in range(9) for s in SUITS)
        for _ in range(6):
            random.shuffle(self)


class Hand:
    """Represents a player's hand in the game"""
    
    def __init__(self, sp1_card=None, sp2_card=None, sp3_card=None, sp4_card=None, *cards):
        self.sp1_card = sp1_card if sp1_card is not None else []
        self.sp2_card = sp2_card if sp2_card is not None else []
        self.sp3_card = sp3_card if sp3_card is not None else []
        self.sp4_card = sp4_card if sp4_card is not None else []
        self.cards = list(cards)
        self.d = Deck()
        
        # Deal cards
        for i in range(3):
            self._move_cards(self.d, self.sp2_card, 3)
            self._move_cards(self.d, self.sp3_card, 3)
            self._move_cards(self.d, self.sp4_card, 3)
            self._move_cards(self.d, self.sp1_card, 3)

    def __str__(self):
        return ", ".join(map(str, self.cards))

    def __repr__(self):
        return "{__class__.__name__}(({sp1_card!r}, {_cards_str}),({sp2_card!r}, {_cards_str}),({sp3_card!r}, {_cards_str}),({sp4_card!r}, {_cards_str}))".format(
            __class__=self.__class__, _cards_str=", ".join(map(repr, self.cards)), **self.__dict__)

    @staticmethod
    def _add_card(hand, card):
        """Add a card to the hand"""
        hand.append(card)

    @staticmethod
    def _pop_card(cards, i=0):
        """Remove and return a card from the cards at position i"""
        return cards.pop(i)

    def _move_cards(self, source, destination, num):
        """Move num cards from source to destination"""
        for _ in range(num):
            self._add_card(destination, self._pop_card(source))
        return destination

    def farbe(self):
        """Group cards by suit"""
        suits = {suit: [] for suit in SUITS}
        
        for card in self:
            suits[card.suit].append(card)
            
        return suits


class Players:
    """Manages players and their cards"""
    
    def __init__(self, spiel_num=None, compo=None, compn=None, compe=None, comps=None,
                 ost=None, nor=None, est=None, sud=None):
        self.spiel_num = spiel_num if spiel_num is not None else 0
        self.ost = ost if ost is not None else []
        self.nor = nor if nor is not None else []
        self.est = est if est is not None else []
        self.sud = sud if sud is not None else []
        self.compo = compo if compo is not None else {}
        self.compe = compe if compe is not None else {}
        self.compn = compn if compn is not None else {}
        self.comps = comps if comps is not None else {}

        self.hand = Hand()
        self._initialize_players()

    def _initialize_players(self):
        """Set up player hands based on the round number"""
        if self.spiel_num == 1:
            self.compo = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp2_card, self.ost, 9)))
            self.compn = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp3_card, self.nor, 9)))
            self.compe = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp4_card, self.est, 9)))
            self.comps = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp1_card, self.sud, 9)))
        elif self.spiel_num == 2:
            self.compn = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp2_card, self.nor, 9)))
            self.compe = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp3_card, self.est, 9)))
            self.comps = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp4_card, self.sud, 9)))
            self.compo = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp1_card, self.ost, 9)))
        elif self.spiel_num == 3:
            self.compe = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp2_card, self.est, 9)))
            self.comps = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp3_card, self.sud, 9)))
            self.compo = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp4_card, self.ost, 9)))
            self.compn = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp1_card, self.nor, 9)))
        elif self.spiel_num == 4:
            self.comps = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp2_card, self.sud, 9)))
            self.compo = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp3_card, self.ost, 9)))
            self.compn = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp4_card, self.nor, 9)))
            self.compe = sort_hand_desc(Hand.farbe(self._move_cards(self.hand.sp1_card, self.est, 9)))
        else:
            raise ValueError("Invalid round number: {}".format(self.spiel_num))
            
    @staticmethod
    def _move_cards(source, destination, num):
        """Move num cards from source to destination"""
        for _ in range(num):
            destination.append(source.pop(0))
        return destination


class Play(Players):
    """Main game play class"""
    
    def __init__(self, spiel=None, game=None, stich=None, lastf=None, partner=None, 
                 folger=None, operator=None, starter=None, farben=None, wis=None, 
                 wis4=None, first=None, **kwargs):
        self.spiel = spiel if spiel is not None else 0
        self.operator = operator if operator is not None else ''
        self.wis = wis if wis is not None else []
        self.wis4 = wis4 if wis4 is not None else []
        self.first = first if first is not None else ''
        
        # Initialize game states
        self.game = game if game is not None else {player: [] for player in ['compo', 'comps', 'compn', 'compe']}
        
        # Define player relationships
        self.partner = partner if partner is not None else {
            'comps': 'compn', 'compo': 'compe', 'compn': 'comps', 'compe': 'compo'
        }
        
        self.folger = folger if folger is not None else {
            'comps': 'compo', 'compo': 'compn', 'compn': 'compe', 'compe': 'comps'
        }
        
        self.lastf = lastf if lastf is not None else {
            'comps': '', 'compo': '', 'compn': '', 'compe': ''
        }
        
        self.stich = stich if stich is not None else {
            'compo': [], 'comps': [], 'compn': [], 'compe': []
        }
        
        self.starter = starter if starter is not None else ''
        
        # Initialize card values for each suit and rank
        self.farben = farben if farben is not None else {
            s: [CARD_ATTRIBUTES[y] for y in range(1, 11)] for s in SUITS
        }
        
        # Call parent constructor
        super().__init__(spiel_num=self.spiel, **kwargs)
        
        # Set up the game based on the round
        self._setup_game()
    
    def _setup_game(self):
        """Configure the game based on the current round"""
        if self.spiel == 1:
            self._setup_round("compo")
        elif self.spiel == 2: 
            self._setup_round("compn")            
        elif self.spiel == 3:
            self._setup_round("compe")          
        elif self.spiel == 4:
            self._setup_round("comps")
    
    def _setup_round(self, first_player):
        """Set up a specific round with the given first player"""
        self.first = first_player
        self.starter = first_player
        self.operator = determine_trumpf(getattr(self, first_player))
        
        # Get combinations (Wiis) for each player
        players = ["compo", "compn", "compe", "comps"]
        start_idx = players.index(first_player)
        ordered_players = players[start_idx:] + players[:start_idx]
        
        for i, player in enumerate(ordered_players):
            self.wis.insert(i, wiis(getattr(self, player)))
            self.wis4.insert(i, wiis_gleiche(getattr(self, player)))


# Utility functions
def sum_values(values):
    """Sum the values in a list"""
    return sum(values)


def determine_longest_suit(player):
    """Determine which suit has the most cards for a player"""
    suit_counts = {}
    for suit in SUITS:
        suit_counts[suit] = len({card.oben for card in player[suit]})
    
    # Find the suit with the most cards
    max_count = 0
    longest_suit = SUITS[0]
    
    for suit, count in suit_counts.items():
        if count >= max_count:
            max_count = count
            longest_suit = suit
    
    return longest_suit


def sort_hand_desc(player):
    """Sort cards in player's hand by reverse order"""
    for suit in player:
        player[suit] = sorted(player[suit], reverse=True)
    return player


def wiis_gleiche(player):
    """Find card combinations of the same rank across different suits"""
    sets_by_suit = {}
    for suit in SUITS:
        sets_by_suit[suit] = {card.trumpf for card in player[suit]}
    
    # Find common cards across all suits
    common_cards = sets_by_suit['Eicheln'].intersection(
        sets_by_suit['Rosen'],
        sets_by_suit['Schellen'],
        sets_by_suit['Schilten']
    )
    
    return list(common_cards)


def calculate_wiis(cards_by_oben, suit_index, length, combinations):
    """Calculate card combinations (Wiis) for scoring"""
    
    def _calculate_sequence(cards, sequence_min_length, suit_idx, result):
        """Find sequences of consecutive cards"""
        if len(cards) < sequence_min_length:
            result.append((suit_idx, None, None))
            return
            
        sequence = [cards[0]]
        for val in cards[1:]:
            if sequence[-1] + 1 == val:
                sequence.append(val)
        
        if len(sequence) >= sequence_min_length:
            result.append((suit_idx, len(sequence), sequence[-1]))
        elif len(sequence) >= 3:  # Still record 3+ card sequences
            result.append((suit_idx, len(sequence), sequence[-1]))
        else:
            result.append((suit_idx, None, None))
            
            # Recursively check for sequences in remaining cards
            if len(cards) > 1:
                calculate_wiis(cards[1:], suit_idx, min(sequence_min_length, len(cards)-1), result)
    
    # Determine sequence calculation based on the length of cards
    if length >= 3:
        _calculate_sequence(cards_by_oben, 3, suit_index, combinations)
    else:
        combinations.append((suit_index, None, None))
    
    return combinations


def wiis(player):
    """Find all scoring combinations (Wiis) in a player's hand"""
    cards_by_suit = []
    
    # Get sorted cards by suit
    for suit in SUITS:
        cards = sorted([card.oben for card in player[suit]])
        cards_by_suit.append(cards)
    
    combinations = []
    for suit_idx, cards in enumerate(cards_by_suit):
        calculate_wiis(cards, suit_idx, len(cards), combinations)
    
    return combinations


def determine_trumpf(player):
    """Determine the trump suit based on card combinations"""
    # Get longest suit and combinations
    longest_suit = determine_longest_suit(player)
    combinations = wiis(player)
    
    # If no combinations, player should pass ("Schieben")
    if not combinations or combinations[0][1] is None:
        return 'Schieben'
    
    # Extract combination info
    suit_idx, seq_length, _ = combinations[0]
    suit = SUITS[suit_idx]
    
    # Get cards of the suit
    cards = [card.oben for card in player[suit]]
    card_sum = sum_values(cards)
    card_count = len(cards)
    
    # Decision logic based on card count and values
    if not seq_length:
        return 'Schieben'
        
    # Define thresholds for different play modes
    if 3 <= seq_length <= 7:
        # Various thresholds for different sequence lengths
        if card_count == seq_length:
            if card_sum in (6, 9, 15, 18, 21):
                return 'Unten'
            elif card_sum in range(12, 22) or card_sum in range(20, 31) or card_sum in range(27, 34):
                return suit
            else:
                return 'Oben'
        elif card_count == seq_length + 1:
            if card_sum in range(11, 13) or card_sum in range(16, 19) or card_sum in range(22, 24) or card_sum == 29:
                return 'Unten'
            elif card_sum in range(13, 26) or card_sum in range(18, 31) or card_sum in range(23, 35):
                return suit
            else:
                return 'Oben'
        elif card_count == seq_length + 2:
            if card_sum in range(17, 21) or card_sum in range(23, 25) or card_sum == 30:
                return 'Unten'
            elif card_sum in range(20, 30) or card_sum in range(24, 35):
                return suit
            elif card_sum > 29:
                return 'Oben'
            else:
                return suit
    elif seq_length == 8:
        if card_sum == 36:
            return 'Unten'
        else:
            return 'Oben'
    elif seq_length == 9:
        return 'Oben'
    
    # Default to the longest suit if no other conditions match
    return suit


def determine_trumpf_after_schieben(player):
    """Alternative trump determination when player passes (schiebt)"""
    # Similar to determine_trumpf but with different thresholds
    longest_suit = determine_longest_suit(player)
    combinations = wiis(player)
    
    # If no combinations, default to longest suit
    if not combinations or combinations[0][1] is None:
        return longest_suit
    
    # Extract combination info
    suit_idx, seq_length, _ = combinations[0]
    suit = SUITS[suit_idx]
    
    # Get cards of the suit
    cards = [card.oben for card in player[suit]]
    card_sum = sum_values(cards)
    card_count = len(cards)
    
    # Similar decision logic to determine_trumpf but favoring suit selection
    # This function is called when the partner has passed (schiebt)
    if not seq_length:
        return longest_suit
        
    # Most of the same logic as determine_trumpf but with slightly different thresholds
    # and a preference for selecting a suit rather than passing
    if 3 <= seq_length <= 7:
        # Various thresholds similar to determine_trumpf
        if card_count == seq_length:
            if card_sum in (6, 9, 15, 18, 21):
                return 'Unten'
            elif card_sum in range(12, 22) or card_sum in range(20, 31) or card_sum in range(27, 34):
                return suit
            else:
                return 'Oben'
        # Similar patterns continue...
    elif seq_length == 8:
        if card_sum == 36:
            return 'Unten'
        else:
            return 'Oben'
    elif seq_length == 9:
        return 'Oben'
    
    # Default to the suit if no other conditions match
    return suit


if __name__ == "__main__":
    # Test code
    dealer = Play(1)
    print(dealer.compo, '\n')
    print(dealer.compn, '\n')
    print(dealer.compe, '\n')
    print(dealer.comps, '\n')
    print(dealer.wis, '\n')
    print(dealer.wis4, '\n')
    print(dealer.farben, '\n')
    print(dealer.partner[dealer.first], '\n')
    print(dealer.starter, '\n')
    print(dealer.game['compo'], '\n')
    print(dealer.game.keys(), '\n')
    print(dealer.folger[dealer.first] == 'compn', '\n')
    print(dealer.folger[dealer.partner[dealer.first]] == 'comps', '\n')
    print(dealer.folger[dealer.partner[dealer.first]] == dealer.partner[dealer.folger[dealer.first]], '\n')
