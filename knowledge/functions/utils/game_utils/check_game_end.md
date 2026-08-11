---
type: Python Function
title: check_game_end
resource: utils/game_utils.py#L77-L91
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/game_session/GameSession/start_game
  - functions/tests/test_game_utils/TestGameUtils/test_check_game_end
  - functions/tests/test_integration/TestIntegration/test_integration_database_and_game
---

# Signature

`def check_game_end(pointSN, pointOW, end_game):`

# Called by

- [start_game](../../../functions/ausbau/game_session/GameSession/start_game.md)
- [test_check_game_end](../../../functions/tests/test_game_utils/TestGameUtils/test_check_game_end.md)
- [test_integration_database_and_game](../../../functions/tests/test_integration/TestIntegration/test_integration_database_and_game.md)