---
type: Python Method
title: _run_spiel
resource: ausbau/game_session.py#L1455-L1547
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_reset_spiel_trick_winners
  - functions/ausbau/game_session/GameSession/broadcast_per_seat
  - functions/ausbau/game_session/GameSession/_trump_phase
  - functions/ausbau/game_session/GameSession/_apply_stoeck
  - functions/ausbau/game_session/GameSession/_weis_phase
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/ausbau/game_session/_mode_multiplier
  - functions/ausbau/game_session/GameSession/_apply_match_bonus
  - functions/ausbau/game_session/GameSession/broadcast
  called_by:
  - functions/ausbau/game_session/GameSession/start_game
---

# Signature

`async def _run_spiel(self, spiel_num: int) -> None:`

# Calls

- [_reset_spiel_trick_winners](../../../../functions/ausbau/game_session/GameSession/_reset_spiel_trick_winners.md)
- [broadcast_per_seat](../../../../functions/ausbau/game_session/GameSession/broadcast_per_seat.md)
- [_trump_phase](../../../../functions/ausbau/game_session/GameSession/_trump_phase.md)
- [_apply_stoeck](../../../../functions/ausbau/game_session/GameSession/_apply_stoeck.md)
- [_weis_phase](../../../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [_mode_multiplier](../../../../functions/ausbau/game_session/_mode_multiplier.md)
- [_apply_match_bonus](../../../../functions/ausbau/game_session/GameSession/_apply_match_bonus.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)

# Called by

- [start_game](../../../../functions/ausbau/game_session/GameSession/start_game.md)