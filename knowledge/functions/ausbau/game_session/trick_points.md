---
type: Python Function
title: trick_points
resource: ausbau/game_session.py#L218-L235
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/_mode_multiplier
  called_by:
  - functions/ausbau/ai_pimc/rollout
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/test_variants/test_trumpf_bock_off_trump_round
  - functions/tests/multiplayer/test_variants/test_trumpf_bock_on_trump_round
  - functions/tests/multiplayer/test_variants/test_trumpf_bock_no_effect_on_oben
  - functions/tests/multiplayer/test_variants/test_trumpf_bock_no_effect_on_unten
  - functions/tests/test_game_session/test_trick_points_oben_mode
  - functions/tests/test_game_session/test_trick_points_trumpf_mode
---

# Signature

`def trick_points(trick: dict, operator: str, *, trumpf_bock: bool = False) -> int:`

# Calls

- [_mode_multiplier](../../../functions/ausbau/game_session/_mode_multiplier.md)

# Called by

- [rollout](../../../functions/ausbau/ai_pimc/rollout.md)
- [_play_trick](../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [test_trumpf_bock_off_trump_round](../../../functions/tests/multiplayer/test_variants/test_trumpf_bock_off_trump_round.md)
- [test_trumpf_bock_on_trump_round](../../../functions/tests/multiplayer/test_variants/test_trumpf_bock_on_trump_round.md)
- [test_trumpf_bock_no_effect_on_oben](../../../functions/tests/multiplayer/test_variants/test_trumpf_bock_no_effect_on_oben.md)
- [test_trumpf_bock_no_effect_on_unten](../../../functions/tests/multiplayer/test_variants/test_trumpf_bock_no_effect_on_unten.md)
- [test_trick_points_oben_mode](../../../functions/tests/test_game_session/test_trick_points_oben_mode.md)
- [test_trick_points_trumpf_mode](../../../functions/tests/test_game_session/test_trick_points_trumpf_mode.md)