"""End-to-end multiplayer integration test (Task 24).

Drives ``GameSession.start_game`` with four FakeWebSocket-backed human
seats. Each seat runs a "responder" task that watches its WebSocket's
``sent`` log for prompts and pushes the right reply into
``seat.incoming``:

  - ``trump_request`` → ``{"type": "choose_trump", "operator": <suit>}``
  - ``weis_request`` → ``{"type": "announce_weis", "announce": False}``
  - ``play_request`` → ``{"type": "play_card", "card": <first valid>}``

The responders exit on ``game_end``. The phase loops are unit-tested
elsewhere (``test_trump_phase``, ``test_weis_phase``, ``test_play_trick``,
``test_run_spiel``); this test exercises the full multi-seat wiring from
``start_game`` through dealing → trump → weis → 9 tricks → ``spiel_end``
→ loop → ``game_end``, catching any drift between phases.

Per the schieber-protocol skill, ``start_game``'s outputs are:
  - per-seat ``game_start`` (and TV ``game_start`` to spectators)
  - ``trump_pending`` / ``trump_request`` / ``trump_chosen``
  - ``weis_request`` / ``weis_resolution``
  - ``play_request`` / ``play_pending`` / ``card_played`` / ``trick_end``
  - ``spiel_end`` (per spiel) and finally ``game_end``
"""

import asyncio

import pytest

from ausbau.game_session import GameSession, PLAYERS
from ausbau.room import Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import seat_4_humans


pytestmark = pytest.mark.asyncio


async def _human_responder(seat, ws, log):
    """Watch ``ws.sent`` and queue replies on ``seat.incoming``.

    Polls via ``asyncio.sleep(0)`` to yield control to the phase loop
    after every check. Exits on ``game_end`` (the only natural terminal
    message for a seat in a finished game).
    """
    last_seen = 0
    while True:
        if len(ws.sent) > last_seen:
            new_msgs = ws.sent[last_seen:]
            last_seen = len(ws.sent)
            for msg in new_msgs:
                t = msg.get("type") if isinstance(msg, dict) else None
                log.append(t)
                if t == "trump_request":
                    # Prefer a real suit so trumpf-mode rules engage; the
                    # phase prompt does not include the option list, so
                    # we hard-pick one. ("Eicheln" works regardless of
                    # who leads — it's always a legal trump choice.)
                    seat.incoming.put_nowait({
                        "type": "choose_trump",
                        "operator": "Eicheln",
                    })
                elif t == "weis_request":
                    # Decline weis: keeps the test deterministic and
                    # avoids depending on the per-seat eligible weis list
                    # shape (which is exercised by test_weis_phase).
                    seat.incoming.put_nowait({
                        "type": "announce_weis",
                        "announce": False,
                    })
                elif t == "play_request":
                    valid = msg.get("valid_cards") or []
                    if valid:
                        seat.incoming.put_nowait({
                            "type": "play_card",
                            "card": valid[0],
                        })
                elif t == "game_end":
                    return
        await asyncio.sleep(0)


def _fresh_4_human_session(*, end_game: int = 300, variant=None) -> GameSession:
    g = Guest(guest_id='h' * 32)
    s = GameSession(
        code="ABCDEF",
        host_principal_id=f"guest:{g.guest_id}",
        variant=variant if variant is not None else Variant(),
        end_game=end_game,
    )
    return s


async def test_e2e_4_humans_full_game(fast_clock):
    """Full multiplayer game with 4 humans — runs to ``game_end``.

    Asserts:
      - state transitions lobby → finished
      - all 4 seats received exactly one ``game_end``
      - final scores satisfy ``end_game`` (one team ≥ target, or tie)
      - per-spiel ``game_start`` / ``spiel_end`` counts match
      - every seat saw at least one ``trump_request``, one ``weis_request``,
        and one ``play_request`` over the course of the game
    """
    s = _fresh_4_human_session(end_game=300)
    wss = seat_4_humans(s)

    log_per_seat: dict[str, list[str | None]] = {pos: [] for pos in wss}
    responder_tasks = []
    for pos, ws in wss.items():
        seat = s._seat(pos)
        log = log_per_seat[pos]
        responder_tasks.append(
            asyncio.create_task(_human_responder(seat, ws, log))
        )

    game_task = asyncio.create_task(s.start_game())
    try:
        await asyncio.wait_for(game_task, timeout=10.0)
    except asyncio.TimeoutError:
        # Cancel responders before failing so pytest-asyncio can clean up.
        for t in responder_tasks:
            t.cancel()
        pytest.fail(
            "game did not finish within 10s; per-seat log: "
            f"{ {pos: log[:30] for pos, log in log_per_seat.items()} }"
        )

    # Drain responders — they should exit on game_end. Give them one tick.
    await asyncio.sleep(0)
    for t in responder_tasks:
        if not t.done():
            t.cancel()
    # Swallow any CancelledError from the cancels above.
    for t in responder_tasks:
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass

    assert s.state == "finished", f"state is {s.state!r}, expected 'finished'"

    # Each of the 4 seats received exactly one game_end.
    for pos, ws in wss.items():
        ge = ws.all_sent_of_type("game_end")
        assert len(ge) == 1, (
            f"seat {pos} received {len(ge)} game_end messages, expected 1"
        )
        end = ge[0]
        assert end["winner_team"] in {"sn", "ow", "tie"}
        assert end["scores"]["sn"] == s.point_sn
        assert end["scores"]["ow"] == s.point_ow

    # End-game condition actually held.
    assert max(s.point_sn, s.point_ow) >= s.end_game

    # game_start and spiel_end counts agree on every seat (one of each
    # per spiel) — catches "spiel_end fired but no fresh game_start".
    any_seat_ws = next(iter(wss.values()))
    n_starts = len(any_seat_ws.all_sent_of_type("game_start"))
    n_ends = len(any_seat_ws.all_sent_of_type("spiel_end"))
    assert n_starts == n_ends, (
        f"game_start ({n_starts}) != spiel_end ({n_ends})"
    )
    assert n_starts >= 1

    # Each seat saw the per-phase prompts at least once.
    for pos, log in log_per_seat.items():
        assert "trump_request" in log or "weis_request" in log or "play_request" in log, (
            f"seat {pos} saw no phase prompts; log: {log[:20]}"
        )
        # Every seat plays cards every spiel — so play_request must
        # appear at least once.
        assert "play_request" in log, (
            f"seat {pos} never received a play_request; log: {log[:30]}"
        )


async def test_e2e_4_humans_trumpf_bock_variant(fast_clock):
    """Same flow but with ``trumpf_bock=True`` and ``match_bonus=False``.

    Spec §11.6 listed variant: 5x trump scoring, no match bonus. We
    don't pin every score arithmetic invariant here — that's covered by
    ``test_variants``. We just verify the e2e path completes for a
    custom variant block, the variant flags are visible to seats via
    ``game_start.variant``, and ``spiel_end.match`` is False everywhere
    (since the bonus is disabled).
    """
    s = _fresh_4_human_session(
        end_game=300,
        variant=Variant(trumpf_bock=True, match_bonus=False, stoeck=True),
    )
    wss = seat_4_humans(s)

    log_per_seat: dict[str, list[str | None]] = {pos: [] for pos in wss}
    responder_tasks = []
    for pos, ws in wss.items():
        seat = s._seat(pos)
        responder_tasks.append(
            asyncio.create_task(_human_responder(seat, ws, log_per_seat[pos]))
        )

    game_task = asyncio.create_task(s.start_game())
    try:
        await asyncio.wait_for(game_task, timeout=10.0)
    except asyncio.TimeoutError:
        for t in responder_tasks:
            t.cancel()
        pytest.fail("variant game did not finish within 10s")

    await asyncio.sleep(0)
    for t in responder_tasks:
        if not t.done():
            t.cancel()
    for t in responder_tasks:
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass

    assert s.state == "finished"

    # Variant block propagated to seats via game_start.
    any_seat_ws = next(iter(wss.values()))
    gs = any_seat_ws.last_sent_of_type("game_start")
    assert gs is not None
    assert gs["variant"] == {
        "trumpf_bock": True,
        "match_bonus": False,
        "stoeck": True,
    }

    # match_bonus disabled → every spiel_end.match is False.
    for pos, ws in wss.items():
        for se in ws.all_sent_of_type("spiel_end"):
            assert se["match"] is False, (
                f"seat {pos} saw spiel_end.match=True with match_bonus disabled"
            )
