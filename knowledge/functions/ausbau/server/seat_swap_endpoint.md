---
type: Python Function
title: seat_swap_endpoint
resource: ausbau/server.py#L543-L615
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/server/_get_principal
  - functions/ausbau/room/principal_id
  - functions/ausbau/game_session/GameSession/_record_seat_swap_request
  - functions/ausbau/game_session/GameSession/_accept_seat_swap
---

# Signature

`async def seat_swap_endpoint( code: str, request: Request, response: Response, payload: Optional[dict] = Body(default={}), ):`

# Calls

- [get_room](../../../functions/ausbau/room/get_room.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [principal_id](../../../functions/ausbau/room/principal_id.md)
- [_record_seat_swap_request](../../../functions/ausbau/game_session/GameSession/_record_seat_swap_request.md)
- [_accept_seat_swap](../../../functions/ausbau/game_session/GameSession/_accept_seat_swap.md)