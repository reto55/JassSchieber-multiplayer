---
type: Python Method
title: send_to_seat
resource: ausbau/game_session.py#L453-L461
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/send_json
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  called_by:
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/broadcast_per_seat
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/game_session/GameSession/_record_seat_swap_request
  - functions/ausbau/game_session/GameSession/_seat_swap_timeout
  - functions/ausbau/game_session/GameSession/_commit_pending_swap
  - functions/ausbau/game_session/GameSession/_trump_phase
  - functions/ausbau/game_session/GameSession/_weis_phase
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/test_routing_helpers/test_send_to_seat_human
  - functions/tests/multiplayer/test_routing_helpers/test_send_to_seat_ai_is_noop
---

# Signature

`async def send_to_seat(self, position: str, msg: dict) -> None:`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [send_json](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/send_json.md)
- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)

# Called by

- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [broadcast_per_seat](../../../../functions/ausbau/game_session/GameSession/broadcast_per_seat.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [_record_seat_swap_request](../../../../functions/ausbau/game_session/GameSession/_record_seat_swap_request.md)
- [_seat_swap_timeout](../../../../functions/ausbau/game_session/GameSession/_seat_swap_timeout.md)
- [_commit_pending_swap](../../../../functions/ausbau/game_session/GameSession/_commit_pending_swap.md)
- [_trump_phase](../../../../functions/ausbau/game_session/GameSession/_trump_phase.md)
- [_weis_phase](../../../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [test_send_to_seat_human](../../../../functions/tests/multiplayer/test_routing_helpers/test_send_to_seat_human.md)
- [test_send_to_seat_ai_is_noop](../../../../functions/tests/multiplayer/test_routing_helpers/test_send_to_seat_ai_is_noop.md)