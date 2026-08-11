---
type: Python Module
title: test_reclaim
resource: tests/multiplayer/test_reclaim.py#L1-L369
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/pytest
  - external/cards-refactored
  - external/ausbau-game-session
  - external/ausbau-room
  - external/frontend-auth-guest
  - external/tests-multiplayer-conftest
---

# Contains

- [_fresh_session](../../../functions/tests/multiplayer/test_reclaim/_fresh_session.md)
- [test_reclaim_seat_cancels_pending_reconnect_task](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task.md)
- [test_reclaim_seat_after_ai_takeover_restores_human](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_after_ai_takeover_restores_human.md)
- [test_reclaim_sends_room_resume](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume.md)
- [test_reclaim_broadcasts_seat_reclaimed_to_others](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others.md)
- [test_reclaim_state_event_set](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_state_event_set.md)
- [test_room_resume_for_spectator_has_null_your_position](../../../functions/tests/multiplayer/test_reclaim/test_room_resume_for_spectator_has_null_your_position.md)
- [test_room_resume_for_seat_includes_hand](../../../functions/tests/multiplayer/test_reclaim/test_room_resume_for_seat_includes_hand.md)
- [test_room_resume_includes_replay_buffer](../../../functions/tests/multiplayer/test_reclaim/test_room_resume_includes_replay_buffer.md)
- [test_room_resume_your_turn_true_when_seat_matches_current_turn](../../../functions/tests/multiplayer/test_reclaim/test_room_resume_your_turn_true_when_seat_matches_current_turn.md)
- [test_reclaim_mid_turn_resends_play_request](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request.md)
- [test_reclaim_mid_turn_no_play_request_when_not_active_seat](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat.md)
- [test_reclaim_mid_turn_lead_suit_none_when_leading](../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading.md)

# Imports

- `asyncio`
- `pytest`
- `Cards_refactored`
- `ausbau.game_session`
- `ausbau.room`
- `frontend.auth.guest`
- `tests.multiplayer.conftest`