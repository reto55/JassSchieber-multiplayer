---
type: Python Method
title: _game_start_for
resource: ausbau/game_session.py#L1395-L1453
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/hand_to_codes
  - functions/ausbau/game_session/GameSession/_partner_of
  called_by:
  - functions/ausbau/game_session/_factory
  - functions/tests/multiplayer/test_run_spiel/test_game_start_for_seat_includes_hand_partner_variant
  - functions/tests/multiplayer/test_run_spiel/test_game_start_for_spectator_no_hand_no_partner
  - functions/tests/multiplayer/test_run_spiel/test_game_start_for_seat_variant_overrides_propagate
---

# Signature

`def _game_start_for(self, position) -> dict:`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [hand_to_codes](../../../../functions/ausbau/game_session/hand_to_codes.md)
- [_partner_of](../../../../functions/ausbau/game_session/GameSession/_partner_of.md)

# Called by

- [_factory](../../../../functions/ausbau/game_session/_factory.md)
- [test_game_start_for_seat_includes_hand_partner_variant](../../../../functions/tests/multiplayer/test_run_spiel/test_game_start_for_seat_includes_hand_partner_variant.md)
- [test_game_start_for_spectator_no_hand_no_partner](../../../../functions/tests/multiplayer/test_run_spiel/test_game_start_for_spectator_no_hand_no_partner.md)
- [test_game_start_for_seat_variant_overrides_propagate](../../../../functions/tests/multiplayer/test_run_spiel/test_game_start_for_seat_variant_overrides_propagate.md)