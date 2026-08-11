---
type: Python Method
title: _update_idle_since
resource: ausbau/game_session.py#L402-L415
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seated_human_count
  - functions/ausbau/game_session/GameSession/_connected_human_count
  called_by:
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/server/leave_endpoint
---

# Signature

`def _update_idle_since(self) -> None:`

# Calls

- [_seated_human_count](../../../../functions/ausbau/game_session/GameSession/_seated_human_count.md)
- [_connected_human_count](../../../../functions/ausbau/game_session/GameSession/_connected_human_count.md)

# Called by

- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reconnect_timeout](../../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [leave_endpoint](../../../../functions/ausbau/server/leave_endpoint.md)