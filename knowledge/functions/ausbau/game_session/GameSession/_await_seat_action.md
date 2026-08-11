---
type: Python Method
title: _await_seat_action
resource: ausbau/game_session.py#L957-L982
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/game_session/GameSession/_compute_ai_action
  called_by:
  - functions/ausbau/game_session/GameSession/_trump_phase
  - functions/ausbau/game_session/GameSession/_weis_phase
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/tests/multiplayer/test_await_seat_action/test_await_human_returns_queued_message
  - functions/tests/multiplayer/test_await_seat_action/test_await_ai_computes_synchronously_no_queue_touched
  - functions/tests/multiplayer/test_await_seat_action/test_await_disconnected_seat_blocks_until_event_set
---

# Signature

`async def _await_seat_action(self, position: str, valid_actions: dict) -> dict:`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [_compute_ai_action](../../../../functions/ausbau/game_session/GameSession/_compute_ai_action.md)

# Called by

- [_trump_phase](../../../../functions/ausbau/game_session/GameSession/_trump_phase.md)
- [_weis_phase](../../../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [test_await_human_returns_queued_message](../../../../functions/tests/multiplayer/test_await_seat_action/test_await_human_returns_queued_message.md)
- [test_await_ai_computes_synchronously_no_queue_touched](../../../../functions/tests/multiplayer/test_await_seat_action/test_await_ai_computes_synchronously_no_queue_touched.md)
- [test_await_disconnected_seat_blocks_until_event_set](../../../../functions/tests/multiplayer/test_await_seat_action/test_await_disconnected_seat_blocks_until_event_set.md)