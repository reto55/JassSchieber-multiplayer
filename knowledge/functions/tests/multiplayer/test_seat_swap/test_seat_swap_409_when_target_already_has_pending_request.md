---
type: Python Function
title: test_seat_swap_409_when_target_already_has_pending_request
resource: tests/multiplayer/test_seat_swap.py#L382-L420
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/game_session/GameSession/_record_seat_swap_request
---

# Signature

`async def test_seat_swap_409_when_target_already_has_pending_request(client, client_other):`

# Calls

- [get_room](../../../../functions/ausbau/room/get_room.md)
- [_record_seat_swap_request](../../../../functions/ausbau/game_session/GameSession/_record_seat_swap_request.md)