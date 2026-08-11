---
type: Python Function
title: _mode_multiplier
resource: ausbau/game_session.py#L198-L215
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/ai_pimc/rollout
  - functions/ausbau/game_session/trick_points
  - functions/ausbau/game_session/describe_weis
  - functions/ausbau/game_session/GameSession/_apply_stoeck
  - functions/ausbau/game_session/GameSession/_run_spiel
---

# Signature

`def _mode_multiplier(operator: str, *, trumpf_bock: bool = False) -> int:`

# Called by

- [rollout](../../../functions/ausbau/ai_pimc/rollout.md)
- [trick_points](../../../functions/ausbau/game_session/trick_points.md)
- [describe_weis](../../../functions/ausbau/game_session/describe_weis.md)
- [_apply_stoeck](../../../functions/ausbau/game_session/GameSession/_apply_stoeck.md)
- [_run_spiel](../../../functions/ausbau/game_session/GameSession/_run_spiel.md)