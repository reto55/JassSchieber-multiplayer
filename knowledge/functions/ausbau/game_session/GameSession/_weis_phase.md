---
type: Python Method
title: _weis_phase
resource: ausbau/game_session.py#L1013-L1148
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/describe_weis
  - functions/Cards_refactored/wiis
  - functions/Cards_refactored/wiis_gleiche
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_await_seat_action
  - functions/ausbau/game_session/GameSession/broadcast
  called_by:
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/tests/multiplayer/test_weis_phase/test_weis_request_per_seat_only_own_weis
  - functions/tests/multiplayer/test_weis_phase/test_weis_resolution_broadcasts_to_all
  - functions/tests/multiplayer/test_weis_phase/test_weis_decline
  - functions/tests/multiplayer/test_weis_phase/test_weis_request_not_sent_to_spectator
  - functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts
  - functions/tests/multiplayer/test_weis_phase/test_weis_no_cross_seat_leak
---

# Signature

`async def _weis_phase(self, play: Play) -> None:`

# Calls

- [describe_weis](../../../../functions/ausbau/game_session/describe_weis.md)
- [wiis](../../../../functions/Cards_refactored/wiis.md)
- [wiis_gleiche](../../../../functions/Cards_refactored/wiis_gleiche.md)
- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_await_seat_action](../../../../functions/ausbau/game_session/GameSession/_await_seat_action.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)

# Called by

- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [test_weis_request_per_seat_only_own_weis](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_per_seat_only_own_weis.md)
- [test_weis_resolution_broadcasts_to_all](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_resolution_broadcasts_to_all.md)
- [test_weis_decline](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_decline.md)
- [test_weis_request_not_sent_to_spectator](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_not_sent_to_spectator.md)
- [test_weis_phase_rejects_wrong_type_then_re_prompts](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts.md)
- [test_weis_no_cross_seat_leak](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_no_cross_seat_leak.md)