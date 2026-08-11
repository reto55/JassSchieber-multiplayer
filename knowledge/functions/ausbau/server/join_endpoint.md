---
type: Python Function
title: join_endpoint
resource: ausbau/server.py#L287-L336
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/server/_get_principal
  - functions/ausbau/server/index
  - functions/ausbau/server/_room_state_dict
  - functions/ausbau/game_session/GameSession/broadcast
---

# Signature

`async def join_endpoint( code: str, payload: Optional[dict] = Body(default={}), request: Request = None, response: Response = None, ):`

# Calls

- [get_room](../../../functions/ausbau/room/get_room.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [index](../../../functions/ausbau/server/index.md)
- [_room_state_dict](../../../functions/ausbau/server/_room_state_dict.md)
- [broadcast](../../../functions/ausbau/game_session/GameSession/broadcast.md)