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


from ausbau.game_session import get_valid_cards, determine_trick_winner, trick_points


def test_valid_cards_leading_all_valid():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln'), Koenig(8, 'Eicheln')]
    codes = get_valid_cards(hand, None, 'Rosen')
    assert set(codes) == {'EA', 'EK'}


def test_valid_cards_must_follow_suit():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    hand['Rosen'] = [Koenig(8, 'Rosen')]
    codes = get_valid_cards(hand, 'Eicheln', 'Schellen')
    assert codes == ['EA']
    assert 'RK' not in codes


def test_valid_cards_cannot_follow_suit():
    hand = {suit: [] for suit in SUITS}
    hand['Rosen'] = [Koenig(8, 'Rosen')]
    codes = get_valid_cards(hand, 'Eicheln', 'Schellen')
    assert 'RK' in codes


def test_valid_cards_trump_under_always_playable():
    """Trump Under can always be played even when following a different suit."""
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    hand['Rosen'] = [Under(6, 'Rosen')]  # Rosen is trump
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen')
    assert 'EA' in codes
    assert 'RU' in codes  # trump Under is always valid


def test_trick_winner_trump_beats_lead():
    folger = {'comps': 'compo', 'compo': 'compn', 'compn': 'compe', 'compe': 'comps'}
    trick = {
        'comps': Sechs(1, 'Eicheln'),
        'compo': Koenig(8, 'Eicheln'),
        'compn': Ass(9, 'Rosen'),    # Rosen is trump
        'compe': Banner(5, 'Eicheln'),
    }
    assert determine_trick_winner(trick, 'comps', 'Rosen', folger) == 'compn'


def test_trick_winner_highest_lead_suit_wins():
    folger = {'comps': 'compo', 'compo': 'compn', 'compn': 'compe', 'compe': 'comps'}
    trick = {
        'comps': Sechs(1, 'Eicheln'),
        'compo': Koenig(8, 'Eicheln'),
        'compn': Banner(5, 'Rosen'),   # off-suit, can't win
        'compe': Ober(7, 'Eicheln'),
    }
    assert determine_trick_winner(trick, 'comps', 'Schellen', folger) == 'compo'


def test_trick_points_oben_mode():
    trick = {
        'comps': Banner(5, 'Eicheln'),   # woben=10
        'compo': Koenig(8, 'Rosen'),     # woben=4
        'compn': Ass(9, 'Schellen'),     # woben=11
        'compe': Under(6, 'Schilten'),   # woben=2
    }
    assert trick_points(trick, 'Oben') == 27  # 10+4+11+2


def test_trick_points_trumpf_mode():
    trick = {
        'comps': Under(6, 'Eicheln'),   # Eicheln is trump → wtrumpf=20
        'compo': Ass(9, 'Rosen'),       # non-trump → wfarbe=11
        'compn': Banner(5, 'Eicheln'),  # trump → wtrumpf=10
        'compe': Koenig(8, 'Rosen'),    # non-trump → wfarbe=4
    }
    assert trick_points(trick, 'Eicheln') == 45  # 20+11+10+4
