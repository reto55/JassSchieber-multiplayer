---
type: Python Function
title: _get_principal
resource: ausbau/server.py#L148-L188
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/server/_ensure_auth_initialised
  - functions/frontend/auth/guest/read_guest_cookie
  - functions/frontend/auth/guest/issue_guest_cookie
  called_by:
  - functions/ausbau/server/create_room_endpoint
  - functions/ausbau/server/rooms_mine_endpoint
  - functions/ausbau/server/join_endpoint
  - functions/ausbau/server/leave_endpoint
  - functions/ausbau/server/spectate_endpoint
  - functions/ausbau/server/leave_spectator_endpoint
  - functions/ausbau/server/start_room_endpoint
  - functions/ausbau/server/seat_swap_endpoint
  - functions/ausbau/server/ai_difficulty_endpoint
  - functions/ausbau/server/target_score_endpoint
---

# Signature

`async def _get_principal(request: Request, response: Response):`

# Calls

- [_ensure_auth_initialised](../../../functions/ausbau/server/_ensure_auth_initialised.md)
- [read_guest_cookie](../../../functions/frontend/auth/guest/read_guest_cookie.md)
- [issue_guest_cookie](../../../functions/frontend/auth/guest/issue_guest_cookie.md)

# Called by

- [create_room_endpoint](../../../functions/ausbau/server/create_room_endpoint.md)
- [rooms_mine_endpoint](../../../functions/ausbau/server/rooms_mine_endpoint.md)
- [join_endpoint](../../../functions/ausbau/server/join_endpoint.md)
- [leave_endpoint](../../../functions/ausbau/server/leave_endpoint.md)
- [spectate_endpoint](../../../functions/ausbau/server/spectate_endpoint.md)
- [leave_spectator_endpoint](../../../functions/ausbau/server/leave_spectator_endpoint.md)
- [start_room_endpoint](../../../functions/ausbau/server/start_room_endpoint.md)
- [seat_swap_endpoint](../../../functions/ausbau/server/seat_swap_endpoint.md)
- [ai_difficulty_endpoint](../../../functions/ausbau/server/ai_difficulty_endpoint.md)
- [target_score_endpoint](../../../functions/ausbau/server/target_score_endpoint.md)