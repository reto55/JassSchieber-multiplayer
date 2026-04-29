import pytest
import random
from Cards_refactored import Play, SUITS
from ausbau.ai_strategies import (
    AIStrategy,
    EasyStrategy,
    MediumStrategy,
    HardStrategy,
    make_strategy,
)


def test_make_strategy_easy():
    s = make_strategy("easy", "compe")
    assert isinstance(s, EasyStrategy)
    assert s.position == "compe"


def test_make_strategy_medium():
    s = make_strategy("medium", "compn")
    assert isinstance(s, MediumStrategy)


def test_make_strategy_hard():
    s = make_strategy("hard", "comps")
    assert isinstance(s, HardStrategy)


def test_make_strategy_unknown():
    with pytest.raises(ValueError, match="unknown difficulty"):
        make_strategy("expert", "compe")


def test_easy_pick_trump_returns_one_of_six_modes():
    random.seed(0)
    s = EasyStrategy("compe")
    play = Play(spiel=1)
    seen = set()
    for _ in range(50):
        msg = s.pick_trump(play, schieben_allowed=True)
        assert msg["type"] == "choose_trump"
        seen.add(msg["operator"])
    # Over 50 calls expect coverage of multiple modes.
    assert len(seen) >= 3
    for op in seen:
        assert op in ("Eicheln", "Rosen", "Schellen", "Schilten", "Oben", "Unten")


def test_easy_pick_trump_never_schiebens():
    random.seed(0)
    s = EasyStrategy("compe")
    play = Play(spiel=1)
    for _ in range(20):
        msg = s.pick_trump(play, schieben_allowed=True)
        assert msg["type"] == "choose_trump"


def test_easy_pick_card_returns_valid_card():
    random.seed(0)
    s = EasyStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    msg = s.pick_card(play, lead_suit=None, trick_so_far=[])
    assert msg["type"] == "play_card"
    # Card must be one of the codes in seat's hand
    from ausbau.game_session import hand_to_codes
    assert msg["card"] in hand_to_codes(play.comps)


def test_medium_pick_trump_uses_farbe_lang():
    from utils.card_utils import farbe_lang
    s = MediumStrategy("comps")
    play = Play(spiel=1)
    msg = s.pick_trump(play, schieben_allowed=True)
    assert msg["type"] == "choose_trump"
    assert msg["operator"] == farbe_lang(play.comps)


def test_medium_pick_trump_never_schiebens():
    s = MediumStrategy("comps")
    play = Play(spiel=1)
    for _ in range(10):
        msg = s.pick_trump(play, schieben_allowed=True)
        assert msg["type"] == "choose_trump"


def test_medium_pick_card_lead_picks_highest_point():
    from ausbau.game_session import ai_select_card, card_to_code
    s = MediumStrategy("compe")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    msg = s.pick_card(play, lead_suit=None, trick_so_far=[])
    expected = card_to_code(ai_select_card(play.compe, None, "Eicheln"))
    assert msg == {"type": "play_card", "card": expected}


def test_medium_pick_card_follow_picks_lowest_point():
    from ausbau.game_session import ai_select_card, card_to_code
    s = MediumStrategy("compn")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    # Lead has been played: pretend lead suit is "Rosen"
    msg = s.pick_card(play, lead_suit="Rosen", trick_so_far=[{"position": "compe", "card": "RA"}])
    expected = card_to_code(ai_select_card(play.compn, "Rosen", "Eicheln"))
    assert msg == {"type": "play_card", "card": expected}


def test_hard_on_spiel_start_populates_remaining():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    # 36 total cards - 9 own = 27 remaining
    total = sum(len(v) for v in s._remaining_by_suit.values())
    assert total == 27
    # All 4 suits keys exist
    assert set(s._remaining_by_suit.keys()) == set(SUITS)


def test_hard_on_spiel_start_excludes_own_hand():
    from ausbau.game_session import hand_to_codes
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    own = set(hand_to_codes(play.comps))
    tracked = {c for codes in s._remaining_by_suit.values() for c in codes}
    assert own.isdisjoint(tracked)


def test_hard_on_card_played_removes_known_card():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    # Pick any tracked card from any suit
    suit, codes = next((k, v) for k, v in s._remaining_by_suit.items() if v)
    code = next(iter(codes))
    s.on_card_played("compo", code)
    assert code not in s._remaining_by_suit[suit]


def test_hard_on_card_played_skips_own_position():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    initial_total = sum(len(v) for v in s._remaining_by_suit.values())
    # Send a "self-play" — own cards aren't tracked anyway, so it's a no-op.
    from ausbau.game_session import hand_to_codes
    own_card = hand_to_codes(play.comps)[0]
    s.on_card_played("comps", own_card)
    after_total = sum(len(v) for v in s._remaining_by_suit.values())
    assert initial_total == after_total


def test_hard_on_card_played_unknown_card_is_noop():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    initial_total = sum(len(v) for v in s._remaining_by_suit.values())
    # Use a code we know is not tracked: pick a card from own hand
    from ausbau.game_session import hand_to_codes
    own_card = hand_to_codes(play.comps)[0]
    s.on_card_played("compo", own_card)  # opponent "playing" something we have — defensive
    after_total = sum(len(v) for v in s._remaining_by_suit.values())
    assert initial_total == after_total  # no crash, no change
