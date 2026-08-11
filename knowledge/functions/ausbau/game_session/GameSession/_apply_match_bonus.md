---
type: Python Method
title: _apply_match_bonus
resource: ausbau/game_session.py#L1345-L1365
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_sn
  - functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_ow
  - functions/tests/multiplayer/test_variants/test_match_bonus_off_no_bonus_even_on_match
  - functions/tests/multiplayer/test_variants/test_match_bonus_split_winners_no_bonus
  - functions/tests/multiplayer/test_variants/test_match_bonus_incomplete_spiel_no_bonus
---

# Signature

`def _apply_match_bonus(self) -> tuple[int, int]:`

# Called by

- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [test_match_bonus_on_9_for_sn](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_sn.md)
- [test_match_bonus_on_9_for_ow](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_ow.md)
- [test_match_bonus_off_no_bonus_even_on_match](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_off_no_bonus_even_on_match.md)
- [test_match_bonus_split_winners_no_bonus](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_split_winners_no_bonus.md)
- [test_match_bonus_incomplete_spiel_no_bonus](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_incomplete_spiel_no_bonus.md)