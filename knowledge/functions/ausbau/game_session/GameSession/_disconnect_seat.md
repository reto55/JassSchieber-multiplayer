---
type: Python Method
title: _disconnect_seat
resource: ausbau/game_session.py#L487-L545
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/room/principal_id
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/_transfer_host
  - functions/ausbau/game_session/GameSession/_update_idle_since
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  called_by:
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/server/websocket_endpoint
  - functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately
  - functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_host_triggers_transfer
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused
  - functions/tests/multiplayer/test_disconnect/test_disconnect_idempotent_for_ai_or_already_disconnected
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout
  - functions/tests/multiplayer/test_disconnect/test_disconnect_state_event_set_wakes_awaiter
  - functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human
  - functions/tests/multiplayer/test_reaper/test_idle_since_set_when_last_human_leaves_lobby
  - functions/tests/multiplayer/test_reaper/test_idle_since_not_set_when_other_humans_remain
  - functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task
---

# Signature

`async def _disconnect_seat(self, position: str) -> None:`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [principal_id](../../../../functions/ausbau/room/principal_id.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_transfer_host](../../../../functions/ausbau/game_session/GameSession/_transfer_host.md)
- [_update_idle_since](../../../../functions/ausbau/game_session/GameSession/_update_idle_since.md)
- [_reconnect_timeout](../../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)

# Called by

- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [websocket_endpoint](../../../../functions/ausbau/server/websocket_endpoint.md)
- [test_disconnect_in_lobby_drops_to_ai_immediately](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately.md)
- [test_disconnect_in_lobby_host_triggers_transfer](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_host_triggers_transfer.md)
- [test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused.md)
- [test_disconnect_idempotent_for_ai_or_already_disconnected](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_idempotent_for_ai_or_already_disconnected.md)
- [test_disconnect_mid_game_host_triggers_transfer_after_timeout](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout.md)
- [test_disconnect_state_event_set_wakes_awaiter](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_state_event_set_wakes_awaiter.md)
- [test_reclaim_into_hostless_room_promotes_reconnecting_human](../../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human.md)
- [test_idle_since_set_when_last_human_leaves_lobby](../../../../functions/tests/multiplayer/test_reaper/test_idle_since_set_when_last_human_leaves_lobby.md)
- [test_idle_since_not_set_when_other_humans_remain](../../../../functions/tests/multiplayer/test_reaper/test_idle_since_not_set_when_other_humans_remain.md)
- [test_reclaim_seat_cancels_pending_reconnect_task](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task.md)