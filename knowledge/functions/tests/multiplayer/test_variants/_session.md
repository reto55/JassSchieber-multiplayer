---
type: Python Function
title: _session
resource: tests/multiplayer/test_variants.py#L32-L42
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_sn
  - functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_ow
  - functions/tests/multiplayer/test_variants/test_match_bonus_off_no_bonus_even_on_match
  - functions/tests/multiplayer/test_variants/test_match_bonus_split_winners_no_bonus
  - functions/tests/multiplayer/test_variants/test_match_bonus_incomplete_spiel_no_bonus
  - functions/tests/multiplayer/test_variants/test_reset_spiel_trick_winners
  - functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners
  - functions/tests/multiplayer/test_variants/test_stoeck_on_sn_holds
  - functions/tests/multiplayer/test_variants/test_stoeck_on_ow_holds
  - functions/tests/multiplayer/test_variants/test_stoeck_off_no_bonus_even_when_holding
  - functions/tests/multiplayer/test_variants/test_stoeck_oben_unten_no_effect
---

# Signature

`def _session(*, trumpf_bock=False, match_bonus=True, stoeck=True):`

# Called by

- [test_match_bonus_on_9_for_sn](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_sn.md)
- [test_match_bonus_on_9_for_ow](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_on_9_for_ow.md)
- [test_match_bonus_off_no_bonus_even_on_match](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_off_no_bonus_even_on_match.md)
- [test_match_bonus_split_winners_no_bonus](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_split_winners_no_bonus.md)
- [test_match_bonus_incomplete_spiel_no_bonus](../../../../functions/tests/multiplayer/test_variants/test_match_bonus_incomplete_spiel_no_bonus.md)
- [test_reset_spiel_trick_winners](../../../../functions/tests/multiplayer/test_variants/test_reset_spiel_trick_winners.md)
- [test_play_trick_appends_to_spiel_winners](../../../../functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners.md)
- [test_stoeck_on_sn_holds](../../../../functions/tests/multiplayer/test_variants/test_stoeck_on_sn_holds.md)
- [test_stoeck_on_ow_holds](../../../../functions/tests/multiplayer/test_variants/test_stoeck_on_ow_holds.md)
- [test_stoeck_off_no_bonus_even_when_holding](../../../../functions/tests/multiplayer/test_variants/test_stoeck_off_no_bonus_even_when_holding.md)
- [test_stoeck_oben_unten_no_effect](../../../../functions/tests/multiplayer/test_variants/test_stoeck_oben_unten_no_effect.md)