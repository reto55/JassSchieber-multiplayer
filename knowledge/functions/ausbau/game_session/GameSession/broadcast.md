---
type: Python Method
title: broadcast
resource: ausbau/game_session.py#L463-L473
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/tests/multiplayer/conftest/FakeWebSocket/send_json
  called_by:
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/game_session/GameSession/_commit_pending_swap
  - functions/ausbau/game_session/GameSession/_trump_phase
  - functions/ausbau/game_session/GameSession/_weis_phase
  - functions/ausbau/game_session/GameSession/_play_trick
  - functions/ausbau/game_session/GameSession/_run_spiel
  - functions/ausbau/game_session/GameSession/start_game
  - functions/ausbau/server/join_endpoint
  - functions/ausbau/server/leave_endpoint
  - functions/ausbau/server/spectate_endpoint
  - functions/ausbau/server/leave_spectator_endpoint
  - functions/ausbau/server/ai_difficulty_endpoint
  - functions/ausbau/server/target_score_endpoint
  - functions/ausbau/server/websocket_endpoint
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_all_seats
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_except_seat
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_spectators
---

# Signature

`async def broadcast(self, msg: dict, *, except_seat: str | None = None) -> None:`

# Calls

- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [send_json](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/send_json.md)

# Called by

- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reconnect_timeout](../../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [_commit_pending_swap](../../../../functions/ausbau/game_session/GameSession/_commit_pending_swap.md)
- [_trump_phase](../../../../functions/ausbau/game_session/GameSession/_trump_phase.md)
- [_weis_phase](../../../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [_play_trick](../../../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [_run_spiel](../../../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [start_game](../../../../functions/ausbau/game_session/GameSession/start_game.md)
- [join_endpoint](../../../../functions/ausbau/server/join_endpoint.md)
- [leave_endpoint](../../../../functions/ausbau/server/leave_endpoint.md)
- [spectate_endpoint](../../../../functions/ausbau/server/spectate_endpoint.md)
- [leave_spectator_endpoint](../../../../functions/ausbau/server/leave_spectator_endpoint.md)
- [ai_difficulty_endpoint](../../../../functions/ausbau/server/ai_difficulty_endpoint.md)
- [target_score_endpoint](../../../../functions/ausbau/server/target_score_endpoint.md)
- [websocket_endpoint](../../../../functions/ausbau/server/websocket_endpoint.md)
- [test_broadcast_to_all_seats](../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_all_seats.md)
- [test_broadcast_except_seat](../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_except_seat.md)
- [test_broadcast_to_spectators](../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_spectators.md)