---
type: Python Function
title: describe_weis
resource: ausbau/game_session.py#L264-L276
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/_mode_multiplier
  called_by:
  - functions/ausbau/game_session/GameSession/_weis_phase
  - functions/tests/test_game_session/test_describe_weis_dreier
  - functions/tests/test_game_session/test_describe_weis_vierter
  - functions/tests/test_game_session/test_describe_weis_fuenfer
  - functions/tests/test_game_session/test_describe_weis_viererle
---

# Signature

`def describe_weis(weis_combos: list, weis_gleiche: list, operator: str = "") -> list:`

# Calls

- [_mode_multiplier](../../../functions/ausbau/game_session/_mode_multiplier.md)

# Called by

- [_weis_phase](../../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [test_describe_weis_dreier](../../../functions/tests/test_game_session/test_describe_weis_dreier.md)
- [test_describe_weis_vierter](../../../functions/tests/test_game_session/test_describe_weis_vierter.md)
- [test_describe_weis_fuenfer](../../../functions/tests/test_game_session/test_describe_weis_fuenfer.md)
- [test_describe_weis_viererle](../../../functions/tests/test_game_session/test_describe_weis_viererle.md)