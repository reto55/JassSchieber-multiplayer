import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Cards_refactored import Ass, Koenig, Ober, Under, Banner, Neun, Acht, Sieben, Sechs, SUITS
from ausbau.game_session import card_to_code, hand_to_codes, find_card_in_hand


def test_card_to_code_eicheln_ass():
    assert card_to_code(Ass(9, 'Eicheln')) == 'EA'

def test_card_to_code_schellen_koenig():
    assert card_to_code(Koenig(8, 'Schellen')) == 'SEK'

def test_card_to_code_schilten_under():
    assert card_to_code(Under(6, 'Schilten')) == 'SIU'

def test_card_to_code_rosen_sechs():
    assert card_to_code(Sechs(1, 'Rosen')) == 'R6'

def test_hand_to_codes_returns_all():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'].append(Ass(9, 'Eicheln'))
    hand['Rosen'].append(Koenig(8, 'Rosen'))
    codes = hand_to_codes(hand)
    assert 'EA' in codes
    assert 'RK' in codes
    assert len(codes) == 2

def test_find_card_in_hand_found():
    hand = {suit: [] for suit in SUITS}
    card = Ass(9, 'Eicheln')
    hand['Eicheln'].append(card)
    found, suit = find_card_in_hand('EA', hand)
    assert found is card
    assert suit == 'Eicheln'

def test_find_card_in_hand_not_found():
    hand = {suit: [] for suit in SUITS}
    found, suit = find_card_in_hand('RK', hand)
    assert found is None
    assert suit is None
