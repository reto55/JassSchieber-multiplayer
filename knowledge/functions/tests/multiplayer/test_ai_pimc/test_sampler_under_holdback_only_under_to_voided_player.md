---
type: Python Function
title: test_sampler_under_holdback_only_under_to_voided_player
resource: tests/multiplayer/test_ai_pimc.py#L93-L114
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/Cards_refactored/create_card
  - functions/tests/multiplayer/test_ai_pimc/_basic_state
  - functions/tests/multiplayer/test_ai_pimc/_hand
  - functions/ausbau/ai_pimc/DealSampler/sample
  - functions/ausbau/game_session/card_to_code
---

# Signature

`def test_sampler_under_holdback_only_under_to_voided_player(): # compo discarded on a trump lead -> may hold ONLY the trump Under.`

# Calls

- [create_card](../../../../functions/Cards_refactored/create_card.md)
- [_basic_state](../../../../functions/tests/multiplayer/test_ai_pimc/_basic_state.md)
- [_hand](../../../../functions/tests/multiplayer/test_ai_pimc/_hand.md)
- [sample](../../../../functions/ausbau/ai_pimc/DealSampler/sample.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)