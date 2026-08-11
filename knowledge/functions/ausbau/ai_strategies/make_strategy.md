---
type: Python Function
title: make_strategy
resource: ausbau/ai_strategies.py#L574-L581
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  - functions/ausbau/game_session/GameSession/_compute_ai_action
  - functions/ausbau/room/create_room
  - functions/ausbau/server/leave_endpoint
  - functions/ausbau/server/ai_difficulty_endpoint
  - functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_human_join_clears_strategy_keeps_difficulty
  - functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_lobby_leave_rebuilds_strategy_from_preserved_difficulty
  - functions/tests/multiplayer/test_ai_strategies/test_make_strategy_easy
  - functions/tests/multiplayer/test_ai_strategies/test_make_strategy_medium
  - functions/tests/multiplayer/test_ai_strategies/test_make_strategy_hard
  - functions/tests/multiplayer/test_ai_strategies/test_make_strategy_unknown
  - functions/tests/multiplayer/test_e2e_mixed_ai/test_e2e_mixed_difficulty_3_ai
---

# Signature

`def make_strategy(difficulty: str, position: str) -> AIStrategy:`

# Called by

- [_reconnect_timeout](../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [_compute_ai_action](../../../functions/ausbau/game_session/GameSession/_compute_ai_action.md)
- [create_room](../../../functions/ausbau/room/create_room.md)
- [leave_endpoint](../../../functions/ausbau/server/leave_endpoint.md)
- [ai_difficulty_endpoint](../../../functions/ausbau/server/ai_difficulty_endpoint.md)
- [test_human_join_clears_strategy_keeps_difficulty](../../../functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_human_join_clears_strategy_keeps_difficulty.md)
- [test_lobby_leave_rebuilds_strategy_from_preserved_difficulty](../../../functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_lobby_leave_rebuilds_strategy_from_preserved_difficulty.md)
- [test_make_strategy_easy](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_easy.md)
- [test_make_strategy_medium](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_medium.md)
- [test_make_strategy_hard](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_hard.md)
- [test_make_strategy_unknown](../../../functions/tests/multiplayer/test_ai_strategies/test_make_strategy_unknown.md)
- [test_e2e_mixed_difficulty_3_ai](../../../functions/tests/multiplayer/test_e2e_mixed_ai/test_e2e_mixed_difficulty_3_ai.md)