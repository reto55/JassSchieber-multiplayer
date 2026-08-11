---
type: Python Method
title: send_json
resource: tests/multiplayer/conftest.py#L31-L32
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/game_session/GameSession/_transfer_host
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/broadcast_per_seat
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/server/websocket_endpoint
  - functions/tests/multiplayer/test_conftest_smoke/test_fake_ws_send_recv
---

# Signature

`async def send_json(self, msg: dict) -> None:`

# Called by

- [_transfer_host](../../../../../functions/ausbau/game_session/GameSession/_transfer_host.md)
- [send_to_seat](../../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [broadcast](../../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [broadcast_per_seat](../../../../../functions/ausbau/game_session/GameSession/broadcast_per_seat.md)
- [_reclaim_seat](../../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [websocket_endpoint](../../../../../functions/ausbau/server/websocket_endpoint.md)
- [test_fake_ws_send_recv](../../../../../functions/tests/multiplayer/test_conftest_smoke/test_fake_ws_send_recv.md)