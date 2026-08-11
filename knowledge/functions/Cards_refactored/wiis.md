---
type: Python Function
title: wiis
resource: Cards_refactored.py#L406-L419
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/calculate_wiis
  called_by:
  - functions/Cards_refactored/Play/_setup_round
  - functions/Cards_refactored/determine_trumpf
  - functions/Cards_refactored/determine_trumpf_after_schieben
  - functions/ausbau/game_session/GameSession/_weis_phase
---

# Signature

`def wiis(player):`

# Calls

- [calculate_wiis](../../functions/Cards_refactored/calculate_wiis.md)

# Called by

- [_setup_round](../../functions/Cards_refactored/Play/_setup_round.md)
- [determine_trumpf](../../functions/Cards_refactored/determine_trumpf.md)
- [determine_trumpf_after_schieben](../../functions/Cards_refactored/determine_trumpf_after_schieben.md)
- [_weis_phase](../../functions/ausbau/game_session/GameSession/_weis_phase.md)