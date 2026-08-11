---
type: Python Function
title: test_play_trick_appends_to_spiel_winners
resource: tests/multiplayer/test_variants.py#L153-L192
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_variants/_session
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_play_trick
---

# Signature

`async def test_play_trick_appends_to_spiel_winners():`

# Calls

- [_session](../../../../functions/tests/multiplayer/test_variants/_session.md)
- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [get_valid_cards](../../../../functions/ausbau/game_session/get_valid_cards.md)
- [card_to_code](../../../../functions/ausbau/game_session/card_to_code.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)