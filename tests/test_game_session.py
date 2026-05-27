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


def test_valid_cards_any_trump_always_playable():
    """Any trump card can be played even when following a different suit."""
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    hand['Rosen'] = [Under(6, 'Rosen'), Sechs(1, 'Rosen')]  # Rosen is trump
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen')
    assert 'EA' in codes
    assert 'RU' in codes
    assert 'R6' in codes  # non-Under trumps are now also always valid


# ── House rules: Under-holdback, trump-always-playable, no-undertrumping ──
# These apply ONLY in the four trump modes (Eicheln/Rosen/Schellen/Schilten).
# `trick_so_far` is the engine shape: [{"position","card"}, ...] of CODES.


def test_underholdback_trump_led_only_under_any_card():
    """Rule 1: trump led, player's ONLY trump is the trump Under → any card."""
    hand = {suit: [] for suit in SUITS}
    hand['Rosen'] = [Under(6, 'Rosen')]                 # Rosen trump, sole trump
    hand['Eicheln'] = [Ass(9, 'Eicheln'), Sechs(1, 'Eicheln')]
    codes = get_valid_cards(hand, 'Rosen', 'Rosen')
    assert set(codes) == {'RU', 'EA', 'E6'}            # Under not forced


def test_underholdback_trump_led_under_plus_other_trump_must_follow():
    """Rule 1 boundary: Under + another trump → must follow with a trump
    (Under stays optional among them)."""
    hand = {suit: [] for suit in SUITS}
    hand['Rosen'] = [Under(6, 'Rosen'), Koenig(8, 'Rosen')]
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    codes = get_valid_cards(hand, 'Rosen', 'Rosen')
    assert set(codes) == {'RU', 'RK'}                  # only trumps, EA excluded


def test_trump_led_no_trump_any_card():
    """Trump led, no trump at all → any card (can't follow)."""
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    hand['Schellen'] = [Sechs(1, 'Schellen')]
    codes = get_valid_cards(hand, 'Rosen', 'Rosen')
    assert set(codes) == {'EA', 'SE6'}


def test_nontrump_led_no_trump_played_may_follow_or_trump():
    """Rule 2: non-trump led, no trump yet in trick → follow OR any trump."""
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]              # can follow Eicheln lead
    hand['Rosen'] = [Under(6, 'Rosen'), Sechs(1, 'Rosen')]   # Rosen trump
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen', trick_so_far=[
        {"position": "comps", "card": "EK"},
    ])
    assert set(codes) == {'EA', 'RU', 'R6'}            # any trump still allowed


def test_no_undertrumping_with_nontrump_in_hand():
    """Rule 3: non-trump led, trump already played, holding higher+lower trump
    AND a non-trump → valid = follow/discards + higher trump only."""
    hand = {suit: [] for suit in SUITS}
    # Rosen is trump. Trump strengths: Under=18, Neun=17, Banner=13, Sechs=10.
    hand['Rosen'] = [Banner(5, 'Rosen'), Sechs(1, 'Rosen')]  # one higher, one lower
    hand['Eicheln'] = [Koenig(8, 'Eicheln')]               # non-trump discard
    # An Ober of Rosen (trumpf=14) already in the trick on an Eicheln lead.
    trick = [
        {"position": "compe", "card": "EA"},               # lead (Eicheln)
        {"position": "compn", "card": "RO"},               # Ober of Rosen, trumpf=14
    ]
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen', trick_so_far=trick)
    # Player CAN follow the Eicheln lead with EK, so EK is valid. The trump
    # restriction applies to the trumps in hand: only an over-trump is allowed.
    assert 'EK' in codes        # can follow Eicheln lead
    assert 'R6' not in codes    # Sechs (10) does NOT beat Ober (14) — undertrump
    assert 'RU' not in codes    # not in hand
    # Banner(13) also does NOT beat Ober(14) — so no overtrump available here.
    assert 'RB' not in codes


def test_no_undertrumping_overtrump_allowed():
    """Rule 3: a trump that DOES beat the highest played trump is allowed."""
    hand = {suit: [] for suit in SUITS}
    hand['Rosen'] = [Under(6, 'Rosen'), Sechs(1, 'Rosen')]  # Under=18 beats Ober=14
    hand['Eicheln'] = [Koenig(8, 'Eicheln')]
    trick = [
        {"position": "compe", "card": "EA"},
        {"position": "compn", "card": "RO"},               # Ober Rosen, 14
    ]
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen', trick_so_far=trick)
    assert 'EK' in codes        # follow the lead
    assert 'RU' in codes        # over-trump allowed (18 > 14)
    assert 'R6' not in codes    # under-trump forbidden (10 < 14)


def test_no_undertrumping_must_beat_highest_of_multiple_trumps():
    """Rule 3 with MULTIPLE trumps already played: the bar is the HIGHEST
    trump in the trick, not the most-recently-played one. A low trump and a
    middle trump are down; the player must over-trump the middle (highest),
    so a trump above it is valid, a trump below it (even though it beats the
    earlier low trump) is NOT, and the non-trump discard is valid."""
    hand = {suit: [] for suit in SUITS}
    # Rosen trump. Player holds Banner(13, BELOW highest) + Under(18, ABOVE
    # highest) + a non-trump discard (Eicheln Sechs).
    hand['Rosen'] = [Banner(5, 'Rosen'), Under(6, 'Rosen')]
    hand['Eicheln'] = [Sechs(1, 'Eicheln')]                # non-trump discard
    # Schellen led; player cannot follow. Two trumps already on the table:
    # Sechs (10, low) then Koenig (15, middle = current highest).
    trick = [
        {"position": "compe", "card": "SEK"},              # Schellen lead
        {"position": "compn", "card": "R6"},               # low trump, 10
        {"position": "comps", "card": "RK"},               # middle trump, 15 (highest)
    ]
    codes = get_valid_cards(hand, 'Schellen', 'Rosen', trick_so_far=trick)
    assert set(codes) == {'RU', 'E6'}                      # over-trump + discard
    assert 'RU' in codes        # Under (18) beats the highest played (15)
    assert 'E6' in codes        # non-trump discard always allowed
    assert 'RB' not in codes    # Banner (13) < highest played (15) — undertrump


def test_all_trump_hand_forced_undertrump_allowed():
    """Rule 3 exception: whole hand is trumps incl. only lower trumps → all
    trumps valid (forced undertrump)."""
    hand = {suit: [] for suit in SUITS}
    # Rosen trump; player holds ONLY low trumps, no non-trump anywhere.
    hand['Rosen'] = [Sieben(2, 'Rosen'), Sechs(1, 'Rosen')]  # trumpf 11 and 10
    trick = [
        {"position": "compe", "card": "EA"},               # Eicheln lead
        {"position": "compn", "card": "RO"},               # Ober Rosen, 14
    ]
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen', trick_so_far=trick)
    assert set(codes) == {'R7', 'R6'}                      # forced, undertrump ok


def test_no_undertrump_discard_nontrump_when_cant_overtrump():
    """Non-trump led, can't follow, trump already played, only lower trumps,
    but a non-trump exists → must discard non-trump (no undertrump)."""
    hand = {suit: [] for suit in SUITS}
    hand['Rosen'] = [Sechs(1, 'Rosen')]                    # low trump, 10
    hand['Schellen'] = [Koenig(8, 'Schellen')]             # non-trump, can't follow
    trick = [
        {"position": "compe", "card": "EA"},               # Eicheln lead
        {"position": "compn", "card": "RO"},               # Ober Rosen, 14
    ]
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen', trick_so_far=trick)
    assert set(codes) == {'SEK'}                           # discard, no undertrump


def test_oben_mode_unaffected_must_follow():
    """Rule f: Oben/Unten unaffected — must follow if able, trump rules N/A."""
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    hand['Rosen'] = [Koenig(8, 'Rosen')]
    codes = get_valid_cards(hand, 'Eicheln', 'Oben', trick_so_far=[
        {"position": "compe", "card": "EK"},
    ])
    assert codes == ['EA']                                 # must follow, no trump rule


def test_unten_mode_cant_follow_any_card():
    """Unten: can't follow → any card."""
    hand = {suit: [] for suit in SUITS}
    hand['Schellen'] = [Koenig(8, 'Schellen')]
    codes = get_valid_cards(hand, 'Eicheln', 'Unten')
    assert set(codes) == {'SEK'}


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
    assert trick_points(trick, 'Oben') == 81  # (10+4+11+2) * 3 (Oben multiplier)


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
