"""PIMC engine (ausbau/ai_pimc.py) unit tests — seeded and deterministic."""
import random
import pytest

from Cards_refactored import SUITS, create_card, Under
from ausbau.game_session import RANK_SUFFIX, card_to_code, PLAYERS
from ausbau import ai_pimc

_INVERSE_RANK = {v: k for k, v in RANK_SUFFIX.items()}


def _hand(suit_to_suffixes):
    """Build a {suit: [Card,...]} hand dict from {suit: 'AKO...'} suffixes."""
    h = {s: [] for s in SUITS}
    for suit, suffixes in suit_to_suffixes.items():
        for suf in suffixes:
            h[suit].append(create_card(_INVERSE_RANK[suf], suit))
    return h


def test_engine_state_holds_fields():
    state = ai_pimc.EngineState(
        me="comps",
        operator="Schellen",
        partner={"comps": "compn", "compn": "comps", "compo": "compe", "compe": "compo"},
        folger={"comps": "compo", "compo": "compn", "compn": "compe", "compe": "comps"},
        my_hand=_hand({"Schellen": "AK"}),
        others=["compo", "compn", "compe"],
        hand_sizes={"compo": 1, "compn": 1, "compe": 1},
        voids={"compo": set(), "compn": set(), "compe": set()},
        no_trump_except_under=set(),
        unseen=[create_card(_INVERSE_RANK["O"], "Schellen")],
    )
    assert state.me == "comps"
    assert state.operator == "Schellen"
    assert state.others == ["compo", "compn", "compe"]
    assert len(state.unseen) == 1
