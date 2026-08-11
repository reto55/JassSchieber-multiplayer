---
type: Python Function
title: hand_to_codes
resource: ausbau/game_session.py#L34-L36
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/card_to_code
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/on_spiel_start
  - functions/ausbau/game_session/GameSession/_room_resume_message_for
  - functions/ausbau/game_session/GameSession/_initial_state
  - functions/ausbau/game_session/GameSession/_game_start_for
  - functions/tests/multiplayer/test_ai_strategies/test_easy_pick_card_returns_valid_card
  - functions/tests/multiplayer/test_ai_strategies/test_hard_on_spiel_start_excludes_own_hand
  - functions/tests/multiplayer/test_ai_strategies/test_hard_on_card_played_skips_own_position
  - functions/tests/multiplayer/test_ai_strategies/test_hard_on_card_played_unknown_card_is_noop
  - functions/tests/multiplayer/test_reclaim/test_room_resume_for_seat_includes_hand
  - functions/tests/test_game_session/test_hand_to_codes_returns_all
---

# Signature

`def hand_to_codes(hand: dict) -> list:`

# Calls

- [card_to_code](../../../functions/ausbau/game_session/card_to_code.md)

# Called by

- [on_spiel_start](../../../functions/ausbau/ai_strategies/HardStrategy/on_spiel_start.md)
- [_room_resume_message_for](../../../functions/ausbau/game_session/GameSession/_room_resume_message_for.md)
- [_initial_state](../../../functions/ausbau/game_session/GameSession/_initial_state.md)
- [_game_start_for](../../../functions/ausbau/game_session/GameSession/_game_start_for.md)
- [test_easy_pick_card_returns_valid_card](../../../functions/tests/multiplayer/test_ai_strategies/test_easy_pick_card_returns_valid_card.md)
- [test_hard_on_spiel_start_excludes_own_hand](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_spiel_start_excludes_own_hand.md)
- [test_hard_on_card_played_skips_own_position](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_card_played_skips_own_position.md)
- [test_hard_on_card_played_unknown_card_is_noop](../../../functions/tests/multiplayer/test_ai_strategies/test_hard_on_card_played_unknown_card_is_noop.md)
- [test_room_resume_for_seat_includes_hand](../../../functions/tests/multiplayer/test_reclaim/test_room_resume_for_seat_includes_hand.md)
- [test_hand_to_codes_returns_all](../../../functions/tests/test_game_session/test_hand_to_codes_returns_all.md)