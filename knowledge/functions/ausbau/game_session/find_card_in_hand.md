---
type: Python Function
title: find_card_in_hand
resource: ausbau/game_session.py#L39-L45
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/card_to_code
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/pick_card
  - functions/ausbau/game_session/ai_select_card
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/test_game_session/test_find_card_in_hand_found
  - functions/tests/test_game_session/test_find_card_in_hand_not_found
---

# Signature

`def find_card_in_hand(code: str, hand: dict):`

# Calls

- [card_to_code](../../../functions/ausbau/game_session/card_to_code.md)

# Called by

- [pick_card](../../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)
- [ai_select_card](../../../functions/ausbau/game_session/ai_select_card.md)
- [_play_trick](../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [test_find_card_in_hand_found](../../../functions/tests/test_game_session/test_find_card_in_hand_found.md)
- [test_find_card_in_hand_not_found](../../../functions/tests/test_game_session/test_find_card_in_hand_not_found.md)