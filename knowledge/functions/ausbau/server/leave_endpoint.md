---
type: Python Function
title: leave_endpoint
resource: ausbau/server.py#L340-L439
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/server/_get_principal
  - functions/ausbau/room/principal_id
  - functions/ausbau/ai_strategies/make_strategy
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/_transfer_host
  - functions/ausbau/game_session/GameSession/_update_idle_since
---

# Signature

`async def leave_endpoint( code: str, payload: Optional[dict] = Body(default={}), request: Request = None, response: Response = None, ):`

# Calls

- [get_room](../../../functions/ausbau/room/get_room.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [principal_id](../../../functions/ausbau/room/principal_id.md)
- [make_strategy](../../../functions/ausbau/ai_strategies/make_strategy.md)
- [broadcast](../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_transfer_host](../../../functions/ausbau/game_session/GameSession/_transfer_host.md)
- [_update_idle_since](../../../functions/ausbau/game_session/GameSession/_update_idle_since.md)