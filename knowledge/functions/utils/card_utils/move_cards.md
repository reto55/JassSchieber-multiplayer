---
type: Python Function
title: move_cards
resource: utils/card_utils.py#L81-L95
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/utils/card_utils/add_card
  - functions/utils/card_utils/pop_card
  called_by:
  - functions/tests/test_card_utils/TestCardUtils/test_move_cards
  - functions/tests/test_integration/TestIntegration/test_integration_card_and_game
---

# Signature

`def move_cards(cards, sp1, num):`

# Calls

- [add_card](../../../functions/utils/card_utils/add_card.md)
- [pop_card](../../../functions/utils/card_utils/pop_card.md)

# Called by

- [test_move_cards](../../../functions/tests/test_card_utils/TestCardUtils/test_move_cards.md)
- [test_integration_card_and_game](../../../functions/tests/test_integration/TestIntegration/test_integration_card_and_game.md)