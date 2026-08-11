---
type: Python Method
title: _trump_phase
resource: ausbau/game_session.py#L870-L950
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/_await_seat_action
  - functions/ausbau/game_session/GameSession/_partner_of
  called_by:
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_human_picks_eicheln
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state
---

# Signature

`async def _trump_phase(self, play: Play) -> None:`

# Calls

- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_await_seat_action](../../../../functions/ausbau/game_session/GameSession/_await_seat_action.md)
- [_partner_of](../../../../functions/ausbau/game_session/GameSession/_partner_of.md)

# Called by

- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [test_trump_phase_human_picks_eicheln](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_human_picks_eicheln.md)
- [test_trump_phase_schieben_transfers_to_partner](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner.md)
- [test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state.md)
- [test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state.md)