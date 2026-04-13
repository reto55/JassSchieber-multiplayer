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
