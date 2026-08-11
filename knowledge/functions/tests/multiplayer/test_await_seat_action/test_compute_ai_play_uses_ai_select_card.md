---
type: Python Function
title: test_compute_ai_play_uses_ai_select_card
resource: tests/multiplayer/test_await_seat_action.py#L196-L250
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_compute_ai_action
  - functions/ausbau/game_session/card_to_code
---

# Signature

`async def test_compute_ai_play_uses_ai_select_card(monkeypatch):`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_compute_ai_action](../../../../functions/ausbau/game_session/GameSession/_compute_ai_action.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)