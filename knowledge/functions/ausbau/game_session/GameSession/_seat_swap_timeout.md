---
type: Python Method
title: _seat_swap_timeout
resource: ausbau/game_session.py#L713-L725
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/send_to_seat
  called_by:
  - functions/ausbau/game_session/GameSession/_record_seat_swap_request
---

# Signature

`async def _seat_swap_timeout(self, from_pos: str, to_pos: str) -> None:`

# Calls

- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)

# Called by

- [_record_seat_swap_request](../../../../functions/ausbau/game_session/GameSession/_record_seat_swap_request.md)