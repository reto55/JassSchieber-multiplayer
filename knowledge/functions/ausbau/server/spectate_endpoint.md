---
type: Python Function
title: spectate_endpoint
resource: ausbau/server.py#L443-L466
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/server/_get_principal
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/server/_room_state_dict
---

# Signature

`async def spectate_endpoint( code: str, request: Request, response: Response, ):`

# Calls

- [get_room](../../../functions/ausbau/room/get_room.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [broadcast](../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_room_state_dict](../../../functions/ausbau/server/_room_state_dict.md)