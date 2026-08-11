---
type: Python Function
title: find_rooms_for_principal
resource: ausbau/room.py#L203-L222
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/principal_id
  called_by:
  - functions/ausbau/server/rooms_mine_endpoint
---

# Signature

`def find_rooms_for_principal(p) -> list[dict]:`

# Calls

- [principal_id](../../../functions/ausbau/room/principal_id.md)

# Called by

- [rooms_mine_endpoint](../../../functions/ausbau/server/rooms_mine_endpoint.md)