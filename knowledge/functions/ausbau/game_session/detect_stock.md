---
type: Python Function
title: detect_stock
resource: ausbau/game_session.py#L279-L284
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/game_session/GameSession/_apply_stoeck
  - functions/tests/test_game_session/test_detect_stock_true
  - functions/tests/test_game_session/test_detect_stock_false_wrong_suit
  - functions/tests/test_game_session/test_detect_stock_false_missing_ober
---

# Signature

`def detect_stock(hand: dict, operator: str) -> bool:`

# Called by

- [_apply_stoeck](../../../functions/ausbau/game_session/GameSession/_apply_stoeck.md)
- [test_detect_stock_true](../../../functions/tests/test_game_session/test_detect_stock_true.md)
- [test_detect_stock_false_wrong_suit](../../../functions/tests/test_game_session/test_detect_stock_false_wrong_suit.md)
- [test_detect_stock_false_missing_ober](../../../functions/tests/test_game_session/test_detect_stock_false_missing_ober.md)