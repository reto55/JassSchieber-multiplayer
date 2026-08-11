---
type: Python Function
title: test_sampler_respects_capacities_and_partitions_unseen
resource: tests/multiplayer/test_ai_pimc.py#L54-L72
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

`def test_sampler_respects_capacities_and_partitions_unseen(): # 2 unseen Schellen cards, two others each needing exactly 1 card.`

# Calls

- [create_card](../../../../functions/Cards_refactored/create_card.md)
- [_basic_state](../../../../functions/tests/multiplayer/test_ai_pimc/_basic_state.md)
- [_hand](../../../../functions/tests/multiplayer/test_ai_pimc/_hand.md)
- [sample](../../../../functions/ausbau/ai_pimc/DealSampler/sample.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)