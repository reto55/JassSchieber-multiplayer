---
type: Python Method
title: _commit_pending_swap
resource: ausbau/game_session.py#L742-L800
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/game_session/GameSession/broadcast
  called_by:
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands
  - functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_noop_when_no_pending
  - functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept
---

# Signature

`async def _commit_pending_swap(self) -> None:`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)

# Called by

- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [test_commit_pending_swap_swaps_principals_and_hands](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands.md)
- [test_commit_pending_swap_noop_when_no_pending](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_noop_when_no_pending.md)
- [test_commit_aborts_if_either_seat_disconnected_post_accept](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept.md)