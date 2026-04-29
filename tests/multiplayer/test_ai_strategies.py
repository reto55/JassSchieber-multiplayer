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
