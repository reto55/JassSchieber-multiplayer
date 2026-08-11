---
type: Python Method
title: _reconnect_timeout
resource: ausbau/game_session.py#L547-L586
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/GameSession/_seat
  - functions/ausbau/room/principal_id
  - functions/ausbau/ai_strategies/make_strategy
  - functions/ausbau/game_session/GameSession/broadcast
  - functions/ausbau/game_session/GameSession/_transfer_host
  - functions/ausbau/game_session/GameSession/_update_idle_since
  called_by:
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_mid_game_ai_takeover_resets_difficulty_to_medium
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned
---

# Signature

`async def _reconnect_timeout(self, position: str) -> None:`

# Calls

- [_seat](../../../../functions/ausbau/game_session/GameSession/_seat.md)
- [principal_id](../../../../functions/ausbau/room/principal_id.md)
- [make_strategy](../../../../functions/ausbau/ai_strategies/make_strategy.md)
- [broadcast](../../../../functions/ausbau/game_session/GameSession/broadcast.md)
- [_transfer_host](../../../../functions/ausbau/game_session/GameSession/_transfer_host.md)
- [_update_idle_since](../../../../functions/ausbau/game_session/GameSession/_update_idle_since.md)

# Called by

- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [test_mid_game_ai_takeover_resets_difficulty_to_medium](../../../../functions/tests/multiplayer/test_ai_difficulty_lifecycle/test_mid_game_ai_takeover_resets_difficulty_to_medium.md)
- [test_reconnect_timeout_flips_to_ai](../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai.md)
- [test_reconnect_timeout_no_op_if_websocket_returned](../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned.md)