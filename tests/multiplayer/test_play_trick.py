"""Tests for the multi-seat ``_play_trick`` (Task 12).

Per the ``schieber-protocol`` skill (multi-seat shapes):

  - ``play_request`` is sent ONLY to the seat whose turn it is, carrying
    ``trick_so_far`` (cumulative), ``lead_suit`` and ``valid_cards``.
  - ``play_pending`` is broadcast to the OTHER seats + spectators with
    ``by_position`` and the same ``trick_so_far`` snapshot.
  - ``card_played`` is broadcast (final) to everyone with
    ``by_position`` and ``card`` (CSS code).
  - ``trick_end`` is broadcast with
    ``{winner_position, winner_team, points}`` ONLY — no running totals.
  - Each seat's hand is private; valid-cards lists must reflect each
    seat's OWN hand at prompt time.

Validation invariants mirror the trump / weis phases: malformed messages
trigger an ``error`` reply followed by a fresh ``play_request`` for the
SAME seat (per-seat re-prompt), and only a valid ``play_card`` proceeds.
"""

import pytest

from Cards_refactored import Play
from ausbau.game_session import (
    GameSession,
    OW_PLAYERS,
    PLAYERS,
    SN_PLAYERS,
    card_to_code,
    get_valid_cards,
)
from ausbau.room import Spectator, Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket, seat_4_humans


pytestmark = pytest.mark.asyncio


def _fresh_session():
    g = Guest(guest_id='a' * 32)
    return GameSession(
        code="A",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
    )


def _queue_seat_plays_first_valid(s, play, seat_order):
    """Queue one ``play_card`` per seat in turn order, picking the
    first card from each seat's valid-cards list at prompt time.

    Because lead-suit / play.operator are known up front and hands are
    fixed before the trick starts, we can compute what the SECOND seat
    will see by simulating the first seat's choice ourselves. To keep
    the test simple we do NOT simulate: each seat just queues its own
    first valid card (which the server then validates against the live
    game state).

    The first seat sees ``lead_suit=None`` so all their cards are valid;
    the second/third/fourth seats see whatever lead-suit emerges. We
    pre-compute valid cards for each seat in the order the trick will
    visit them, simulating each play.
    """
    chosen: list[tuple[str, str]] = []
    lead_suit = None
    # work on copies so we don't mutate play.* hands
    hands = {pos: {suit: list(getattr(play, pos)[suit]) for suit in getattr(play, pos)}
             for pos in PLAYERS}
    player = seat_order[0]
    for i in range(4):
        valid = get_valid_cards(hands[player], lead_suit, play.operator)
        assert valid, f"{player} has no valid cards"
        code = valid[0]
        # Find that card in the simulated hand and remove it.
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
        chosen.append((player, code))
        s._seat(player).incoming.put_nowait({"type": "play_card", "card": code})
        player = play.folger[player]
    return chosen


async def test_play_trick_4_humans_one_round():
    """End-to-end: 4 humans each queue a valid card; trick resolves cleanly."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"  # Spiel 1 default lead

    seat_order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        seat_order.append(nxt)
        nxt = play.folger[nxt]

    chosen = _queue_seat_plays_first_valid(s, play, seat_order)

    score_before = s.point_sn + s.point_ow
    winner, pts = await s._play_trick(play)

    # Each seat's `play_request` carried THEIR own valid_cards.
    for pos in seat_order:
        reqs = wss[pos].all_sent_of_type("play_request")
        assert len(reqs) == 1, (
            f"{pos} expected exactly 1 play_request, got {len(reqs)}: {reqs}"
        )

    # Other 3 seats received play_pending (one per seat's turn excluding self).
    for pos in seat_order:
        pending = wss[pos].all_sent_of_type("play_pending")
        assert len(pending) == 3, (
            f"{pos} expected 3 play_pending events, got {len(pending)}: {pending}"
        )

    # All 4 seats received the 4 card_played broadcasts and 1 trick_end.
    for pos in seat_order:
        played = wss[pos].all_sent_of_type("card_played")
        assert len(played) == 4, (
            f"{pos} expected 4 card_played, got {len(played)}: {played}"
        )
        end_msgs = wss[pos].all_sent_of_type("trick_end")
        assert len(end_msgs) == 1, (
            f"{pos} expected 1 trick_end, got {len(end_msgs)}: {end_msgs}"
        )

    # trick_end shape contract.
    end = wss[seat_order[0]].last_sent_of_type("trick_end")
    assert end["type"] == "trick_end"
    assert end["winner_position"] in {"compo", "compn", "compe", "comps"}
    assert end["winner_position"] == winner
    assert isinstance(end["points"], int)
    assert end["points"] == pts
    if winner in SN_PLAYERS:
        assert end["winner_team"] == "sn"
    else:
        assert end["winner_team"] == "ow"

    # Score moved by exactly `pts`.
    assert (s.point_sn + s.point_ow) - score_before == pts

    # Cards played by each seat (in order) matches what we queued.
    all_played = wss[seat_order[0]].all_sent_of_type("card_played")
    for i, msg in enumerate(all_played):
        exp_pos, exp_card = chosen[i]
        assert msg["by_position"] == exp_pos, (
            f"play #{i}: expected by_position={exp_pos}, got {msg}"
        )
        assert msg["card"] == exp_card, (
            f"play #{i}: expected card={exp_card}, got {msg}"
        )


async def test_play_trick_invalid_card_re_prompts():
    """Human sends a bogus card code, then a valid one. Server sends
    `error` + re-prompt + then proceeds normally."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    # First seat queues garbage then valid; remaining three queue valid.
    seat_order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        seat_order.append(nxt)
        nxt = play.folger[nxt]

    # Pre-queue garbage for the lead seat BEFORE the valid play, then
    # valid play, then valid plays for the other three seats.
    lead = seat_order[0]
    s._seat(lead).incoming.put_nowait(
        {"type": "play_card", "card": "ZZZ-not-a-card"}
    )
    # Now compute and queue valids (including for the lead's second try).
    _queue_seat_plays_first_valid(s, play, seat_order)

    await s._play_trick(play)

    errors = wss[lead].all_sent_of_type("error")
    assert errors, f"expected at least one error on {lead}, got: {wss[lead].sent}"
    assert any("ZZZ" in e.get("message", "") or "Ungültig" in e.get("message", "")
               for e in errors), errors

    # The lead got at least 2 play_request messages: initial + re-prompt.
    reqs = wss[lead].all_sent_of_type("play_request")
    assert len(reqs) >= 2, (
        f"expected >=2 play_request on {lead}, got {len(reqs)}: {reqs}"
    )


async def test_play_trick_wrong_type_re_prompts():
    """Human sends `{type: announce_weis}` first, then valid play_card.
    Server sends `error` + re-prompt + then proceeds normally."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    seat_order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        seat_order.append(nxt)
        nxt = play.folger[nxt]

    lead = seat_order[0]
    # Wrong type first; then the normal queue drives the trick.
    s._seat(lead).incoming.put_nowait({"type": "announce_weis", "announce": False})
    _queue_seat_plays_first_valid(s, play, seat_order)

    await s._play_trick(play)

    errors = wss[lead].all_sent_of_type("error")
    assert errors, f"expected error on {lead}, got: {wss[lead].sent}"
    assert any("play_card" in e.get("message", "") for e in errors), errors

    reqs = wss[lead].all_sent_of_type("play_request")
    assert len(reqs) >= 2, (
        f"expected >=2 play_request on {lead}, got {len(reqs)}: {reqs}"
    )


async def test_play_trick_pending_carries_trick_so_far():
    """Each `play_pending` includes the cumulative `trick_so_far` list as
    of the moment that prompt was issued. After N plays so far, the next
    seat's prompt (and the broadcast pending) carries N entries."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    seat_order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        seat_order.append(nxt)
        nxt = play.folger[nxt]

    _queue_seat_plays_first_valid(s, play, seat_order)
    await s._play_trick(play)

    # For each non-lead seat, find their `play_request` and assert the
    # `trick_so_far` length matches their position in `seat_order`
    # (seat at index `i` should see exactly `i` plays so far).
    for i, pos in enumerate(seat_order):
        req = wss[pos].last_sent_of_type("play_request")
        assert req is not None, f"{pos} did not receive play_request"
        assert len(req["trick_so_far"]) == i, (
            f"{pos} (index {i}) play_request.trick_so_far has "
            f"{len(req['trick_so_far'])} entries, expected {i}: {req}"
        )

    # Same property on play_pending broadcast — for each broadcast the
    # active seat's index in seat_order = len(trick_so_far).
    # We collect pending events from the lead's stream (lead is included
    # in 3 of the 4 broadcasts as a non-active seat).
    lead = seat_order[0]
    pending = wss[lead].all_sent_of_type("play_pending")
    # Lead is the active seat on round 0 → no pending broadcast goes to
    # the lead during their own turn. So lead receives pendings for
    # rounds 1, 2, 3 → 3 events with trick_so_far lengths 1, 2, 3.
    assert len(pending) == 3
    for i, msg in enumerate(pending, start=1):
        assert len(msg["trick_so_far"]) == i, msg


async def test_play_trick_request_only_to_active_seat():
    """`play_request` is sent ONLY to the active seat. Spectators NEVER
    receive `play_request`. Other seats receive `play_pending` only."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    spec_ws = FakeWebSocket()
    s.spectators.append(Spectator(
        principal=Guest(guest_id="z" * 32),
        websocket=spec_ws,
    ))

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    seat_order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        seat_order.append(nxt)
        nxt = play.folger[nxt]

    _queue_seat_plays_first_valid(s, play, seat_order)
    await s._play_trick(play)

    assert spec_ws.last_sent_of_type("play_request") is None, (
        f"spectator must NOT receive play_request: {spec_ws.sent}"
    )
    pending = spec_ws.all_sent_of_type("play_pending")
    assert len(pending) == 4, (
        f"spectator expected 4 play_pending events, got {len(pending)}: {pending}"
    )
    # Spectator also sees all card_played + trick_end broadcasts.
    assert len(spec_ws.all_sent_of_type("card_played")) == 4
    assert len(spec_ws.all_sent_of_type("trick_end")) == 1


async def test_play_trick_updates_current_seat_turn_per_iteration():
    """Mid-trick state tracking: `_current_seat_turn` and
    `_current_trick_so_far` must be updated at the top of EACH iteration
    of the 4-play loop, not just once before the call.

    Without this, a reconnect mid-trick would see a stale
    ``current_seat_turn`` and the wrong ``trick_so_far`` snapshot via
    ``room_resume`` — so the reclaiming client thinks it's still the
    lead's turn / nothing has been played yet.

    We hook into ``send_to_seat`` to snapshot the live attributes at the
    moment each ``play_request`` is dispatched.
    """
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    seat_order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        seat_order.append(nxt)
        nxt = play.folger[nxt]

    snapshots: list[dict] = []
    original_send = s.send_to_seat

    async def spy_send(position, msg):
        if isinstance(msg, dict) and msg.get("type") == "play_request":
            snapshots.append({
                "position": position,
                "current_seat_turn": s._current_seat_turn,
                "trick_so_far_len": len(s._current_trick_so_far),
            })
        await original_send(position, msg)

    s.send_to_seat = spy_send

    _queue_seat_plays_first_valid(s, play, seat_order)
    await s._play_trick(play)

    # One snapshot per seat in turn order, each showing the active seat
    # as `_current_seat_turn` and an increasing `trick_so_far` length.
    assert len(snapshots) == 4, snapshots
    for i, (snap, expected_pos) in enumerate(zip(snapshots, seat_order)):
        assert snap["position"] == expected_pos, (i, snap)
        assert snap["current_seat_turn"] == expected_pos, (i, snap)
        assert snap["trick_so_far_len"] == i, (i, snap)
