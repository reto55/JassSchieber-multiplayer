---
type: Python Method
title: _transfer_host
resource: ausbau/game_session.py#L417-L451
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/principal_id
  - functions/tests/multiplayer/conftest/FakeWebSocket/send_json
  called_by:
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/server/leave_endpoint
  - functions/tests/multiplayer/test_host_transfer/test_transfer_host_no_op_when_no_connected_humans
---

# Signature

`async def _transfer_host(self):`

# Calls

- [principal_id](../../../../functions/ausbau/room/principal_id.md)
- [send_json](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/send_json.md)

# Called by

- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reconnect_timeout](../../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [leave_endpoint](../../../../functions/ausbau/server/leave_endpoint.md)
- [test_transfer_host_no_op_when_no_connected_humans](../../../../functions/tests/multiplayer/test_host_transfer/test_transfer_host_no_op_when_no_connected_humans.md)