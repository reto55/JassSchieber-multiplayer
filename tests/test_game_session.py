import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
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
    asyncio.run(session._trump_phase_legacy(ws, play))

    assert play.operator == "Eicheln"
    calls = [c[0][0] for c in ws.send_json.call_args_list]
    assert calls[0]['type'] == 'trump_request'
    assert calls[0]['can_schieben'] is True
    assert calls[1]['type'] == 'trump_chosen'
    assert calls[1]['suit'] == 'Eicheln'


def test_trump_phase_human_leads_schiebt():
    """Human schiebt → partner Nord (AI) chooses via determine_trumpf_after_schieben()."""
    session = GameSession()
    play = Play(4)
    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={"type": "schieben"})
    asyncio.run(session._trump_phase_legacy(ws, play))

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


# --- Trick-end payload contract (defect D1) -------------------------------

def _drive_single_trick(session, play, human_card_code):
    """Run one trick with the human replying with `human_card_code`.
    Returns the AsyncMock WebSocket so the caller can inspect sent messages.
    """
    from unittest.mock import AsyncMock, patch
    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={"type": "play_card", "card": human_card_code})
    # skip the AI think-pause so tests run instantly
    with patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        result = asyncio.run(session._play_trick(ws, play))
    return ws, result


def test_play_trick_returns_winner_and_points():
    """_play_trick must return (winner_key, points_int) so _run_spiel can emit `points`."""
    session = GameSession()
    play = Play(4)  # comps leads
    human_card = hand_to_codes(play.comps)[0]
    ws, result = _drive_single_trick(session, play, human_card)

    # New contract: return value is a (winner, pts) tuple, not just winner.
    assert isinstance(result, tuple), f"_play_trick must return a tuple, got {type(result).__name__}"
    assert len(result) == 2
    winner, pts = result
    assert winner in {'comps', 'compo', 'compn', 'compe'}
    assert isinstance(pts, int)
    assert pts >= 0


def test_run_spiel_trick_end_includes_points_key():
    """The trick_end payload must carry a `points` key with the per-trick integer value."""
    from unittest.mock import AsyncMock, patch

    session = GameSession()
    ws = AsyncMock()

    # Stub every phase except the trick loop so we can observe exactly 9 trick_end payloads.
    async def _noop_trump(self, websocket, play):
        play.operator = 'Eicheln'
        play.starter = 'comps'

    async def _noop_weis(self, websocket, play):
        return

    fake_trick_values = iter([7, 11, 3, 9, 4, 0, 6, 14, 2])

    async def _fake_play_trick(self, websocket, play):
        return ('comps', next(fake_trick_values))

    with patch.object(GameSession, '_trump_phase_legacy', _noop_trump), \
         patch.object(GameSession, '_weis_phase', _noop_weis), \
         patch.object(GameSession, '_play_trick', _fake_play_trick), \
         patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        asyncio.run(session._run_spiel(ws, 4))

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    trick_ends = [m for m in sent if m.get('type') == 'trick_end']
    assert len(trick_ends) == 9, f"expected 9 trick_end messages, got {len(trick_ends)}"

    expected = [7, 11, 3, 9, 4, 0, 6, 14, 2]
    for i, msg in enumerate(trick_ends):
        assert 'points' in msg, f"trick_end #{i} missing required `points` key: {msg}"
        assert isinstance(msg['points'], int), f"trick_end #{i}.points is not an int: {msg}"
        assert msg['points'] == expected[i], (
            f"trick_end #{i}.points={msg['points']}, expected {expected[i]}"
        )
        # running totals remain available (skill: optional, backend still emits)
        assert isinstance(msg.get('points_sn'), int), f"points_sn not int: {msg}"
        assert isinstance(msg.get('points_ow'), int), f"points_ow not int: {msg}"
        assert msg['winner_key'] in {'comps', 'compo', 'compn', 'compe'}


# --- round_end normalization (defects D3 + D8) ----------------------------

def _drive_run_spiel_and_collect(session_scores):
    """Run a single spiel with stubbed phases; return the sent messages list.

    ``session_scores`` is a (sn, ow) tuple applied to the GameSession just
    before ``_run_spiel`` fires round_end, so the test can control the
    round totals observable in the payload.
    """
    from unittest.mock import AsyncMock, patch

    session = GameSession(end_game=1000)
    ws = AsyncMock()

    async def _noop_trump(self, websocket, play):
        play.operator = 'Eicheln'
        play.starter = 'comps'

    async def _noop_weis(self, websocket, play):
        return

    sn, ow = session_scores
    # We produce 0-point tricks and then mutate the session score right after
    # the 9th trick but before round_end runs. We achieve that by using a
    # side-effect-bearing fake for trick #9 specifically.
    call_count = {'n': 0}

    async def _fake_play_trick(self, websocket, play):
        call_count['n'] += 1
        if call_count['n'] == 9:
            # Set the final totals immediately before round_end is emitted
            self.point_sn = sn
            self.point_ow = ow
        return ('comps', 0)

    with patch.object(GameSession, '_trump_phase_legacy', _noop_trump), \
         patch.object(GameSession, '_weis_phase', _noop_weis), \
         patch.object(GameSession, '_play_trick', _fake_play_trick), \
         patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        asyncio.run(session._run_spiel(ws, 4))

    return [c[0][0] for c in ws.send_json.call_args_list]


def test_round_end_winner_team_sn_token():
    """round_end.winner_team is 'sn' when SN scored higher this round."""
    # SN already leads after the last trick (comps wins trick 9 → +5 bonus → sn=105)
    sent = _drive_run_spiel_and_collect(session_scores=(100, 50))
    round_end = [m for m in sent if m.get('type') == 'round_end'][-1]
    assert round_end['winner_team'] == 'sn', round_end


def test_round_end_winner_team_ow_token():
    """round_end.winner_team is 'ow' when OW scored higher this round."""
    # OW started ahead; comps wins trick 9 → +5 on SN, but still less than 200
    sent = _drive_run_spiel_and_collect(session_scores=(50, 200))
    round_end = [m for m in sent if m.get('type') == 'round_end'][-1]
    assert round_end['winner_team'] == 'ow', round_end


def test_round_end_winner_team_tie_token():
    """round_end.winner_team is 'tie' when round totals are equal."""
    # Pre-trick-9 totals set to (95, 100); comps wins trick 9 → +5 → (100,100)
    sent = _drive_run_spiel_and_collect(session_scores=(95, 100))
    round_end = [m for m in sent if m.get('type') == 'round_end'][-1]
    assert round_end['winner_team'] == 'tie', round_end


def test_round_end_has_target_int():
    """round_end must carry the `target` field (int) per skill contract."""
    sent = _drive_run_spiel_and_collect(session_scores=(100, 50))
    round_end = [m for m in sent if m.get('type') == 'round_end'][-1]
    assert 'target' in round_end, f"round_end missing target: {round_end}"
    assert isinstance(round_end['target'], int)
    assert round_end['target'] == 1000  # matches GameSession(end_game=1000)


def test_round_end_field_set_matches_skill():
    """round_end carries exactly {type, score_sn, score_ow, winner_team, target}."""
    sent = _drive_run_spiel_and_collect(session_scores=(100, 50))
    round_end = [m for m in sent if m.get('type') == 'round_end'][-1]
    assert set(round_end.keys()) == {
        'type', 'score_sn', 'score_ow', 'winner_team', 'target'
    }, f"unexpected round_end keys: {round_end.keys()}"


# --- declare_weis subset selection (defect D6) ----------------------------

def test_weis_phase_subset_announces_only_selected():
    """announce=True + weis=['Dreier'] → only the Dreier is announced, Vierter dropped."""
    from unittest.mock import AsyncMock, patch

    session = GameSession()
    play = Play(1)

    human_weis = [
        {'name': 'Dreier', 'suit': 'Eicheln', 'points': 20},
        {'name': 'Vierter', 'suit': 'Rosen', 'points': 50},
    ]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={
        "type": "declare_weis",
        "weis": ["Dreier"],
        "announce": True,
    })

    # Patch describe_weis so the HUMAN sees both, but AI players see none.
    call_counter = {'n': 0}

    def _fake_describe(combos, gleiche):
        call_counter['n'] += 1
        # First invocation is for the human (play.comps); rest are AI.
        return human_weis if call_counter['n'] == 1 else []

    with patch('ausbau.game_session.describe_weis', side_effect=_fake_describe):
        asyncio.run(session._weis_phase(ws, play))

    last = ws.send_json.call_args_list[-1][0][0]
    assert last['type'] == 'weis_result'
    sued = [a for a in last['announcements'] if a['player'] == 'Süd']
    assert len(sued) == 1, f"expected exactly one Süd announcement: {last}"
    names = [w['name'] for w in sued[0]['weis']]
    assert names == ['Dreier'], f"expected only Dreier, got {names}"
    assert sued[0]['points'] == 20
    # Only 20 points should have been added to SN (no Vierter's 50).
    assert session.point_sn == 20


def test_weis_phase_empty_weis_with_announce_true_keeps_all():
    """announce=True + missing/empty weis → legacy all-announce behavior preserved."""
    from unittest.mock import AsyncMock, patch

    session = GameSession()
    play = Play(1)

    human_weis = [
        {'name': 'Dreier', 'suit': 'Eicheln', 'points': 20},
        {'name': 'Vierter', 'suit': 'Rosen', 'points': 50},
    ]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={
        "type": "declare_weis",
        "weis": [],           # empty → announce all
        "announce": True,
    })

    call_counter = {'n': 0}

    def _fake_describe(combos, gleiche):
        call_counter['n'] += 1
        return human_weis if call_counter['n'] == 1 else []

    with patch('ausbau.game_session.describe_weis', side_effect=_fake_describe):
        asyncio.run(session._weis_phase(ws, play))

    last = ws.send_json.call_args_list[-1][0][0]
    sued = [a for a in last['announcements'] if a['player'] == 'Süd']
    assert len(sued) == 1
    names = sorted(w['name'] for w in sued[0]['weis'])
    assert names == ['Dreier', 'Vierter'], f"expected all, got {names}"
    assert sued[0]['points'] == 70
    assert session.point_sn == 70


def test_weis_phase_missing_weis_with_announce_true_keeps_all():
    """announce=True with the `weis` key omitted entirely → announce all (legacy)."""
    from unittest.mock import AsyncMock, patch

    session = GameSession()
    play = Play(1)

    human_weis = [
        {'name': 'Dreier', 'suit': 'Eicheln', 'points': 20},
    ]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={
        "type": "declare_weis",
        "announce": True,
        # no 'weis' key at all
    })

    call_counter = {'n': 0}

    def _fake_describe(combos, gleiche):
        call_counter['n'] += 1
        return human_weis if call_counter['n'] == 1 else []

    with patch('ausbau.game_session.describe_weis', side_effect=_fake_describe):
        asyncio.run(session._weis_phase(ws, play))

    assert session.point_sn == 20


def test_weis_phase_announce_false_announces_nothing_even_with_weis():
    """announce=False + weis=['Dreier'] → still declines, nothing announced."""
    from unittest.mock import AsyncMock, patch

    session = GameSession()
    play = Play(1)

    human_weis = [
        {'name': 'Dreier', 'suit': 'Eicheln', 'points': 20},
    ]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={
        "type": "declare_weis",
        "weis": ["Dreier"],
        "announce": False,
    })

    call_counter = {'n': 0}

    def _fake_describe(combos, gleiche):
        call_counter['n'] += 1
        return human_weis if call_counter['n'] == 1 else []

    with patch('ausbau.game_session.describe_weis', side_effect=_fake_describe):
        asyncio.run(session._weis_phase(ws, play))

    last = ws.send_json.call_args_list[-1][0][0]
    sued = [a for a in last['announcements'] if a['player'] == 'Süd']
    assert sued == []
    assert session.point_sn == 0


def test_weis_phase_subset_with_nonexistent_name_drops_it():
    """Names not present in offered human_weis are silently dropped; matching is exact."""
    from unittest.mock import AsyncMock, patch

    session = GameSession()
    play = Play(1)

    human_weis = [
        {'name': 'Dreier', 'suit': 'Eicheln', 'points': 20},
        {'name': 'Vierter', 'suit': 'Rosen', 'points': 50},
    ]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={
        "type": "declare_weis",
        "weis": ["Dreier", "Viererle"],  # Viererle was not offered
        "announce": True,
    })

    call_counter = {'n': 0}

    def _fake_describe(combos, gleiche):
        call_counter['n'] += 1
        return human_weis if call_counter['n'] == 1 else []

    with patch('ausbau.game_session.describe_weis', side_effect=_fake_describe):
        asyncio.run(session._weis_phase(ws, play))

    last = ws.send_json.call_args_list[-1][0][0]
    sued = [a for a in last['announcements'] if a['player'] == 'Süd']
    names = [w['name'] for w in sued[0]['weis']]
    assert names == ['Dreier'], f"expected only Dreier, got {names}"
    assert session.point_sn == 20


def test_game_end_winner_team_is_normalized_token():
    """game_end.winner_team must be 'sn' | 'ow' | 'tie' — not the long strings from get_winner."""
    from unittest.mock import AsyncMock, patch
    session = GameSession(end_game=50)
    session.point_sn = 60
    session.point_ow = 30
    ws = AsyncMock()

    async def _fake_spiel(self, websocket, spiel_num):
        return

    with patch.object(GameSession, '_run_spiel', _fake_spiel):
        asyncio.run(session.run(ws))

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    game_end = [m for m in sent if m.get('type') == 'game_end']
    assert len(game_end) == 1
    assert game_end[0]['winner_team'] in {'sn', 'ow', 'tie'}
    assert game_end[0]['winner_team'] == 'sn'
    assert game_end[0]['final_scores'] == {'sn': 60, 'ow': 30}


def test_game_end_winner_team_tie():
    from unittest.mock import AsyncMock, patch
    session = GameSession(end_game=50)
    session.point_sn = 55
    session.point_ow = 55
    ws = AsyncMock()

    async def _fake_spiel(self, websocket, spiel_num):
        return

    with patch.object(GameSession, '_run_spiel', _fake_spiel):
        asyncio.run(session.run(ws))

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    game_end = [m for m in sent if m.get('type') == 'game_end']
    assert game_end[0]['winner_team'] == 'tie'


# --- D9: trump-phase message-type discriminator ---------------------------

def test_trump_phase_rejects_invalid_type_then_accepts_choose_trump():
    """Human sends wrong `type` during trump prompt → server errors + re-prompts; valid reply still wins."""
    from unittest.mock import AsyncMock
    session = GameSession()
    play = Play(4)  # comps leads

    ws = AsyncMock()
    # First message has bogus type (note: it still carries a `suit` key, which
    # the OLD permissive branch would have accepted silently). Second is valid.
    ws.receive_json = AsyncMock(side_effect=[
        {"type": "play_card", "card": "EA", "suit": "Schellen"},
        {"type": "choose_trump", "suit": "Eicheln"},
    ])
    asyncio.run(session._trump_phase_legacy(ws, play))

    # operator must reflect the VALID message, not the injected bogus suit.
    assert play.operator == "Eicheln"
    assert play.starter == 'comps'

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    types = [m['type'] for m in sent]

    # Exactly one error, two trump_request prompts (initial + re-prompt), one trump_chosen.
    assert types.count('error') == 1, f"expected 1 error, sequence was: {types}"
    assert types.count('trump_request') == 2, f"expected 2 trump_request, sequence was: {types}"
    assert types.count('trump_chosen') == 1
    # Ordering: trump_request, error, trump_request, trump_chosen.
    assert types == ['trump_request', 'error', 'trump_request', 'trump_chosen'], types
    # Re-prompt must carry can_schieben=True (same prompt as the initial one).
    assert sent[2]['can_schieben'] is True


def test_trump_phase_rejects_schieben_when_disallowed():
    """AI schiebs to human partner — `schieben` from human is invalid; server errors + re-prompts."""
    from unittest.mock import AsyncMock
    session = GameSession()
    # Spiel 2 → compn leads. Force the post-schieben branch where partner == comps.
    play = Play(2)
    play.operator = 'Schieben'

    ws = AsyncMock()
    ws.receive_json = AsyncMock(side_effect=[
        {"type": "schieben"},  # not allowed: can_schieben was False
        {"type": "choose_trump", "suit": "Rosen"},
    ])
    asyncio.run(session._trump_phase_legacy(ws, play))

    assert play.operator == "Rosen"
    assert play.starter == 'comps'

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    types = [m['type'] for m in sent]
    assert types.count('error') == 1, types
    assert types.count('trump_request') == 2, types
    # re-prompt carries can_schieben=False (schieben not permitted here)
    trump_requests = [m for m in sent if m['type'] == 'trump_request']
    assert all(tr['can_schieben'] is False for tr in trump_requests), trump_requests


def test_trump_phase_rejects_invalid_type_in_post_schieben_branch():
    """Post-schieben branch (partner==comps): non-choose_trump messages are rejected."""
    from unittest.mock import AsyncMock
    session = GameSession()
    play = Play(2)
    play.operator = 'Schieben'

    ws = AsyncMock()
    ws.receive_json = AsyncMock(side_effect=[
        {"type": "play_card", "card": "EA"},  # wrong type
        {"type": "choose_trump", "suit": "Schilten"},
    ])
    asyncio.run(session._trump_phase_legacy(ws, play))

    assert play.operator == "Schilten"
    sent = [c[0][0] for c in ws.send_json.call_args_list]
    types = [m['type'] for m in sent]
    assert types == ['trump_request', 'error', 'trump_request', 'trump_chosen'], types


def test_trump_phase_loops_on_repeated_invalid_input():
    """Multiple invalid messages in a row all get error + re-prompt until valid arrives."""
    from unittest.mock import AsyncMock
    session = GameSession()
    play = Play(4)

    ws = AsyncMock()
    ws.receive_json = AsyncMock(side_effect=[
        {"type": "play_card", "card": "EA"},
        {"type": "declare_weis", "announce": True},
        {"type": "garbage"},
        {"type": "choose_trump", "suit": "Rosen"},
    ])
    asyncio.run(session._trump_phase_legacy(ws, play))

    assert play.operator == "Rosen"
    sent = [c[0][0] for c in ws.send_json.call_args_list]
    types = [m['type'] for m in sent]
    assert types.count('error') == 3, types
    assert types.count('trump_request') == 4, types  # initial + 3 re-prompts
    assert types[-1] == 'trump_chosen'


def test_trump_phase_schieben_still_works_when_allowed():
    """Regression: valid `schieben` in the leading branch must still be honored."""
    from unittest.mock import AsyncMock
    session = GameSession()
    play = Play(4)

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={"type": "schieben"})
    asyncio.run(session._trump_phase_legacy(ws, play))

    assert play.starter == 'compn'  # partner takes over after schieben
    # operator set by AI partner via determine_trumpf_after_schieben()
    assert play.operator in ['Eicheln', 'Rosen', 'Schellen', 'Schilten', 'Oben', 'Unten']
    sent = [c[0][0] for c in ws.send_json.call_args_list]
    types = [m['type'] for m in sent]
    # No errors on the happy path.
    assert 'error' not in types, types


# --- Task 15 / step 4: 4-Spiele cycle ------------------------------------

def test_run_cycles_four_spiele_and_ends():
    """`GameSession.run` must cycle spiel_num 1→2→3→4 and then emit `game_end`.

    We stub `_run_spiel` with an async function that (a) records the
    `spiel_num` it was called with and (b) bumps `point_sn` by 300 each
    call. With end_game=1000 this guarantees `check_game_end` fires
    exactly after the 4th Spiel (totals: 300, 600, 900, 1200 → crosses
    target at call 4). The test asserts the call sequence AND that a
    final `game_end` payload is sent.
    """
    from unittest.mock import AsyncMock, patch

    session = GameSession(end_game=1000)
    ws = AsyncMock()
    seen = []

    async def _fake_run_spiel(self, websocket, spiel_num):
        seen.append(spiel_num)
        self.point_sn += 300

    with patch.object(GameSession, '_run_spiel', _fake_run_spiel), \
         patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        asyncio.run(session.run(ws))

    # spiel_num cycles 1,2,3,4 in order, exactly 4 calls.
    assert seen == [1, 2, 3, 4], f"expected [1,2,3,4], got {seen}"

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    game_end = [m for m in sent if m.get('type') == 'game_end']
    assert len(game_end) == 1, f"expected exactly one game_end, got {len(game_end)}"
    assert game_end[0]['winner_team'] == 'sn'
    assert game_end[0]['final_scores'] == {'sn': 1200, 'ow': 0}


def test_run_cycles_wrap_after_fourth_spiel():
    """If end_game is not yet reached after Spiel 4, spiel_num wraps back to 1."""
    from unittest.mock import AsyncMock, patch

    session = GameSession(end_game=1000)
    ws = AsyncMock()
    seen = []

    async def _fake_run_spiel(self, websocket, spiel_num):
        seen.append(spiel_num)
        # 100 points per Spiel → need 10 Spiele to cross end_game.
        self.point_sn += 100

    with patch.object(GameSession, '_run_spiel', _fake_run_spiel), \
         patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        asyncio.run(session.run(ws))

    # Must wrap: 1,2,3,4,1,2,3,4,1,2 → 1000 at call 10 triggers end.
    assert seen[:4] == [1, 2, 3, 4]
    assert seen[4] == 1, f"spiel_num must wrap to 1 after 4, got {seen[4]}"
    assert seen == [1, 2, 3, 4, 1, 2, 3, 4, 1, 2], seen


# --- E4.1: _play_trick malformed-message hardening ------------------------

def test_play_trick_rejects_wrong_type_then_accepts_valid():
    """Human sends a message whose `type` is not `play_card` → server errors + re-prompts.
    When a legitimate `play_card` finally arrives, the trick proceeds normally.
    """
    from unittest.mock import AsyncMock, patch
    session = GameSession()
    play = Play(4)  # comps leads
    human_card = hand_to_codes(play.comps)[0]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(side_effect=[
        {"type": "noise"},                                # wrong type
        {"type": "play_card", "card": human_card},        # valid
    ])
    with patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        asyncio.run(session._play_trick(ws, play))

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    # Must contain at least: your_turn, error, your_turn, card_played(for human)
    types = [m['type'] for m in sent]
    assert 'error' in types, f"expected an error payload, sequence was: {types}"
    # Exactly one error for the single malformed message.
    assert types.count('error') == 1, f"expected 1 error, sequence was: {types}"
    # your_turn appears at least twice: initial prompt + re-prompt after error.
    assert types.count('your_turn') >= 2, f"expected >=2 your_turn, sequence was: {types}"
    # Initial your_turn → error → re-prompt your_turn, then card_played for human.
    first_yt = types.index('your_turn')
    err_idx = types.index('error')
    assert first_yt < err_idx, f"your_turn must precede error: {types}"
    # re-prompt (second your_turn) must come right after the error
    assert types[err_idx + 1] == 'your_turn', (
        f"re-prompt must follow error, got: {types}"
    )


def test_play_trick_rejects_missing_card_key_then_accepts_valid():
    """Human sends `{\"type\": \"play_card\"}` with no `card` → server errors + re-prompts."""
    from unittest.mock import AsyncMock, patch
    session = GameSession()
    play = Play(4)
    human_card = hand_to_codes(play.comps)[0]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(side_effect=[
        {"type": "play_card"},                            # missing card
        {"type": "play_card", "card": human_card},        # valid
    ])
    with patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        asyncio.run(session._play_trick(ws, play))

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    types = [m['type'] for m in sent]
    assert types.count('error') == 1, f"expected 1 error, got: {types}"
    assert types.count('your_turn') >= 2, types


def test_play_trick_non_string_card_rejected():
    """Human sends `card` as a non-string → server errors + re-prompts, survives."""
    from unittest.mock import AsyncMock, patch
    session = GameSession()
    play = Play(4)
    human_card = hand_to_codes(play.comps)[0]

    ws = AsyncMock()
    ws.receive_json = AsyncMock(side_effect=[
        {"type": "play_card", "card": 42},                # non-string card
        {"type": "play_card", "card": human_card},        # valid
    ])
    with patch('ausbau.game_session.asyncio.sleep', new=AsyncMock()):
        asyncio.run(session._play_trick(ws, play))

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    types = [m['type'] for m in sent]
    assert types.count('error') == 1, types


# --- E4.2: server-level protocol-shaped error on uncaught exception -------

@pytest.mark.skip(reason="legacy single-WS /ws error-handling removed in multiplayer Task 9; "
                         "new /ws/{code} endpoint has per-room connection logic")
def test_server_sends_error_payload_before_close_on_unexpected_exception():
    """If GameSession.run raises a non-WebSocketDisconnect exception, the /ws handler
    must send a protocol-shaped `{type: "error", message: "..."}` payload before closing.
    """
    from unittest.mock import AsyncMock, patch
    import importlib

    # Import the module fresh so we can monkeypatch its GameSession.
    from ausbau import server as server_mod

    ws = AsyncMock()
    # receive_json should never be reached — we raise during run().
    # .send_json and .close are AsyncMocks by default.

    async def _boom_run(self, websocket):
        raise RuntimeError("synthetic failure in GameSession.run")

    with patch.object(server_mod.GameSession, 'run', _boom_run):
        asyncio.run(server_mod.websocket_endpoint(ws))

    # Collect every send_json payload
    sent = [c[0][0] for c in ws.send_json.call_args_list]
    error_msgs = [m for m in sent if isinstance(m, dict) and m.get('type') == 'error']
    assert len(error_msgs) >= 1, (
        f"expected an error payload before close, sent: {sent}"
    )
    # Must carry a message string
    assert isinstance(error_msgs[-1].get('message'), str)
    assert error_msgs[-1]['message']  # non-empty

    # close() must have been called
    assert ws.close.await_count >= 1 or ws.close.call_count >= 1, (
        "websocket.close() must be invoked after the error payload"
    )


@pytest.mark.skip(reason="legacy single-WS /ws error-handling removed in multiplayer Task 9; "
                         "new /ws/{code} endpoint has per-room connection logic")
def test_server_disconnect_does_not_send_error_payload():
    """Regression: WebSocketDisconnect is the clean-exit path — no error payload."""
    from unittest.mock import AsyncMock, patch
    from fastapi import WebSocketDisconnect
    from ausbau import server as server_mod

    ws = AsyncMock()

    async def _disconnect_run(self, websocket):
        raise WebSocketDisconnect(code=1000)

    with patch.object(server_mod.GameSession, 'run', _disconnect_run):
        asyncio.run(server_mod.websocket_endpoint(ws))

    sent = [c[0][0] for c in ws.send_json.call_args_list]
    error_msgs = [m for m in sent if isinstance(m, dict) and m.get('type') == 'error']
    assert error_msgs == [], (
        f"WebSocketDisconnect path must not send an error payload, got: {error_msgs}"
    )


@pytest.mark.skip(reason="legacy single-WS /ws error-handling removed in multiplayer Task 9; "
                         "new /ws/{code} endpoint has per-room connection logic")
def test_server_survives_if_error_send_itself_fails():
    """If the final error-send raises (e.g. socket already half-closed), the handler
    must still fall through to close() without propagating the secondary failure.
    """
    from unittest.mock import AsyncMock, patch
    from ausbau import server as server_mod

    ws = AsyncMock()
    # Make send_json raise to simulate a dead socket.
    ws.send_json = AsyncMock(side_effect=RuntimeError("socket dead"))

    async def _boom_run(self, websocket):
        raise RuntimeError("original failure")

    with patch.object(server_mod.GameSession, 'run', _boom_run):
        # Must not raise
        asyncio.run(server_mod.websocket_endpoint(ws))

    # close was still attempted
    assert ws.close.await_count >= 1 or ws.close.call_count >= 1


# --- Task 23: WS principal injection tests --------------------------------

import pytest


@pytest.mark.skip(reason="legacy single-WS resolve_principal removed in multiplayer Task 9; "
                         "WS attach is now per-room")
@pytest.mark.asyncio
async def test_resolve_principal_returns_guest_when_no_cookies(monkeypatch):
    """resolve_principal returns a fresh Guest when neither cookie is present."""
    # Bypass auth_settings init by stubbing the load
    from frontend.auth.guest import Guest
    import ausbau.server as srv

    monkeypatch.setattr(srv, "_auth_settings", _StubSettings())
    monkeypatch.setattr(srv, "_auth_factory", None)

    class FakeWS:
        cookies = {}

    p = await srv.resolve_principal(FakeWS())
    assert isinstance(p, Guest)


@pytest.mark.skip(reason="legacy single-WS resolve_principal removed in multiplayer Task 9; "
                         "WS attach is now per-room")
@pytest.mark.asyncio
async def test_resolve_principal_returns_user_when_session_cookie_valid(monkeypatch):
    """resolve_principal returns the User from _resolve_user_from_cookie when cookie is valid."""
    import ausbau.server as srv

    fake_user = _StubUser()
    fake_user.username = "testuser"

    async def stub_resolver(token):
        return fake_user

    monkeypatch.setattr(srv, "_auth_settings", _StubSettings())
    monkeypatch.setattr(srv, "_resolve_user_from_cookie", stub_resolver)

    class FakeWS:
        cookies = {"schieber_session": "abc"}

    p = await srv.resolve_principal(FakeWS())
    assert p is fake_user


class _StubSettings:
    secret_key = "k" * 32


class _StubUser:
    pass
