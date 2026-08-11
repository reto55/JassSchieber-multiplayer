---
type: Python Function
title: test_e2e_mixed_difficulty_3_ai
resource: tests/multiplayer/test_e2e_mixed_ai.py#L38-L76
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_strategies/make_strategy
  - functions/ausbau/game_session/GameSession/start_game
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_e2e_mixed_difficulty_3_ai(fast_clock):`

# Calls

- [make_strategy](../../../../functions/ausbau/ai_strategies/make_strategy.md)
- [start_game](../../../../functions/ausbau/game_session/GameSession/start_game.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)