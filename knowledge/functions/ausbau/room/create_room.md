---
type: Python Function
title: create_room
resource: ausbau/room.py#L86-L103
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/make_code
  - functions/ausbau/room/principal_id
  - functions/ausbau/ai_strategies/make_strategy
  called_by:
  - functions/ausbau/server/create_room_endpoint
  - functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_human_join_clears_strategy_keeps_difficulty
  - functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_lobby_leave_rebuilds_strategy_from_preserved_difficulty
  - functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_mid_game_ai_takeover_resets_difficulty_to_medium
  - functions/tests/multiplayer/test_conftest_smoke/test_rooms_isolated_per_test
  - functions/tests/multiplayer/test_room_model/test_create_room_assigns_host_to_seat_0
  - functions/tests/multiplayer/test_room_model/test_remove_room
  - functions/tests/multiplayer/test_room_model/test_create_room_assigns_medium_strategy_to_ai_seats
  - functions/tests/multiplayer/test_ws_attach/test_seat_for_principal_for_seat_owner
---

# Signature

`def create_room(*, host, variant: Variant):`

# Calls

- [make_code](../../../functions/ausbau/room/make_code.md)
- [principal_id](../../../functions/ausbau/room/principal_id.md)
- [make_strategy](../../../functions/ausbau/ai_strategies/make_strategy.md)

# Called by

- [create_room_endpoint](../../../functions/ausbau/server/create_room_endpoint.md)
- [test_human_join_clears_strategy_keeps_difficulty](../../../functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_human_join_clears_strategy_keeps_difficulty.md)
- [test_lobby_leave_rebuilds_strategy_from_preserved_difficulty](../../../functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_lobby_leave_rebuilds_strategy_from_preserved_difficulty.md)
- [test_mid_game_ai_takeover_resets_difficulty_to_medium](../../../functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_mid_game_ai_takeover_resets_difficulty_to_medium.md)
- [test_rooms_isolated_per_test](../../../functions/tests/multiplayer/test_conftest_smoke/test_rooms_isolated_per_test.md)
- [test_create_room_assigns_host_to_seat_0](../../../functions/tests/multiplayer/test_room_model/test_create_room_assigns_host_to_seat_0.md)
- [test_remove_room](../../../functions/tests/multiplayer/test_room_model/test_remove_room.md)
- [test_create_room_assigns_medium_strategy_to_ai_seats](../../../functions/tests/multiplayer/test_room_model/test_create_room_assigns_medium_strategy_to_ai_seats.md)
- [test_seat_for_principal_for_seat_owner](../../../functions/tests/multiplayer/test_ws_attach/test_seat_for_principal_for_seat_owner.md)