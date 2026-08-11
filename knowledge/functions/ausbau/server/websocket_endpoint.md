---
type: Python Function
title: websocket_endpoint
resource: ausbau/server.py#L713-L859
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/FakeWebSocket/accept
  - functions/ausbau/server/_ensure_auth_initialised
  - functions/frontend/auth/guest/read_guest_cookie
  - functions/tests/multiplayer/conftest/FakeWebSocket/send_json
  - functions/ausbau/room/get_room
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/game_session/GameSession/_room_resume_message_for
  - functions/tests/multiplayer/conftest/FakeWebSocket/receive_json
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/_disconnect_seat
---

# Signature

`async def websocket_endpoint(websocket: WebSocket, code: str):`

# Calls

- [accept](../../../functions/tests/multiplayer/conftest/FakeWebSocket/accept.md)
- [_ensure_auth_initialised](../../../functions/ausbau/server/_ensure_auth_initialised.md)
- [read_guest_cookie](../../../functions/frontend/auth/guest/read_guest_cookie.md)
- [send_json](../../../functions/tests/multiplayer/conftest/FakeWebSocket/send_json.md)
- [get_room](../../../functions/ausbau/room/get_room.md)
- [_reclaim_seat](../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [_room_resume_message_for](../../../functions/ausbau/game_session/GameSession/_room_resume_message_for.md)
- [receive_json](../../../functions/tests/multiplayer/conftest/FakeWebSocket/receive_json.md)
- [broadcast](../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_disconnect_seat](../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)