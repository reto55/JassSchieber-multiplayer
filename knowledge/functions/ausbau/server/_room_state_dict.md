---
type: Python Function
title: _room_state_dict
resource: ausbau/server.py#L209-L223
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/server/create_room_endpoint
  - functions/ausbau/server/get_room_endpoint
  - functions/ausbau/server/join_endpoint
  - functions/ausbau/server/spectate_endpoint
  - functions/ausbau/server/ai_difficulty_endpoint
  - functions/ausbau/server/target_score_endpoint
---

# Signature

`def _room_state_dict(room) -> dict:`

# Called by

- [create_room_endpoint](../../../functions/ausbau/server/create_room_endpoint.md)
- [get_room_endpoint](../../../functions/ausbau/server/get_room_endpoint.md)
- [join_endpoint](../../../functions/ausbau/server/join_endpoint.md)
- [spectate_endpoint](../../../functions/ausbau/server/spectate_endpoint.md)
- [ai_difficulty_endpoint](../../../functions/ausbau/server/ai_difficulty_endpoint.md)
- [target_score_endpoint](../../../functions/ausbau/server/target_score_endpoint.md)