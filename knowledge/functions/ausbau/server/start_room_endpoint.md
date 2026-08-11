---
type: Python Function
title: start_room_endpoint
resource: ausbau/server.py#L501-L534
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/server/_get_principal
  - functions/ausbau/room/principal_id
  - functions/ausbau/game_session/GameSession/start_game
---

# Signature

`async def start_room_endpoint( code: str, request: Request, response: Response, ):`

# Calls

- [get_room](../../../functions/ausbau/room/get_room.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [principal_id](../../../functions/ausbau/room/principal_id.md)
- [start_game](../../../functions/ausbau/game_session/GameSession/start_game.md)