"""Tests for the replay buffer (Task 16, spec §5.2.8).

The replay buffer is ``GameSession._completed_tricks`` — the most recent
``REPLAY_BUFFER_TRICK_COUNT`` (=3) completed tricks, each as a redacted
snapshot ready for ``room_resume.missed_tricks``.

Each entry shape (per spec example):
    {
        "by": ["compo:E7", "compn:R6", "compe:RA", "comps:E9"],
        "winner_position": "compe",
        "points": 18,
    }

The buffer is appended to at the end of ``_play_trick`` (multi-seat only;
the legacy single-WS path does NOT touch it). It is capped to the last
N entries — older tricks are dropped from the front.
"""

import pytest

from Cards_refactored import Play
from ausbau.game_session import (
    GameSession,
    PLAYERS,
    card_to_code,
    get_valid_cards,
)
from ausbau.room import REPLAY_BUFFER_TRICK_COUNT, Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import seat_4_humans


pytestmark = pytest.mark.asyncio


def _fresh_session():
    g = Guest(guest_id='a' * 32)
    return GameSession(
        code="A",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
    )


def _seat_order(play):
    order = [play.first]
    nxt = play.folger[play.first]
    while nxt != play.first:
        order.append(nxt)
        nxt = play.folger[nxt]
    return order


def _queue_first_valid_for_trick(s, play):
    """Queue one ``play_card`` per seat for the upcoming trick.

    Each seat plays the FIRST card from its valid-cards list at the moment
    its prompt is computed — we simulate the state changes ourselves so
    follow-suit constraints come out right. Returns the chosen
    ``[(position, code), ...]`` list in trick order.
    """
    chosen: list[tuple[str, str]] = []
    lead_suit = None
    # Operate on shallow per-suit copies so simulation does not mutate hands.
    hands = {pos: {suit: list(getattr(play, pos)[suit])
                   for suit in getattr(play, pos)}
             for pos in PLAYERS}
    player = play.first
    for i in range(4):
        valid = get_valid_cards(hands[player], lead_suit, play.operator)
        assert valid, f"{player} has no valid cards"
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
        chosen.append((player, code))
        s._seat(player).incoming.put_nowait(
            {"type": "play_card", "card": code}
        )
        player = play.folger[player]
    return chosen


async def test_replay_buffer_appends_one_trick():
    """One trick → one entry with the spec-mandated shape."""
    s = _fresh_session()
    seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    assert s._completed_tricks == []

    chosen = _queue_first_valid_for_trick(s, play)
    winner, pts = await s._play_trick(play)

    assert len(s._completed_tricks) == 1
    entry = s._completed_tricks[0]

    # Shape check.
    assert set(entry.keys()) == {"by", "winner_position", "points"}
    assert isinstance(entry["by"], list)
    assert len(entry["by"]) == 4
    # `by` matches what we queued, in trick order, "position:CODE" form.
    expected_by = [f"{pos}:{code}" for pos, code in chosen]
    assert entry["by"] == expected_by
    # winner / points are the values returned by _play_trick.
    assert entry["winner_position"] == winner
    assert entry["points"] == pts


async def test_replay_buffer_caps_at_three():
    """Run 5 tricks → buffer holds only the last 3 (oldest dropped)."""
    s = _fresh_session()
    seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    all_winners: list[str] = []
    for _ in range(5):
        _queue_first_valid_for_trick(s, play)
        winner, _pts = await s._play_trick(play)
        all_winners.append(winner)
        # Trick winner leads next (matches `_run_spiel` semantics).
        play.first = winner

    assert len(s._completed_tricks) == REPLAY_BUFFER_TRICK_COUNT == 3
    # The buffer holds the LAST 3 winners — tricks 3, 4, 5 (zero-indexed 2..4).
    buffered_winners = [e["winner_position"] for e in s._completed_tricks]
    assert buffered_winners == all_winners[-REPLAY_BUFFER_TRICK_COUNT:]


async def test_replay_entry_carries_winner_and_points_matching_trick_end():
    """Replay entry's ``winner_position`` and ``points`` agree with the
    ``trick_end`` broadcast that immediately preceded it."""
    s = _fresh_session()
    wss = seat_4_humans(s)

    play = Play(spiel=1)
    play.operator = "Eicheln"
    play.first = "compo"

    _queue_first_valid_for_trick(s, play)
    await s._play_trick(play)

    end = wss[play.first].last_sent_of_type("trick_end")
    assert end is not None
    entry = s._completed_tricks[-1]
    assert entry["winner_position"] == end["winner_position"]
    assert entry["points"] == end["points"]
