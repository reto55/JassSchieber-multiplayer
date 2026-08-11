---
type: Python Function
title: determine_trick_winner
resource: ausbau/game_session.py#L170-L195
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/strength
  called_by:
  - functions/ausbau/ai_pimc/rollout
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/test_game_session/test_trick_winner_trump_beats_lead
  - functions/tests/test_game_session/test_trick_winner_highest_lead_suit_wins
---

# Signature

`def determine_trick_winner(trick: dict, first: str, operator: str, folger: dict) -> str:`

# Calls

- [strength](../../../functions/ausbau/game_session/strength.md)

# Called by

- [rollout](../../../functions/ausbau/ai_pimc/rollout.md)
- [_play_trick](../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [test_trick_winner_trump_beats_lead](../../../functions/tests/test_game_session/test_trick_winner_trump_beats_lead.md)
- [test_trick_winner_highest_lead_suit_wins](../../../functions/tests/test_game_session/test_trick_winner_highest_lead_suit_wins.md)