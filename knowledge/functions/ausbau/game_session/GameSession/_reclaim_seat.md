---
type: Python Method
title: _reclaim_seat
resource: ausbau/game_session.py#L588-L648
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/send_json
  - functions/ausbau/game_session/GameSession/_room_resume_message_for
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/_lead_suit_from_trick_so_far
  - functions/ausbau/game_session/get_valid_cards
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/game_session/GameSession/_update_idle_since
  - functions/ausbau/game_session/GameSession/_has_connected_host
  - functions/ausbau/game_session/GameSession/_transfer_host
  called_by:
  - functions/ausbau/server/websocket_endpoint
  - functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human
  - functions/tests/multiplayer/test_host_transfer/test_reclaim_into_room_with_connected_host_does_not_promote
  - functions/tests/multiplayer/test_reaper/test_idle_since_cleared_when_human_reclaims
  - functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task
  - functions/tests/multiplayer/test_reclaim/test_reclaim_seat_after_ai_takeover_restores_human
  - functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume
  - functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others
  - functions/tests/multiplayer/test_reclaim/test_reclaim_state_event_set
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading
---

# Signature

`async def _reclaim_seat(self, position: str, websocket, principal) -> None:`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [send_json](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/send_json.md)
- [_room_resume_message_for](../../../../functions/ausbau/game_session/GameSession/_room_resume_message_for.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_lead_suit_from_trick_so_far](../../../../functions/ausbau/game_session/GameSession/_lead_suit_from_trick_so_far.md)
- [get_valid_cards](../../../../functions/ausbau/game_session/get_valid_cards.md)
- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [_update_idle_since](../../../../functions/ausbau/game_session/GameSession/_update_idle_since.md)
- [_has_connected_host](../../../../functions/ausbau/game_session/GameSession/_has_connected_host.md)
- [_transfer_host](../../../../functions/ausbau/game_session/GameSession/_transfer_host.md)

# Called by

- [websocket_endpoint](../../../../functions/ausbau/server/websocket_endpoint.md)
- [test_reclaim_into_hostless_room_promotes_reconnecting_human](../../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human.md)
- [test_reclaim_into_room_with_connected_host_does_not_promote](../../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_room_with_connected_host_does_not_promote.md)
- [test_idle_since_cleared_when_human_reclaims](../../../../functions/tests/multiplayer/test_reaper/test_idle_since_cleared_when_human_reclaims.md)
- [test_reclaim_seat_cancels_pending_reconnect_task](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task.md)
- [test_reclaim_seat_after_ai_takeover_restores_human](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_after_ai_takeover_restores_human.md)
- [test_reclaim_sends_room_resume](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume.md)
- [test_reclaim_broadcasts_seat_reclaimed_to_others](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others.md)
- [test_reclaim_state_event_set](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_state_event_set.md)
- [test_reclaim_mid_turn_resends_play_request](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request.md)
- [test_reclaim_mid_turn_no_play_request_when_not_active_seat](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat.md)
- [test_reclaim_mid_turn_lead_suit_none_when_leading](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading.md)