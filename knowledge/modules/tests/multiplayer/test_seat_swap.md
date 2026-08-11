---
type: Python Module
title: test_seat_swap
resource: tests/multiplayer/test_seat_swap.py#L1-L442
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/pytest
  - external/pytest-asyncio
  - external/httpx
  - external/cards-refactored
  - external/ausbau-game-session
  - external/ausbau-room
  - external/frontend-auth-guest
  - external/tests-multiplayer-conftest
  - external/ausbau-server
---

# Contains

- [_fresh_session](../../../functions/tests/multiplayer/test_seat_swap/_fresh_session.md)
- [test_seat_swap_request_records_and_pushes](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_records_and_pushes.md)
- [test_seat_swap_request_overwrites_prior_from_same_seat](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_overwrites_prior_from_same_seat.md)
- [test_seat_swap_accept_sets_pending_swap](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_accept_sets_pending_swap.md)
- [test_commit_pending_swap_swaps_principals_and_hands](../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands.md)
- [test_commit_pending_swap_noop_when_no_pending](../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_noop_when_no_pending.md)
- [test_commit_aborts_if_either_seat_disconnected_post_accept](../../../functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept.md)
- [test_seat_swap_ttl_fires_seat_swap_expired](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_ttl_fires_seat_swap_expired.md)
- [client](../../../functions/tests/multiplayer/test_seat_swap/client.md)
- [client_other](../../../functions/tests/multiplayer/test_seat_swap/client_other.md)
- [test_seat_swap_endpoint_409_if_state_lobby](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_409_if_state_lobby.md)
- [test_seat_swap_endpoint_403_if_caller_not_seated](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_403_if_caller_not_seated.md)
- [test_seat_swap_endpoint_400_if_target_ai](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_400_if_target_ai.md)
- [test_seat_swap_endpoint_400_if_self](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_400_if_self.md)
- [test_seat_swap_endpoint_happy_request_path](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_request_path.md)
- [test_seat_swap_endpoint_happy_accept_path](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_accept_path.md)
- [test_seat_swap_409_when_target_already_has_pending_request](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_409_when_target_already_has_pending_request.md)
- [test_seat_swap_endpoint_403_if_caller_disconnected](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_403_if_caller_disconnected.md)

# Imports

- `asyncio`
- `pytest`
- `pytest_asyncio`
- `httpx`
- `Cards_refactored`
- `ausbau.game_session`
- `ausbau.room`
- `frontend.auth.guest`
- `tests.multiplayer.conftest`
- `ausbau.server`