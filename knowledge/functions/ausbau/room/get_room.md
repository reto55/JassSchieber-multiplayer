---
type: Python Function
title: get_room
resource: ausbau/room.py#L106-L107
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/server/get_room_endpoint
  - functions/ausbau/server/join_endpoint
  - functions/ausbau/server/leave_endpoint
  - functions/ausbau/server/spectate_endpoint
  - functions/ausbau/server/leave_spectator_endpoint
  - functions/ausbau/server/start_room_endpoint
  - functions/ausbau/server/seat_swap_endpoint
  - functions/ausbau/server/ai_difficulty_endpoint
  - functions/ausbau/server/target_score_endpoint
  - functions/ausbau/server/websocket_endpoint
  - functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_transfers_host
  - functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_no_other_humans_no_transfer
  - functions/tests/multiplayer/test_host_transfer/test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target
  - functions/tests/multiplayer/test_host_transfer/test_kick_mid_game_returns_400
  - functions/tests/multiplayer/test_host_transfer/test_kick_self_treated_as_leave_transfers_host
  - functions/tests/multiplayer/test_room_model/test_create_room_assigns_host_to_seat_0
  - functions/tests/multiplayer/test_room_model/test_remove_room
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_403_if_caller_not_seated
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_400_if_target_ai
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_400_if_self
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_request_path
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_accept_path
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_409_when_target_already_has_pending_request
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_403_if_caller_disconnected
  - functions/tests/multiplayer/test_start_game/test_start_happy_path_204
  - functions/tests/multiplayer/test_start_game/test_start_not_host_403
  - functions/tests/multiplayer/test_start_game/test_start_not_lobby_409
---

# Signature

`def get_room(code: str):`

# Called by

- [get_room_endpoint](../../../functions/ausbau/server/get_room_endpoint.md)
- [join_endpoint](../../../functions/ausbau/server/join_endpoint.md)
- [leave_endpoint](../../../functions/ausbau/server/leave_endpoint.md)
- [spectate_endpoint](../../../functions/ausbau/server/spectate_endpoint.md)
- [leave_spectator_endpoint](../../../functions/ausbau/server/leave_spectator_endpoint.md)
- [start_room_endpoint](../../../functions/ausbau/server/start_room_endpoint.md)
- [seat_swap_endpoint](../../../functions/ausbau/server/seat_swap_endpoint.md)
- [ai_difficulty_endpoint](../../../functions/ausbau/server/ai_difficulty_endpoint.md)
- [target_score_endpoint](../../../functions/ausbau/server/target_score_endpoint.md)
- [websocket_endpoint](../../../functions/ausbau/server/websocket_endpoint.md)
- [test_host_leave_in_lobby_transfers_host](../../../functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_transfers_host.md)
- [test_host_leave_in_lobby_no_other_humans_no_transfer](../../../functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_no_other_humans_no_transfer.md)
- [test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target](../../../functions/tests/multiplayer/test_host_transfer/test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target.md)
- [test_kick_mid_game_returns_400](../../../functions/tests/multiplayer/test_host_transfer/test_kick_mid_game_returns_400.md)
- [test_kick_self_treated_as_leave_transfers_host](../../../functions/tests/multiplayer/test_host_transfer/test_kick_self_treated_as_leave_transfers_host.md)
- [test_create_room_assigns_host_to_seat_0](../../../functions/tests/multiplayer/test_room_model/test_create_room_assigns_host_to_seat_0.md)
- [test_remove_room](../../../functions/tests/multiplayer/test_room_model/test_remove_room.md)
- [test_seat_swap_endpoint_403_if_caller_not_seated](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_403_if_caller_not_seated.md)
- [test_seat_swap_endpoint_400_if_target_ai](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_400_if_target_ai.md)
- [test_seat_swap_endpoint_400_if_self](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_400_if_self.md)
- [test_seat_swap_endpoint_happy_request_path](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_request_path.md)
- [test_seat_swap_endpoint_happy_accept_path](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_accept_path.md)
- [test_seat_swap_409_when_target_already_has_pending_request](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_409_when_target_already_has_pending_request.md)
- [test_seat_swap_endpoint_403_if_caller_disconnected](../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_403_if_caller_disconnected.md)
- [test_start_happy_path_204](../../../functions/tests/multiplayer/test_start_game/test_start_happy_path_204.md)
- [test_start_not_host_403](../../../functions/tests/multiplayer/test_start_game/test_start_not_host_403.md)
- [test_start_not_lobby_409](../../../functions/tests/multiplayer/test_start_game/test_start_not_lobby_409.md)