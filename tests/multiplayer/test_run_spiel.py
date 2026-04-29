"""Tests for the multi-seat ``_run_spiel`` + ``start_game`` (Task 18).

Drives a full game with all four seats as AI so no human input is
required. Verifies:

  - ``_game_start_for(None)`` (TV) and ``_game_start_for("compn")``
    payload shapes per the schieber-protocol skill.
  - End-to-end: ``start_game`` runs spiele until ``check_game_end``
    fires, broadcasts ``game_end``, and sets ``state="finished"``.

Caps ``end_game`` low (50) so the loop terminates quickly. Patches
``asyncio.sleep`` so the inter-spiel pause does not delay the test.
"""

import asyncio

import pytest

from Cards_refactored import Play
from ausbau.game_session import GameSession, PLAYERS
from ausbau.room import Spectator, Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket


def _all_ai_session(*, end_game: int = 50):
    """Create a session whose four seats are all AI.

    Note ``create_room`` flips seat 0 to non-AI for the host. We
    explicitly leave all four seats as AI so the game loop never
    blocks on human input.
    """
    g = Guest(guest_id='a' * 32)
    s = GameSession(
        code="A",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
        end_game=end_game,
    )
    # Reset all seats to AI explicitly (default), no principals.
    for seat in s.seats:
        seat.is_ai = True
        seat.principal = None
        seat.websocket = None
    return s


# ─── _game_start_for shape ────────────────────────────────────────────


def test_game_start_for_seat_includes_hand_partner_variant():
    """Per-seat ``game_start`` carries own hand, partner flag, variant block."""
    s = _all_ai_session()
    s.current_play = Play(spiel=1)

    msg = s._game_start_for("compn")
    assert msg["type"] == "game_start"
    assert msg["your_position"] == "compn"
    assert isinstance(msg["your_hand"], list) and len(msg["your_hand"]) == 9
    assert msg["first_player"] in PLAYERS

    # Other 3 seats — exactly one is_partner=True (the partner of compn).
    assert len(msg["players"]) == 3
    partners = [p for p in msg["players"] if p["is_partner"]]
    assert len(partners) == 1
    assert partners[0]["position"] == "comps"  # partner_of(compn) = comps
    for p in msg["players"]:
        assert p["card_count"] == 9
        assert "display_name" in p

    assert msg["scores"] == {"sn": 0, "ow": 0}
    assert msg["target"] == s.end_game
    assert msg["variant"] == {
        "trumpf_bock": False,
        "match_bonus": True,
        "stoeck": True,
    }


def test_game_start_for_spectator_no_hand_no_partner():
    """Spectator (TV) ``game_start``: no hand, lists all 4, no is_partner."""
    s = _all_ai_session()
    s.current_play = Play(spiel=1)

    msg = s._game_start_for(None)
    assert msg["type"] == "game_start"
    assert msg["your_position"] is None
    assert msg["your_hand"] is None
    assert len(msg["players"]) == 4
    for p in msg["players"]:
        assert "is_partner" not in p
        assert p["card_count"] == 9


def test_game_start_for_seat_variant_overrides_propagate():
    """Custom Variant flags appear in ``game_start.variant``."""
    g = Guest(guest_id='a' * 32)
    s = GameSession(
        code="B",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(trumpf_bock=True, match_bonus=False, stoeck=False),
    )
    s.current_play = Play(spiel=1)
    msg = s._game_start_for("compo")
    assert msg["variant"] == {
        "trumpf_bock": True,
        "match_bonus": False,
        "stoeck": False,
    }


# ─── full game loop: start_game with 4 AIs ────────────────────────────


@pytest.mark.asyncio
async def test_start_game_runs_to_completion_4_ai(monkeypatch):
    """Full game loop with 4 AIs terminates with game_end + state=finished."""
    real_sleep = asyncio.sleep

    async def fast_sleep(seconds):  # short-circuit the inter-spiel pause
        await real_sleep(0)

    monkeypatch.setattr("asyncio.sleep", fast_sleep)

    s = _all_ai_session(end_game=50)

    # Attach a single spectator FakeWS to capture broadcasts.
    spec_ws = FakeWebSocket()
    s.spectators.append(Spectator(
        principal=Guest(guest_id="z" * 32),
        websocket=spec_ws,
    ))

    await s.start_game()

    # State flipped to finished.
    assert s.state == "finished"

    # game_end was broadcast (spectator received it).
    game_end_msgs = spec_ws.all_sent_of_type("game_end")
    assert len(game_end_msgs) == 1, (
        f"expected exactly one game_end, got {len(game_end_msgs)}: "
        f"{spec_ws.sent}"
    )
    end = game_end_msgs[0]
    assert end["winner_team"] in {"sn", "ow", "tie"}
    assert "scores" in end
    assert end["scores"]["sn"] == s.point_sn
    assert end["scores"]["ow"] == s.point_ow

    # End-game condition actually held: max(sn, ow) >= end_game (50)
    # OR a tie at >= end_game.
    assert max(s.point_sn, s.point_ow) >= 50

    # At least one spiel_end broadcast was emitted.
    spiel_ends = spec_ws.all_sent_of_type("spiel_end")
    assert len(spiel_ends) >= 1, "expected >=1 spiel_end broadcasts"
    # spiel_end shape contract.
    last_spiel_end = spiel_ends[-1]
    assert "scores" in last_spiel_end
    assert "weis_added" in last_spiel_end
    assert "match" in last_spiel_end
    assert "stoeck_team" in last_spiel_end
    assert isinstance(last_spiel_end["match"], bool)


@pytest.mark.asyncio
async def test_start_game_emits_game_start_per_spiel(monkeypatch):
    """Each spiel emits a fresh ``game_start`` (per-seat)."""
    real_sleep = asyncio.sleep

    async def fast_sleep(seconds):
        await real_sleep(0)

    monkeypatch.setattr("asyncio.sleep", fast_sleep)

    s = _all_ai_session(end_game=50)

    spec_ws = FakeWebSocket()
    s.spectators.append(Spectator(
        principal=Guest(guest_id="y" * 32),
        websocket=spec_ws,
    ))

    await s.start_game()

    game_starts = spec_ws.all_sent_of_type("game_start")
    spiel_ends = spec_ws.all_sent_of_type("spiel_end")
    # One game_start per spiel, one spiel_end per spiel.
    assert len(game_starts) == len(spiel_ends), (
        f"game_start count {len(game_starts)} != spiel_end count "
        f"{len(spiel_ends)}"
    )
    # Spectator's game_start is the TV-mode one.
    for gs in game_starts:
        assert gs["your_position"] is None
        assert gs["your_hand"] is None
        assert len(gs["players"]) == 4


@pytest.mark.asyncio
async def test_start_game_state_transitions(monkeypatch):
    """state goes lobby → playing → finished."""
    real_sleep = asyncio.sleep

    async def fast_sleep(seconds):
        await real_sleep(0)

    monkeypatch.setattr("asyncio.sleep", fast_sleep)

    s = _all_ai_session(end_game=50)
    assert s.state == "lobby"

    await s.start_game()
    assert s.state == "finished"
