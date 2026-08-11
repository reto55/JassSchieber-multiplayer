---
type: Python Function
title: principal_id
resource: ausbau/room.py#L31-L36
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/game_session/GameSession/_seat_for_principal
  - functions/ausbau/game_session/GameSession/_spectator_for_principal
  - functions/ausbau/game_session/GameSession/_seat_to_dict
  - functions/ausbau/game_session/GameSession/_transfer_host
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  - functions/ausbau/game_session/GameSession/_has_connected_host
  - functions/ausbau/room/create_room
  - functions/ausbau/room/find_rooms_for_principal
  - functions/ausbau/server/_seat_to_dict
  - functions/ausbau/server/_seat_for_principal
  - functions/ausbau/server/_spectator_for_principal
  - functions/ausbau/server/leave_endpoint
  - functions/ausbau/server/start_room_endpoint
  - functions/ausbau/server/seat_swap_endpoint
  - functions/ausbau/server/ai_difficulty_endpoint
  - functions/ausbau/server/target_score_endpoint
  - functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human
  - functions/tests/multiplayer/test_host_transfer/test_reclaim_into_room_with_connected_host_does_not_promote
  - functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_transfers_host
  - functions/tests/multiplayer/test_host_transfer/test_kick_self_treated_as_leave_transfers_host
  - functions/tests/multiplayer/test_room_model/test_principal_id_for_guest
  - functions/tests/multiplayer/test_room_model/test_create_room_assigns_host_to_seat_0
---

# Signature

`def principal_id(p) -> str:`

# Called by

- [_seat_for_principal](../../../functions/ausbau/game_session/GameSession/_seat_for_principal.md)
- [_spectator_for_principal](../../../functions/ausbau/game_session/GameSession/_spectator_for_principal.md)
- [_seat_to_dict](../../../functions/ausbau/game_session/GameSession/_seat_to_dict.md)
- [_transfer_host](../../../functions/ausbau/game_session/GameSession/_transfer_host.md)
- [_disconnect_seat](../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reconnect_timeout](../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [_has_connected_host](../../../functions/ausbau/game_session/GameSession/_has_connected_host.md)
- [create_room](../../../functions/ausbau/room/create_room.md)
- [find_rooms_for_principal](../../../functions/ausbau/room/find_rooms_for_principal.md)
- [_seat_to_dict](../../../functions/ausbau/server/_seat_to_dict.md)
- [_seat_for_principal](../../../functions/ausbau/server/_seat_for_principal.md)
- [_spectator_for_principal](../../../functions/ausbau/server/_spectator_for_principal.md)
- [leave_endpoint](../../../functions/ausbau/server/leave_endpoint.md)
- [start_room_endpoint](../../../functions/ausbau/server/start_room_endpoint.md)
- [seat_swap_endpoint](../../../functions/ausbau/server/seat_swap_endpoint.md)
- [ai_difficulty_endpoint](../../../functions/ausbau/server/ai_difficulty_endpoint.md)
- [target_score_endpoint](../../../functions/ausbau/server/target_score_endpoint.md)
- [test_reclaim_into_hostless_room_promotes_reconnecting_human](../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human.md)
- [test_reclaim_into_room_with_connected_host_does_not_promote](../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_room_with_connected_host_does_not_promote.md)
- [test_host_leave_in_lobby_transfers_host](../../../functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_transfers_host.md)
- [test_kick_self_treated_as_leave_transfers_host](../../../functions/tests/multiplayer/test_host_transfer/test_kick_self_treated_as_leave_transfers_host.md)
- [test_principal_id_for_guest](../../../functions/tests/multiplayer/test_room_model/test_principal_id_for_guest.md)
- [test_create_room_assigns_host_to_seat_0](../../../functions/tests/multiplayer/test_room_model/test_create_room_assigns_host_to_seat_0.md)