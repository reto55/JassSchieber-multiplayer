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


from Cards_refactored import Play
from ausbau.game_session import ai_select_card, describe_weis, detect_stock


def test_ai_leads_plays_highest_value():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln'), Sechs(1, 'Eicheln')]
    card = ai_select_card(hand, None, 'Rosen')
    assert card_to_code(card) == 'EA'


def test_ai_follows_plays_lowest_value():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln'), Sechs(1, 'Eicheln')]
    card = ai_select_card(hand, 'Eicheln', 'Rosen')
    assert card_to_code(card) == 'E6'


def test_describe_weis_dreier():
    combos = [(0, 3, 7)]  # Eicheln, 3-sequence
    result = describe_weis(combos, [])
    assert result == [{'name': 'Dreier', 'suit': 'Eicheln', 'points': 20}]


def test_describe_weis_vierter():
    combos = [(2, 4, 8)]  # Schellen, 4-sequence
    result = describe_weis(combos, [])
    assert result == [{'name': 'Vierter', 'suit': 'Schellen', 'points': 50}]


def test_describe_weis_fuenfer():
    combos = [(1, 5, 9)]  # Rosen, 5-sequence
    result = describe_weis(combos, [])
    assert result == [{'name': '5er', 'suit': 'Rosen', 'points': 100}]


def test_describe_weis_viererle():
    result = describe_weis([], [18])  # Under in all suits
    assert result == [{'name': 'Viererle', 'suit': None, 'points': 100}]


def test_detect_stock_true():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Koenig(8, 'Eicheln'), Ober(7, 'Eicheln')]
    assert detect_stock(hand, 'Eicheln') is True


def test_detect_stock_false_wrong_suit():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Koenig(8, 'Eicheln'), Ober(7, 'Eicheln')]
    assert detect_stock(hand, 'Rosen') is False


def test_detect_stock_false_missing_ober():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Koenig(8, 'Eicheln')]
    assert detect_stock(hand, 'Eicheln') is False


from ausbau.game_session import GameSession


def test_initial_state_structure():
    session = GameSession(end_game=500)
    play = Play(1)
    state = session._initial_state(play)

    assert state['type'] == 'game_start'
    assert len(state['hand']) == 9
    assert state['scores'] == {'sn': 0, 'ow': 0}
    assert state['target'] == 500
    assert len(state['players']) == 3
    assert any(p['is_partner'] for p in state['players'])
    assert all('card_count' in p for p in state['players'])


def test_initial_state_scores_accumulate():
    session = GameSession(end_game=500)
    session.point_sn = 42
    session.point_ow = 17
    state = session._initial_state(Play(1))
    assert state['scores'] == {'sn': 42, 'ow': 17}


import asyncio
from unittest.mock import AsyncMock


def test_trump_phase_human_leads_chooses():
    """When human (comps) leads, server asks and human responds choose_trump."""
    session = GameSession()
    play = Play(4)  # spiel 4 → comps leads

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={"type": "choose_trump", "suit": "Eicheln"})
    asyncio.run(session._trump_phase(ws, play))

    assert play.operator == "Eicheln"
    calls = [c[0][0] for c in ws.send_json.call_args_list]
    assert calls[0]['type'] == 'trump_request'
    assert calls[0]['can_schieben'] is True
    assert calls[1]['type'] == 'trump_chosen'
    assert calls[1]['suit'] == 'Eicheln'


def test_trump_phase_human_leads_schiebt():
    """Human schiebt → partner Nord (AI) chooses via trumpfs()."""
    session = GameSession()
    play = Play(4)
    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={"type": "schieben"})
    asyncio.run(session._trump_phase(ws, play))

    assert play.operator in ['Eicheln', 'Rosen', 'Schellen', 'Schilten', 'Oben', 'Unten']
    assert play.starter == 'compn'


def test_weis_phase_sends_result():
    """weis_result is always sent, even if no weis exist."""
    session = GameSession()
    play = Play(1)
    ws = AsyncMock()
    asyncio.run(session._weis_phase(ws, play))

    last = ws.send_json.call_args_list[-1][0][0]
    assert last['type'] == 'weis_result'
    assert 'announcements' in last
    assert 'scores' in last


def test_weis_phase_human_announces_adds_points():
    """If human announces weis, SN score increases."""
    from unittest.mock import patch

    session = GameSession()
    play = Play(1)

    fake_weis = [{'name': 'Dreier', 'suit': 'Eicheln', 'points': 20}]
    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={
        "type": "declare_weis", "weis": ["Dreier"], "announce": True
    })

    with patch('ausbau.game_session.describe_weis', return_value=fake_weis):
        asyncio.run(session._weis_phase(ws, play))

    # Human (comps) is SN team — points should have increased
    assert session.point_sn >= 20
