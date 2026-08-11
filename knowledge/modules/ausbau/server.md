---
type: Python Module
title: server
resource: ausbau/server.py#L1-L859
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/sys
  - external/os
  - external/asyncio
  - external/secrets
  - external/contextlib
  - external/datetime
  - external/fastapi
  - external/fastapi-staticfiles
  - external/fastapi-responses
  - external/fastapi-middleware-cors
  - external/typing
  - external/slowapi-errors
  - external/sqlalchemy-ext-asyncio
  - external/sqlalchemy
  - external/frontend-auth-guest
  - external/frontend-auth-models
  - external/frontend-auth-db
  - external/frontend-auth-settings
  - external/frontend-auth-app
  - external/frontend-auth-email
  - external/ausbau-game-session
  - external/uvicorn-middleware-proxy-headers
  - external/ausbau-room
  - external/ausbau-ai-strategies
  - external/sys-as-sys
---

# Contains

- [_lifespan](../../functions/ausbau/server/_lifespan.md)
- [_ensure_auth_initialised](../../functions/ausbau/server/_ensure_auth_initialised.md)
- [_build_auth_app](../../functions/ausbau/server/_build_auth_app.md)
- [get_session](../../functions/ausbau/server/get_session.md)
- [index](../../functions/ausbau/server/index.md)
- [lobby_page](../../functions/ausbau/server/lobby_page.md)
- [home_page](../../functions/ausbau/server/home_page.md)
- [_rate_limit_handler](../../functions/ausbau/server/_rate_limit_handler.md)
- [_get_principal](../../functions/ausbau/server/_get_principal.md)
- [_seat_to_dict](../../functions/ausbau/server/_seat_to_dict.md)
- [_room_state_dict](../../functions/ausbau/server/_room_state_dict.md)
- [create_room_endpoint](../../functions/ausbau/server/create_room_endpoint.md)
- [rooms_mine_endpoint](../../functions/ausbau/server/rooms_mine_endpoint.md)
- [get_room_endpoint](../../functions/ausbau/server/get_room_endpoint.md)
- [_seat_for_principal](../../functions/ausbau/server/_seat_for_principal.md)
- [_spectator_for_principal](../../functions/ausbau/server/_spectator_for_principal.md)
- [join_endpoint](../../functions/ausbau/server/join_endpoint.md)
- [leave_endpoint](../../functions/ausbau/server/leave_endpoint.md)
- [spectate_endpoint](../../functions/ausbau/server/spectate_endpoint.md)
- [leave_spectator_endpoint](../../functions/ausbau/server/leave_spectator_endpoint.md)
- [start_room_endpoint](../../functions/ausbau/server/start_room_endpoint.md)
- [seat_swap_endpoint](../../functions/ausbau/server/seat_swap_endpoint.md)
- [ai_difficulty_endpoint](../../functions/ausbau/server/ai_difficulty_endpoint.md)
- [target_score_endpoint](../../functions/ausbau/server/target_score_endpoint.md)
- [websocket_endpoint](../../functions/ausbau/server/websocket_endpoint.md)

# Imports

- `sys`
- `os`
- `asyncio`
- `secrets`
- `contextlib`
- `datetime`
- `fastapi`
- `fastapi.staticfiles`
- `fastapi.responses`
- `fastapi.middleware.cors`
- `typing`
- `slowapi.errors`
- `sqlalchemy.ext.asyncio`
- `sqlalchemy`
- `frontend.auth.guest`
- `frontend.auth.models`
- `frontend.auth.db`
- `frontend.auth.settings`
- `frontend.auth.app`
- `frontend.auth.email`
- `ausbau.game_session`
- `uvicorn.middleware.proxy_headers`
- `ausbau.room`
- `ausbau.ai_strategies`
- `sys as _sys`