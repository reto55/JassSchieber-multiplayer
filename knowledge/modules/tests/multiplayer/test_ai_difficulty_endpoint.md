---
type: Python Module
title: test_ai_difficulty_endpoint
resource: tests/multiplayer/test_ai_difficulty_endpoint.py#L1-L120
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/pytest
  - external/pytest-asyncio
  - external/httpx
  - external/ausbau-room
  - external/ausbau-server
  - external/ausbau-ai-strategies
---

# Contains

- [client](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/client.md)
- [client_other](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/client_other.md)
- [_make_lobby](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/_make_lobby.md)
- [test_set_ai_difficulty_happy](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/test_set_ai_difficulty_happy.md)
- [test_set_ai_difficulty_invalid_level](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/test_set_ai_difficulty_invalid_level.md)
- [test_set_ai_difficulty_invalid_position](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/test_set_ai_difficulty_invalid_position.md)
- [test_set_ai_difficulty_human_seat](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/test_set_ai_difficulty_human_seat.md)
- [test_set_ai_difficulty_not_host](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/test_set_ai_difficulty_not_host.md)
- [test_set_ai_difficulty_mid_game_409](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/test_set_ai_difficulty_mid_game_409.md)
- [test_set_ai_difficulty_room_not_found_404](../../../functions/tests/multiplayer/test_ai_difficulty_endpoint/test_set_ai_difficulty_room_not_found_404.md)

# Imports

- `pytest`
- `pytest_asyncio`
- `httpx`
- `ausbau.room`
- `ausbau.server`
- `ausbau.ai_strategies`