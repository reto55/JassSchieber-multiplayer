---
type: Python Function
title: leave_spectator_endpoint
resource: ausbau/server.py#L470-L493
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/server/_get_principal
  - functions/ausbau/game_session/GameSession/broadcast
---

# Signature

`async def leave_spectator_endpoint( code: str, request: Request, response: Response, ):`

# Calls

- [get_room](../../../functions/ausbau/room/get_room.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [broadcast](../../../functions/ausbau/game_session/GameSession/broadcast.md)