"""Tests for the real ``_await_seat_action`` and ``_compute_ai_action`` (Task 13).

The contract:

  - Connected human seat: dequeue ONE message from ``seat.incoming`` and
    return it. The phase loop owns validation and may re-prompt.
  - AI seat: compute a synchronous action via ``_compute_ai_action``,
    which delegates to ``seat._strategy``. Never touches ``seat.incoming``.
  - Disconnected human seat (``websocket is None``, ``is_ai is False``):
    block on ``seat.state_event`` until a reclaim or AI-takeover (Task 14)
    flips the state. Then re-evaluate.

  - ``_compute_ai_action`` for ``valid_actions["type"] == "trump"`` calls
    ``seat._strategy.pick_trump(play, schieben_allowed)``. ``MediumStrategy``
    in turn uses ``utils.card_utils.farbe_lang`` against the seat's hand
    on the live ``Play`` object.
  - ``_compute_ai_action`` for ``valid_actions["type"] == "play_card"``
    calls ``seat._strategy.pick_card(play, lead_suit, trick_so_far)``.
    ``MediumStrategy`` in turn uses module-level
    ``ai_select_card(hand, lead_suit, operator)``.
"""

import asyncio

import pytest

from ausbau.ai_strategies import MediumStrategy
from ausbau.game_session import GameSession
from ausbau.room import Variant
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket


pytestmark = pytest.mark.asyncio


def _fresh_session():
    g = Guest(guest_id='a' * 32)
    return GameSession(
        code="A",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
    )


async def test_await_human_returns_queued_message():
    """A connected human seat: queued message is dequeued and returned."""
    s = _fresh_session()
    seat = s._seat("compo")
    seat.is_ai = False
    seat.principal = Guest(guest_id='b' * 32)
    seat.websocket = FakeWebSocket()

    expected = {"type": "choose_trump", "operator": "Schilten"}
    seat.incoming.put_nowait(expected)

    got = await asyncio.wait_for(
        s._await_seat_action("compo", valid_actions={"type": "trump"}),
        timeout=0.1,
    )
    assert got == expected


async def test_await_ai_computes_synchronously_no_queue_touched():
    """AI seat: returns a computed action without dequeuing."""
    from Cards_refactored import Play

    s = _fresh_session()
    seat = s._seat("compo")
    # Default seats start as is_ai=True with no principal/ws — that's fine.
    assert seat.is_ai is True
    # Bare GameSession() doesn't auto-attach strategies (only `create_room`
    # does for seats 1-3); the defensive rebuild in `_compute_ai_action`
    # will fill it in. Pre-attach explicitly so this test is independent
    # of that fallback behavior.
    seat._strategy = MediumStrategy(seat.position)

    # Strategy needs a live Play to read its own hand from.
    s.current_play = Play(spiel=1)
    s.current_play.operator = "Eicheln"

    # Put a sentinel message into the queue. If the code path mistakenly
    # reads it, the test will leak it via remaining qsize; we assert
    # the sentinel is still queued after the call.
    sentinel = {"type": "should_not_be_consumed"}
    seat.incoming.put_nowait(sentinel)

    got = await asyncio.wait_for(
        s._await_seat_action(
            "compo",
            valid_actions={
                "type": "play_card",
                "valid_cards": ["EA", "RB"],
                "lead_suit": None,
                "operator": "Eicheln",
                "trick_so_far": [],
            },
        ),
        timeout=0.1,
    )

    # Action shape from AI must be a dict with a `type`.
    assert isinstance(got, dict)
    assert got.get("type") in {"play_card", "noop"}
    # Queue still has the sentinel; AI path must not touch it.
    assert seat.incoming.qsize() == 1


async def test_await_disconnected_seat_blocks_until_event_set():
    """A human seat with websocket=None must NOT return until state_event
    is set. Simulating an AI-takeover (Task 14) by flipping is_ai=True
    and setting the event releases the await."""
    from Cards_refactored import Play

    s = _fresh_session()
    seat = s._seat("compo")
    seat.is_ai = False
    seat.principal = Guest(guest_id='b' * 32)
    seat.websocket = None  # disconnected

    # When the takeover wakes the await, `_compute_ai_action` will run on
    # this seat — it needs a strategy and a live Play to read its hand.
    s.current_play = Play(spiel=1)
    s.current_play.operator = "Eicheln"

    task = asyncio.create_task(
        s._await_seat_action(
            "compo",
            valid_actions={
                "type": "play_card",
                "valid_cards": ["EA"],
                "lead_suit": None,
                "operator": "Eicheln",
                "trick_so_far": [],
            },
        )
    )

    # The task must NOT complete while the seat is disconnected.
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(asyncio.shield(task), timeout=0.05)
    assert not task.done()

    # Simulate AI-takeover (Task 14): seat becomes AI, strategy attached,
    # state_event set. Strategy must exist BEFORE the event fires so the
    # awaiter sees a fully-formed AI seat the moment it wakes.
    seat._strategy = MediumStrategy(seat.position)
    seat.is_ai = True
    seat.state_event.set()

    got = await asyncio.wait_for(task, timeout=0.2)
    assert isinstance(got, dict)
    assert got.get("type") in {"play_card", "noop"}


async def test_compute_ai_trump_uses_farbe_lang(monkeypatch):
    """When ``valid_actions["type"] == "trump"`` MediumStrategy.pick_trump
    delegates to ``utils.card_utils.farbe_lang`` against its own hand on
    the live ``Play``. ``_compute_ai_action`` returns the resulting
    ``choose_trump``."""
    from Cards_refactored import Play

    s = _fresh_session()
    seat = s._seat("compo")
    seat._strategy = MediumStrategy(seat.position)

    # Strategy reads its hand off the live play via getattr(play, position).
    play = Play(spiel=1)
    s.current_play = play
    sentinel_hand = play.compo

    captured = {}

    def fake_farbe_lang(hand):
        captured["hand"] = hand
        return "Schilten"

    # `MediumStrategy.pick_trump` does `from utils.card_utils import farbe_lang`
    # at call time, so monkeypatching the symbol on the module rebinds for
    # subsequent imports.
    monkeypatch.setattr("utils.card_utils.farbe_lang", fake_farbe_lang)

    out = s._compute_ai_action(
        seat,
        valid_actions={
            "type": "trump",
            "options": ["Eicheln", "Rosen", "Schellen", "Schilten", "Oben", "Unten"],
            "schieben_allowed": True,
        },
    )

    assert out == {"type": "choose_trump", "operator": "Schilten"}
    assert captured["hand"] is sentinel_hand


async def test_compute_ai_play_uses_ai_select_card(monkeypatch):
    """When ``valid_actions["type"] == "play_card"`` MediumStrategy.pick_card
    delegates to ``ausbau.game_session.ai_select_card`` against its own
    hand and the live ``Play.operator``. ``_compute_ai_action`` returns
    the resulting ``play_card`` with the chosen card's code."""
    from Cards_refactored import Play

    s = _fresh_session()
    seat = s._seat("compo")
    seat._strategy = MediumStrategy(seat.position)

    # Strategy reads its hand off the live play and uses play.operator.
    play = Play(spiel=1)
    play.operator = "Eicheln"
    s.current_play = play

    # pull any card from compo's Eicheln (or fallback to first non-empty).
    chosen_card = None
    for suit in ("Eicheln", "Rosen", "Schellen", "Schilten"):
        if play.compo[suit]:
            chosen_card = play.compo[suit][0]
            break
    assert chosen_card is not None

    captured = {}

    def fake_ai_select_card(hand, lead_suit, operator, trick_so_far=None):
        captured["hand"] = hand
        captured["lead_suit"] = lead_suit
        captured["operator"] = operator
        captured["trick_so_far"] = trick_so_far
        return chosen_card

    # `MediumStrategy.pick_card` does `from ausbau.game_session import
    # ai_select_card, card_to_code` at call time, so monkeypatching the
    # module-level symbol rebinds for the lazy import.
    monkeypatch.setattr("ausbau.game_session.ai_select_card", fake_ai_select_card)

    out = s._compute_ai_action(
        seat,
        valid_actions={
            "type": "play_card",
            "lead_suit": "Rosen",
            "operator": "Eicheln",
            "valid_cards": [],
            "trick_so_far": [],
        },
    )

    from ausbau.game_session import card_to_code
    assert out == {"type": "play_card", "card": card_to_code(chosen_card)}
    assert captured["hand"] is play.compo
    assert captured["lead_suit"] == "Rosen"
    assert captured["operator"] == "Eicheln"
    assert captured["trick_so_far"] == []   # forwarded from valid_actions
