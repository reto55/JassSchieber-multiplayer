"""Tests for the real ``_await_seat_action`` and ``_compute_ai_action`` (Task 13).

The contract:

  - Connected human seat: dequeue ONE message from ``seat.incoming`` and
    return it. The phase loop owns validation and may re-prompt.
  - AI seat: compute a synchronous action via ``_compute_ai_action``.
    Never touches ``seat.incoming``.
  - Disconnected human seat (``websocket is None``, ``is_ai is False``):
    block on ``seat.state_event`` until a reclaim or AI-takeover (Task 14)
    flips the state. Then re-evaluate.

  - ``_compute_ai_action`` for ``valid_actions["type"] == "trump"`` uses
    ``utils.card_utils.farbe_lang`` over ``valid_actions["hand"]``.
  - ``_compute_ai_action`` for ``valid_actions["type"] == "play_card"``
    uses module-level ``ai_select_card(hand, lead_suit, operator)``.
"""

import asyncio

import pytest

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
    s = _fresh_session()
    seat = s._seat("compo")
    # Default seats start as is_ai=True with no principal/ws — that's fine.
    assert seat.is_ai is True

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
    s = _fresh_session()
    seat = s._seat("compo")
    seat.is_ai = False
    seat.principal = Guest(guest_id='b' * 32)
    seat.websocket = None  # disconnected

    task = asyncio.create_task(
        s._await_seat_action(
            "compo",
            valid_actions={
                "type": "play_card",
                "valid_cards": ["EA"],
                "lead_suit": None,
                "operator": "Eicheln",
            },
        )
    )

    # The task must NOT complete while the seat is disconnected.
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(asyncio.shield(task), timeout=0.05)
    assert not task.done()

    # Simulate AI-takeover (Task 14): seat becomes AI, state_event set.
    seat.is_ai = True
    seat.state_event.set()

    got = await asyncio.wait_for(task, timeout=0.2)
    assert isinstance(got, dict)
    assert got.get("type") in {"play_card", "noop"}


async def test_compute_ai_trump_uses_farbe_lang(monkeypatch):
    """When ``valid_actions["type"] == "trump"`` and a ``hand`` is given,
    ``_compute_ai_action`` returns ``choose_trump`` with the suit from
    ``farbe_lang``."""
    s = _fresh_session()
    seat = s._seat("compo")

    sentinel_hand = {"Eicheln": [], "Rosen": [], "Schellen": [], "Schilten": []}
    captured = {}

    def fake_farbe_lang(hand):
        captured["hand"] = hand
        return "Schilten"

    # `_compute_ai_action` imports `farbe_lang` lazily — patch where it lives.
    monkeypatch.setattr("utils.card_utils.farbe_lang", fake_farbe_lang)

    out = s._compute_ai_action(
        seat,
        valid_actions={
            "type": "trump",
            "options": ["Eicheln", "Rosen", "Schellen", "Schilten", "Oben", "Unten"],
            "hand": sentinel_hand,
        },
    )

    assert out == {"type": "choose_trump", "operator": "Schilten"}
    assert captured["hand"] is sentinel_hand


async def test_compute_ai_play_uses_ai_select_card(monkeypatch):
    """When ``valid_actions["type"] == "play_card"`` and a ``hand`` is
    given, ``_compute_ai_action`` returns ``play_card`` with the code of
    the card chosen by ``ai_select_card``."""
    s = _fresh_session()
    seat = s._seat("compo")

    # Build a synthetic Card-like with a `suit` and known `card_to_code`-able
    # rank by importing a real Card via Play to avoid mocking too much.
    from Cards_refactored import Play
    play = Play(spiel=1)
    # pull any card from compo's Eicheln (or fallback to first non-empty).
    chosen_card = None
    for suit in ("Eicheln", "Rosen", "Schellen", "Schilten"):
        if play.compo[suit]:
            chosen_card = play.compo[suit][0]
            break
    assert chosen_card is not None

    captured = {}

    def fake_ai_select_card(hand, lead_suit, operator):
        captured["hand"] = hand
        captured["lead_suit"] = lead_suit
        captured["operator"] = operator
        return chosen_card

    monkeypatch.setattr("ausbau.game_session.ai_select_card", fake_ai_select_card)

    out = s._compute_ai_action(
        seat,
        valid_actions={
            "type": "play_card",
            "hand": play.compo,
            "lead_suit": "Rosen",
            "operator": "Eicheln",
            "valid_cards": [],
        },
    )

    from ausbau.game_session import card_to_code
    assert out == {"type": "play_card", "card": card_to_code(chosen_card)}
    assert captured["hand"] is play.compo
    assert captured["lead_suit"] == "Rosen"
    assert captured["operator"] == "Eicheln"
