---
type: Python Method
title: _apply_stoeck
resource: ausbau/game_session.py#L1367-L1393
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/detect_stock
  - functions/ausbau/game_session/_mode_multiplier
  called_by:
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/tests/multiplayer/test_variants/test_stoeck_on_sn_holds
  - functions/tests/multiplayer/test_variants/test_stoeck_on_ow_holds
  - functions/tests/multiplayer/test_variants/test_stoeck_off_no_bonus_even_when_holding
  - functions/tests/multiplayer/test_variants/test_stoeck_oben_unten_no_effect
---

# Signature

`def _apply_stoeck(self, play: Play) -> tuple[int, int]:`

# Calls

- [detect_stock](../../../../functions/ausbau/game_session/detect_stock.md)
- [_mode_multiplier](../../../../functions/ausbau/game_session/_mode_multiplier.md)

# Called by

- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [test_stoeck_on_sn_holds](../../../../functions/tests/multiplayer/test_variants/test_stoeck_on_sn_holds.md)
- [test_stoeck_on_ow_holds](../../../../functions/tests/multiplayer/test_variants/test_stoeck_on_ow_holds.md)
- [test_stoeck_off_no_bonus_even_when_holding](../../../../functions/tests/multiplayer/test_variants/test_stoeck_off_no_bonus_even_when_holding.md)
- [test_stoeck_oben_unten_no_effect](../../../../functions/tests/multiplayer/test_variants/test_stoeck_oben_unten_no_effect.md)