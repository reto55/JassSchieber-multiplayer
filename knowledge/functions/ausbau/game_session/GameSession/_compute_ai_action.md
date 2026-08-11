---
type: Python Method
title: _compute_ai_action
resource: ausbau/game_session.py#L984-L1011
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_strategies/make_strategy
  called_by:
  - functions/ausbau/game_session/GameSession/_await_seat_action
  - functions/tests/multiplayer/test_await_seat_action/test_compute_ai_trump_uses_farbe_lang
  - functions/tests/multiplayer/test_await_seat_action/test_compute_ai_play_uses_ai_select_card
---

# Signature

`def _compute_ai_action(self, seat, valid_actions: dict) -> dict:`

# Calls

- [make_strategy](../../../../functions/ausbau/ai_strategies/make_strategy.md)

# Called by

- [_await_seat_action](../../../../functions/ausbau/game_session/GameSession/_await_seat_action.md)
- [test_compute_ai_trump_uses_farbe_lang](../../../../functions/tests/multiplayer/test_await_seat_action/test_compute_ai_trump_uses_farbe_lang.md)
- [test_compute_ai_play_uses_ai_select_card](../../../../functions/tests/multiplayer/test_await_seat_action/test_compute_ai_play_uses_ai_select_card.md)