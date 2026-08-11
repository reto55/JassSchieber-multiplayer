---
type: Python Method
title: _accept_seat_swap
resource: ausbau/game_session.py#L727-L740
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/server/seat_swap_endpoint
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_accept_sets_pending_swap
---

# Signature

`async def _accept_seat_swap(self, accepter_pos: str, requester_pos: str) -> None:`

# Called by

- [seat_swap_endpoint](../../../../functions/ausbau/server/seat_swap_endpoint.md)
- [test_seat_swap_accept_sets_pending_swap](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_accept_sets_pending_swap.md)