---
type: Python Module
title: test_disconnect
resource: tests/multiplayer/test_disconnect.py#L1-L302
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/pytest
  - external/ausbau-game-session
  - external/ausbau-room
  - external/frontend-auth-guest
  - external/tests-multiplayer-conftest
---

# Contains

- [_fresh_session](../../../functions/tests/multiplayer/test_disconnect/_fresh_session.md)
- [test_disconnect_in_lobby_drops_to_ai_immediately](../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately.md)
- [test_disconnect_in_lobby_host_triggers_transfer](../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_host_triggers_transfer.md)
- [test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused](../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused.md)
- [test_disconnect_idempotent_for_ai_or_already_disconnected](../../../functions/tests/multiplayer/test_disconnect/test_disconnect_idempotent_for_ai_or_already_disconnected.md)
- [test_reconnect_timeout_flips_to_ai](../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai.md)
- [test_reconnect_timeout_no_op_if_websocket_returned](../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned.md)
- [test_disconnect_mid_game_host_triggers_transfer_after_timeout](../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout.md)
- [test_disconnect_state_event_set_wakes_awaiter](../../../functions/tests/multiplayer/test_disconnect/test_disconnect_state_event_set_wakes_awaiter.md)

# Imports

- `asyncio`
- `pytest`
- `ausbau.game_session`
- `ausbau.room`
- `frontend.auth.guest`
- `tests.multiplayer.conftest`