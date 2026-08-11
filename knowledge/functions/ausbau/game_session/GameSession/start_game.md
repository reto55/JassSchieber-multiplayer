---
type: Python Method
title: start_game
resource: ausbau/game_session.py#L1549-L1580
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/utils/game_utils/check_game_end
  - functions/ausbau/game_session/GameSession/broadcast
  called_by:
  - functions/ausbau/server/start_room_endpoint
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant
  - functions/tests/multiplayer/test_e2e_mixed_ai/test_e2e_mixed_difficulty_3_ai
  - functions/tests/multiplayer/test_reaper/test_finished_at_set_on_game_end
  - functions/tests/multiplayer/test_run_spiel/test_start_game_runs_to_completion_4_ai
  - functions/tests/multiplayer/test_run_spiel/test_start_game_emits_game_start_per_spiel
  - functions/tests/multiplayer/test_run_spiel/test_start_game_state_transitions
---

# Signature

`async def start_game(self) -> None:`

# Calls

- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [check_game_end](../../../../functions/utils/game_utils/check_game_end.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)

# Called by

- [start_room_endpoint](../../../../functions/ausbau/server/start_room_endpoint.md)
- [test_e2e_4_humans_full_game](../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game.md)
- [test_e2e_4_humans_trumpf_bock_variant](../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant.md)
- [test_e2e_mixed_difficulty_3_ai](../../../../functions/tests/multiplayer/test_e2e_mixed_ai/test_e2e_mixed_difficulty_3_ai.md)
- [test_finished_at_set_on_game_end](../../../../functions/tests/multiplayer/test_reaper/test_finished_at_set_on_game_end.md)
- [test_start_game_runs_to_completion_4_ai](../../../../functions/tests/multiplayer/test_run_spiel/test_start_game_runs_to_completion_4_ai.md)
- [test_start_game_emits_game_start_per_spiel](../../../../functions/tests/multiplayer/test_run_spiel/test_start_game_emits_game_start_per_spiel.md)
- [test_start_game_state_transitions](../../../../functions/tests/multiplayer/test_run_spiel/test_start_game_state_transitions.md)