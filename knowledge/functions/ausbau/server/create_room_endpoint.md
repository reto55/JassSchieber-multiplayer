---
type: Python Function
title: create_room_endpoint
resource: ausbau/server.py#L227-L241
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/server/_get_principal
  - functions/ausbau/room/create_room
  - functions/ausbau/server/_room_state_dict
---

# Signature

`async def create_room_endpoint( request: Request, response: Response, payload: Optional[dict] = Body(default={}), ):`

# Calls

- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [create_room](../../../functions/ausbau/room/create_room.md)
- [_room_state_dict](../../../functions/ausbau/server/_room_state_dict.md)