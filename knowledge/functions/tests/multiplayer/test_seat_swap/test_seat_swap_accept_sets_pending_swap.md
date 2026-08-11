---
type: Python Function
title: test_seat_swap_accept_sets_pending_swap
resource: tests/multiplayer/test_seat_swap.py#L106-L116
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_record_seat_swap_request
  - functions/ausbau/game_session/GameSession/_accept_seat_swap
---

# Signature

`async def test_seat_swap_accept_sets_pending_swap():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_record_seat_swap_request](../../../../functions/ausbau/game_session/GameSession/_record_seat_swap_request.md)
- [_accept_seat_swap](../../../../functions/ausbau/game_session/GameSession/_accept_seat_swap.md)