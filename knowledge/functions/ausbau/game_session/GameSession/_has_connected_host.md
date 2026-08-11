---
type: Python Method
title: _has_connected_host
resource: ausbau/game_session.py#L673-L681
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/principal_id
  called_by:
  - functions/ausbau/game_session/GameSession/_reclaim_seat
---

# Signature

`def _has_connected_host(self) -> bool:`

# Calls

- [principal_id](../../../../functions/ausbau/room/principal_id.md)

# Called by

- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)