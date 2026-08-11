---
type: Python Function
title: rooms_mine_endpoint
resource: ausbau/server.py#L245-L248
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/server/_get_principal
  - functions/ausbau/room/find_rooms_for_principal
---

# Signature

`async def rooms_mine_endpoint(request: Request, response: Response):`

# Calls

- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [find_rooms_for_principal](../../../functions/ausbau/room/find_rooms_for_principal.md)