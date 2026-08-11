---
type: Python Method
title: _record_seat_swap_request
resource: ausbau/game_session.py#L683-L711
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat_swap_timeout
  - functions/ausbau/game_session/GameSession/send_to_seat
  called_by:
  - functions/ausbau/server/seat_swap_endpoint
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_records_and_pushes
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_overwrites_prior_from_same_seat
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_accept_sets_pending_swap
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_ttl_fires_seat_swap_expired
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_409_when_target_already_has_pending_request
---

# Signature

`async def _record_seat_swap_request( self, from_pos: str, to_pos: str, from_display: str ) -> None:`

# Calls

- [_seat_swap_timeout](../../../../functions/ausbau/game_session/GameSession/_seat_swap_timeout.md)
- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)

# Called by

- [seat_swap_endpoint](../../../../functions/ausbau/server/seat_swap_endpoint.md)
- [test_seat_swap_request_records_and_pushes](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_records_and_pushes.md)
- [test_seat_swap_request_overwrites_prior_from_same_seat](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_overwrites_prior_from_same_seat.md)
- [test_seat_swap_accept_sets_pending_swap](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_accept_sets_pending_swap.md)
- [test_seat_swap_ttl_fires_seat_swap_expired](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_ttl_fires_seat_swap_expired.md)
- [test_seat_swap_409_when_target_already_has_pending_request](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_409_when_target_already_has_pending_request.md)