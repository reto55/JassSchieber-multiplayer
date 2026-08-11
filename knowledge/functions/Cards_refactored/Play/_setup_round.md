---
type: Python Method
title: _setup_round
resource: Cards_refactored.py#L309-L322
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/determine_trumpf
  - functions/ausbau/server/index
  - functions/Cards_refactored/wiis
  - functions/Cards_refactored/wiis_gleiche
  called_by:
  - functions/Cards_refactored/Play/_setup_game
---

# Signature

`def _setup_round(self, first_player):`

# Calls

- [determine_trumpf](../../../functions/Cards_refactored/determine_trumpf.md)
- [index](../../../functions/ausbau/server/index.md)
- [wiis](../../../functions/Cards_refactored/wiis.md)
- [wiis_gleiche](../../../functions/Cards_refactored/wiis_gleiche.md)

# Called by

- [_setup_game](../../../functions/Cards_refactored/Play/_setup_game.md)