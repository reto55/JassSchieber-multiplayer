---
type: Python Function
title: test_start_game_emits_game_start_per_spiel
resource: tests/multiplayer/test_run_spiel.py#L168-L198
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_run_spiel/_all_ai_session
  - functions/ausbau/game_session/GameSession/start_game
  - functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type
---

# Signature

`async def test_start_game_emits_game_start_per_spiel(monkeypatch):`

# Calls

- [_all_ai_session](../../../../functions/tests/multiplayer/test_run_spiel/_all_ai_session.md)
- [start_game](../../../../functions/ausbau/game_session/GameSession/start_game.md)
- [all_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/all_sent_of_type.md)