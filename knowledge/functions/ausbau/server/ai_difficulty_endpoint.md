---
type: Python Function
title: ai_difficulty_endpoint
resource: ausbau/server.py#L624-L667
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/server/_get_principal
  - functions/ausbau/room/principal_id
  - functions/ausbau/ai_strategies/make_strategy
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/server/_room_state_dict
---

# Signature

`async def ai_difficulty_endpoint( code: str, request: Request, response: Response, payload: Optional[dict] = Body(default={}), ):`

# Calls

- [get_room](../../../functions/ausbau/room/get_room.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [principal_id](../../../functions/ausbau/room/principal_id.md)
- [make_strategy](../../../functions/ausbau/ai_strategies/make_strategy.md)
- [broadcast](../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_room_state_dict](../../../functions/ausbau/server/_room_state_dict.md)