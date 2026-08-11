---
type: Python Method
title: _room_resume_message_for
resource: ausbau/game_session.py#L802-L850
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/hand_to_codes
  called_by:
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/server/websocket_endpoint
  - functions/tests/multiplayer/test_reclaim/test_room_resume_for_spectator_has_null_your_position
  - functions/tests/multiplayer/test_reclaim/test_room_resume_for_seat_includes_hand
  - functions/tests/multiplayer/test_reclaim/test_room_resume_includes_replay_buffer
  - functions/tests/multiplayer/test_reclaim/test_room_resume_your_turn_true_when_seat_matches_current_turn
---

# Signature

`def _room_resume_message_for(self, position):`

# Calls

- [hand_to_codes](../../../../functions/ausbau/game_session/hand_to_codes.md)

# Called by

- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [websocket_endpoint](../../../../functions/ausbau/server/websocket_endpoint.md)
- [test_room_resume_for_spectator_has_null_your_position](../../../../functions/tests/multiplayer/test_reclaim/test_room_resume_for_spectator_has_null_your_position.md)
- [test_room_resume_for_seat_includes_hand](../../../../functions/tests/multiplayer/test_reclaim/test_room_resume_for_seat_includes_hand.md)
- [test_room_resume_includes_replay_buffer](../../../../functions/tests/multiplayer/test_reclaim/test_room_resume_includes_replay_buffer.md)
- [test_room_resume_your_turn_true_when_seat_matches_current_turn](../../../../functions/tests/multiplayer/test_reclaim/test_room_resume_your_turn_true_when_seat_matches_current_turn.md)