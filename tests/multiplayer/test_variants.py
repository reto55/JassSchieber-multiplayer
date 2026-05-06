"""Tests for variant arithmetic (Task 17).

Spec §7 covers three optional rule variants exposed via ``Variant``:

  - ``trumpf_bock`` (default ``False``): when True, every trick in a
    trump-mode round (``operator in SUITS``) has its trick points
    multiplied by 5. Weis and Stöck are NOT affected. ``Oben`` /
    ``Unten`` rounds are NOT affected.
  - ``match_bonus`` (default ``True``): when one team wins all 9 tricks
    of a Spiel AND ``match_bonus`` is True, +100 is added to that team's
    score. Mixed-winner spiele get nothing.
  - ``stoeck`` (default ``True``): when True, the existing ``detect_stock``
    detection awards +20 to the holding player's team. When False, no
    bonus is granted regardless of holdings.

Per spec §7.5, ALL variant arithmetic is server-side. These tests
exercise the helpers (``trick_points`` kwarg, ``_apply_match_bonus``,
``_apply_stoeck``) directly. Wiring into the spiel-end flow happens in
Task 18; here we only verify the math.
"""

from unittest.mock import patch

import pytest

from Cards_refactored import Ass, Banner, Koenig, Ober, Play, Under
from ausbau.game_session import GameSession, trick_points
from ausbau.room import Variant
from frontend.auth.guest import Guest


def _session(*, trumpf_bock=False, match_bonus=True, stoeck=True):
    g = Guest(guest_id='a' * 32)
    return GameSession(
        code="A",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(
            trumpf_bock=trumpf_bock,
            match_bonus=match_bonus,
            stoeck=stoeck,
        ),
    )


# ─── trumpf_bock ──────────────────────────────────────────────────────


def test_trumpf_bock_off_trump_round():
    """Trump-mode round, ``trumpf_bock=False`` → points NOT multiplied."""
    # Eicheln Ass (trump, +11), Eicheln Koenig (trump, +4),
    # Rosen Ass (non-trump, +11), Rosen Koenig (non-trump, +4) = 30.
    trick = {
        "compo": Ass(rank=9, suit="Eicheln"),
        "compn": Koenig(rank=8, suit="Eicheln"),
        "compe": Ass(rank=9, suit="Rosen"),
        "comps": Koenig(rank=8, suit="Rosen"),
    }
    pts = trick_points(trick, "Eicheln", trumpf_bock=False)
    assert pts == 11 + 4 + 11 + 4
    # And again with the kwarg unset (default).
    assert trick_points(trick, "Eicheln") == 30


def test_trumpf_bock_on_trump_round():
    """Trump-mode round, ``trumpf_bock=True`` → points × 5."""
    trick = {
        "compo": Ass(rank=9, suit="Eicheln"),
        "compn": Koenig(rank=8, suit="Eicheln"),
        "compe": Ass(rank=9, suit="Rosen"),
        "comps": Koenig(rank=8, suit="Rosen"),
    }
    pts = trick_points(trick, "Eicheln", trumpf_bock=True)
    assert pts == 30 * 5


def test_trumpf_bock_no_effect_on_oben():
    """Oben round, ``trumpf_bock=True`` → bock NOT applied (not a trump
    mode). The Oben mode multiplier ×3 still applies."""
    # Oben values: Ass=11, Koenig=4, Banner=10, Under=2 = 27 → ×3 = 81.
    trick = {
        "compo": Ass(rank=9, suit="Eicheln"),
        "compn": Koenig(rank=8, suit="Rosen"),
        "compe": Banner(rank=5, suit="Schellen"),
        "comps": Under(rank=6, suit="Schilten"),
    }
    pts = trick_points(trick, "Oben", trumpf_bock=True)
    assert pts == (11 + 4 + 10 + 2) * 3


def test_trumpf_bock_no_effect_on_unten():
    """Unten round, ``trumpf_bock=True`` → bock NOT applied. Unten
    mode multiplier ×3 still applies."""
    # Unten values: Ass=0, Koenig=4, Banner=10, Under=2 = 16 → ×3 = 48.
    trick = {
        "compo": Ass(rank=9, suit="Eicheln"),
        "compn": Koenig(rank=8, suit="Rosen"),
        "compe": Banner(rank=5, suit="Schellen"),
        "comps": Under(rank=6, suit="Schilten"),
    }
    pts = trick_points(trick, "Unten", trumpf_bock=True)
    assert pts == (0 + 4 + 10 + 2) * 3


# ─── match_bonus ──────────────────────────────────────────────────────


def test_match_bonus_on_9_for_sn():
    """All 9 tricks won by SN, ``match_bonus=True`` → +100 SN, 0 OW."""
    s = _session(match_bonus=True)
    s._spiel_trick_winners = ["compn", "comps"] * 4 + ["compn"]  # 9 SN
    assert s._apply_match_bonus() == (100, 0)


def test_match_bonus_on_9_for_ow():
    """All 9 tricks won by OW, ``match_bonus=True`` → 0 SN, +100 OW."""
    s = _session(match_bonus=True)
    s._spiel_trick_winners = ["compo", "compe"] * 4 + ["compo"]  # 9 OW
    assert s._apply_match_bonus() == (0, 100)


def test_match_bonus_off_no_bonus_even_on_match():
    """``match_bonus=False`` → no bonus even if one team won all 9."""
    s = _session(match_bonus=False)
    s._spiel_trick_winners = ["compn"] * 9
    assert s._apply_match_bonus() == (0, 0)


def test_match_bonus_split_winners_no_bonus():
    """Mixed winners, ``match_bonus=True`` → no bonus."""
    s = _session(match_bonus=True)
    s._spiel_trick_winners = (
        ["compn"] * 5 + ["compo"] * 4
    )
    assert s._apply_match_bonus() == (0, 0)


def test_match_bonus_incomplete_spiel_no_bonus():
    """Fewer than 9 tricks recorded → no bonus, even if all SN."""
    s = _session(match_bonus=True)
    s._spiel_trick_winners = ["compn"] * 8
    assert s._apply_match_bonus() == (0, 0)


def test_reset_spiel_trick_winners():
    """Helper resets the per-spiel trick-winner list."""
    s = _session()
    s._spiel_trick_winners = ["compn"] * 9
    s._reset_spiel_trick_winners()
    assert s._spiel_trick_winners == []


@pytest.mark.asyncio
async def test_play_trick_appends_to_spiel_winners():
    """Multi-seat ``_play_trick`` appends winner to ``_spiel_trick_winners``."""
    from tests.multiplayer.conftest import seat_4_humans
    from ausbau.game_session import PLAYERS, get_valid_cards, card_to_code

    s = _session()
    seat_4_humans(s)
    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    seat_order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        seat_order.append(nxt)
        nxt = play.folger[nxt]

    lead_suit = None
    hands = {pos: {suit: list(getattr(play, pos)[suit]) for suit in getattr(play, pos)}
             for pos in PLAYERS}
    player = seat_order[0]
    for i in range(4):
        valid = get_valid_cards(hands[player], lead_suit, play.operator)
        code = valid[0]
        for suit, cards in hands[player].items():
            for card in cards:
                if card_to_code(card) == code:
                    cards.remove(card)
                    if i == 0:
                        lead_suit = suit
                    break
            else:
                continue
            break
        s._seat(player).incoming.put_nowait({"type": "play_card", "card": code})
        player = play.folger[player]

    assert s._spiel_trick_winners == []
    winner, _ = await s._play_trick(play)
    assert s._spiel_trick_winners == [winner]


# ─── stoeck ───────────────────────────────────────────────────────────


def test_stoeck_on_sn_holds():
    """``stoeck=True`` and one SN seat holds K+O of trump → (20, 0)."""
    s = _session(stoeck=True)
    play = Play(spiel=1)
    play.operator = "Eicheln"

    def fake_detect(hand, op):
        return hand is play.compn  # exactly one SN seat holds it

    with patch("ausbau.game_session.detect_stock", side_effect=fake_detect):
        assert s._apply_stoeck(play) == (20, 0)


def test_stoeck_on_ow_holds():
    """``stoeck=True`` and one OW seat holds K+O of trump → 20 ×
    Schilten multiplier (×2) = 40 OW."""
    s = _session(stoeck=True)
    play = Play(spiel=1)
    play.operator = "Schilten"

    def fake_detect(hand, op):
        return hand is play.compe  # exactly one OW seat holds it

    with patch("ausbau.game_session.detect_stock", side_effect=fake_detect):
        assert s._apply_stoeck(play) == (0, 40)


def test_stoeck_off_no_bonus_even_when_holding():
    """``stoeck=False`` → no bonus regardless of holdings."""
    s = _session(stoeck=False)
    play = Play(spiel=1)
    play.operator = "Eicheln"

    with patch("ausbau.game_session.detect_stock", return_value=True):
        assert s._apply_stoeck(play) == (0, 0)


def test_stoeck_oben_unten_no_effect():
    """No-trump modes never award stöck."""
    s = _session(stoeck=True)
    play = Play(spiel=1)
    play.operator = "Oben"

    with patch("ausbau.game_session.detect_stock", return_value=True):
        # detect_stock would return False internally for Oben/Unten anyway
        # but the helper's gate on ``operator in SUITS`` is the real check.
        assert s._apply_stoeck(play) == (0, 0)

    play.operator = "Unten"
    with patch("ausbau.game_session.detect_stock", return_value=True):
        assert s._apply_stoeck(play) == (0, 0)
