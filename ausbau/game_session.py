import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from typing import Optional
from Cards_refactored import (
    Play, SUITS, PLAY_MODES, Card,
    determine_trumpf, trumpfs, wiis, wiis_gleiche,
)
from utils.game_utils import check_game_end, get_winner

SUIT_PREFIX = {'Eicheln': 'E', 'Rosen': 'R', 'Schellen': 'SE', 'Schilten': 'SI'}
RANK_SUFFIX = {9: 'A', 8: 'K', 7: 'O', 6: 'U', 5: 'B', 4: '9', 3: '8', 2: '7', 1: '6'}

POSITION_NAMES = {'comps': 'Süd', 'compn': 'Nord', 'compo': 'Ost', 'compe': 'West'}
SN_PLAYERS = {'comps', 'compn'}
OW_PLAYERS = {'compo', 'compe'}
PLAYERS = ['comps', 'compo', 'compn', 'compe']


def card_to_code(card: Card) -> str:
    """Convert a Card object to its CSS code string, e.g. Ass(Eicheln) → 'EA'."""
    return SUIT_PREFIX[card.suit] + RANK_SUFFIX[card.rank]


def hand_to_codes(hand: dict) -> list:
    """Return list of card codes for all cards in a hand dict."""
    return [card_to_code(c) for suit in SUITS for c in hand[suit]]


def find_card_in_hand(code: str, hand: dict):
    """Find a card in a hand dict by code. Returns (Card, suit) or (None, None)."""
    for suit in SUITS:
        for card in hand[suit]:
            if card_to_code(card) == code:
                return card, suit
    return None, None


def get_valid_cards(hand: dict, lead_suit: Optional[str], operator: str) -> list:
    """Return card codes valid to play. lead_suit=None means player is leading."""
    all_cards = [c for suit in SUITS for c in hand[suit]]

    if lead_suit is None:
        return [card_to_code(c) for c in all_cards]

    follow_cards = hand.get(lead_suit, [])
    if not follow_cards:
        return [card_to_code(c) for c in all_cards]

    valid = list(follow_cards)
    # Trump Under (Bube) can always be played in a trump game
    if operator in SUITS:
        for c in hand.get(operator, []):
            if c.__class__.__name__ == 'Under' and c not in valid:
                valid.append(c)

    return [card_to_code(c) for c in valid]


def determine_trick_winner(trick: dict, first: str, operator: str, folger: dict) -> str:
    """Return the player key who wins the trick."""
    lead_suit = trick[first].suit

    def strength(card: Card):
        if operator in SUITS:
            if card.suit == operator:
                return (2, card.trumpf)
            elif card.suit == lead_suit:
                return (1, card.rank)
            return (0, 0)
        elif operator == 'Oben':
            return (1, card.oben) if card.suit == lead_suit else (0, 0)
        else:  # Unten
            return (1, card.unten) if card.suit == lead_suit else (0, 0)

    winner = first
    best = strength(trick[first])
    player = folger[first]
    for _ in range(3):
        s = strength(trick[player])
        if s > best:
            best = s
            winner = player
        player = folger[player]
    return winner


def trick_points(trick: dict, operator: str) -> int:
    """Sum point values of all cards in the trick for the given mode."""
    total = 0
    for card in trick.values():
        if operator in SUITS:
            total += card.wtrumpf if card.suit == operator else card.wfarbe
        elif operator == 'Oben':
            total += card.woben
        else:
            total += card.wunten
    return total


def ai_select_card(hand: dict, lead_suit: Optional[str], operator: str) -> Card:
    """Simple AI: lead=highest point value, follow=lowest point value."""
    valid_codes = get_valid_cards(hand, lead_suit, operator)
    valid_cards = [find_card_in_hand(code, hand)[0] for code in valid_codes]

    def point_value(card: Card) -> int:
        if operator in SUITS:
            return card.wtrumpf if card.suit == operator else card.wfarbe
        elif operator == 'Oben':
            return card.woben
        return card.wunten

    if lead_suit is None:
        return max(valid_cards, key=point_value)
    return min(valid_cards, key=point_value)


def describe_weis(weis_combos: list, weis_gleiche: list) -> list:
    """Convert raw wiis() / wiis_gleiche() output to human-readable dicts."""
    result = []
    SCORE_MAP = {3: ('Dreier', 20), 4: ('Vierter', 50)}
    for suit_idx, seq_len, _ in weis_combos:
        if seq_len is None or seq_len < 3:
            continue
        name, pts = SCORE_MAP.get(seq_len, (f'{seq_len}er', 100))
        result.append({'name': name, 'suit': SUITS[suit_idx], 'points': pts})
    if weis_gleiche:
        result.append({'name': 'Viererle', 'suit': None, 'points': 100})
    return result


def detect_stock(hand: dict, operator: str) -> bool:
    """True if hand has König + Ober of the trump suit (Stöck, 20pts)."""
    if operator not in SUITS:
        return False
    ranks = {c.__class__.__name__ for c in hand.get(operator, [])}
    return 'Koenig' in ranks and 'Ober' in ranks
