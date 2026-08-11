---
type: Python Module
title: test_await_seat_action
resource: tests/multiplayer/test_await_seat_action.py#L1-L250
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/pytest
  - external/ausbau-ai-strategies
  - external/ausbau-game-session
  - external/ausbau-room
  - external/frontend-auth-guest
  - external/tests-multiplayer-conftest
  - external/cards-refactored
---

# Contains

- [_fresh_session](../../../functions/tests/multiplayer/test_await_seat_action/_fresh_session.md)
- [test_await_human_returns_queued_message](../../../functions/tests/multiplayer/test_await_seat_action/test_await_human_returns_queued_message.md)
- [test_await_ai_computes_synchronously_no_queue_touched](../../../functions/tests/multiplayer/test_await_seat_action/test_await_ai_computes_synchronously_no_queue_touched.md)
- [test_await_disconnected_seat_blocks_until_event_set](../../../functions/tests/multiplayer/test_await_seat_action/test_await_disconnected_seat_blocks_until_event_set.md)
- [test_compute_ai_trump_uses_farbe_lang](../../../functions/tests/multiplayer/test_await_seat_action/test_compute_ai_trump_uses_farbe_lang.md)
- [fake_farbe_lang](../../../functions/tests/multiplayer/test_await_seat_action/fake_farbe_lang.md)
- [test_compute_ai_play_uses_ai_select_card](../../../functions/tests/multiplayer/test_await_seat_action/test_compute_ai_play_uses_ai_select_card.md)
- [fake_ai_select_card](../../../functions/tests/multiplayer/test_await_seat_action/fake_ai_select_card.md)

# Imports

- `asyncio`
- `pytest`
- `ausbau.ai_strategies`
- `ausbau.game_session`
- `ausbau.room`
- `frontend.auth.guest`
- `tests.multiplayer.conftest`
- `Cards_refactored`