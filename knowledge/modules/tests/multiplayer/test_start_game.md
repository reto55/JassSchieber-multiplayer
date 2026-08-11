---
type: Python Module
title: test_start_game
resource: tests/multiplayer/test_start_game.py#L1-L117
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/pytest
  - external/pytest-asyncio
  - external/httpx
  - external/ausbau-server
  - external/ausbau-game-session
  - external/ausbau-room
---

# Contains

- [client](../../../functions/tests/multiplayer/test_start_game/client.md)
- [client_other](../../../functions/tests/multiplayer/test_start_game/client_other.md)
- [_stub_start_game](../../../functions/tests/multiplayer/test_start_game/_stub_start_game.md)
- [test_start_happy_path_204](../../../functions/tests/multiplayer/test_start_game/test_start_happy_path_204.md)
- [test_start_not_host_403](../../../functions/tests/multiplayer/test_start_game/test_start_not_host_403.md)
- [test_start_not_lobby_409](../../../functions/tests/multiplayer/test_start_game/test_start_not_lobby_409.md)
- [test_start_room_not_found_404](../../../functions/tests/multiplayer/test_start_game/test_start_room_not_found_404.md)

# Imports

- `asyncio`
- `pytest`
- `pytest_asyncio`
- `httpx`
- `ausbau.server`
- `ausbau.game_session`
- `ausbau.room`