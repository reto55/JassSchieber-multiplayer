---
type: Python Function
title: determine_trumpf
resource: Cards_refactored.py#L422-L480
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/determine_longest_suit
  - functions/Cards_refactored/wiis
  - functions/Cards_refactored/sum_values
  called_by:
  - functions/Cards_refactored/Play/_setup_round
---

# Signature

`def determine_trumpf(player):`

# Calls

- [determine_longest_suit](../../functions/Cards_refactored/determine_longest_suit.md)
- [wiis](../../functions/Cards_refactored/wiis.md)
- [sum_values](../../functions/Cards_refactored/sum_values.md)

# Called by

- [_setup_round](../../functions/Cards_refactored/Play/_setup_round.md)