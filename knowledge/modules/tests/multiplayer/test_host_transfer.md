---
type: Python Module
title: test_host_transfer
resource: tests/multiplayer/test_host_transfer.py#L1-L383
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/pytest
  - external/pytest-asyncio
  - external/httpx
  - external/ausbau-game-session
  - external/ausbau-room
  - external/frontend-auth-guest
  - external/tests-multiplayer-conftest
  - external/ausbau-server
  - external/time
---

# Contains

- [_fresh_session](../../../functions/tests/multiplayer/test_host_transfer/_fresh_session.md)
- [test_transfer_host_no_op_when_no_connected_humans](../../../functions/tests/multiplayer/test_host_transfer/test_transfer_host_no_op_when_no_connected_humans.md)
- [test_reclaim_into_hostless_room_promotes_reconnecting_human](../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human.md)
- [test_reclaim_into_room_with_connected_host_does_not_promote](../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_room_with_connected_host_does_not_promote.md)
- [client](../../../functions/tests/multiplayer/test_host_transfer/client.md)
- [client_other](../../../functions/tests/multiplayer/test_host_transfer/client_other.md)
- [test_host_leave_in_lobby_transfers_host](../../../functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_transfers_host.md)
- [test_host_leave_in_lobby_no_other_humans_no_transfer](../../../functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_no_other_humans_no_transfer.md)
- [test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target](../../../functions/tests/multiplayer/test_host_transfer/test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target.md)
- [test_kick_not_host_returns_403](../../../functions/tests/multiplayer/test_host_transfer/test_kick_not_host_returns_403.md)
- [test_kick_mid_game_returns_400](../../../functions/tests/multiplayer/test_host_transfer/test_kick_mid_game_returns_400.md)
- [test_kick_self_treated_as_leave_transfers_host](../../../functions/tests/multiplayer/test_host_transfer/test_kick_self_treated_as_leave_transfers_host.md)
- [test_kick_invalid_target_position_returns_422](../../../functions/tests/multiplayer/test_host_transfer/test_kick_invalid_target_position_returns_422.md)
- [test_kick_target_already_ai_is_idempotent](../../../functions/tests/multiplayer/test_host_transfer/test_kick_target_already_ai_is_idempotent.md)

# Imports

- `asyncio`
- `pytest`
- `pytest_asyncio`
- `httpx`
- `ausbau.game_session`
- `ausbau.room`
- `frontend.auth.guest`
- `tests.multiplayer.conftest`
- `ausbau.server`
- `time`