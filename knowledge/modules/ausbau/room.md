---
type: Python Module
title: room
resource: ausbau/room.py#L1-L222
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/logging
  - external/os
  - external/secrets
  - external/time
  - external/dataclasses
  - external/typing
  - external/frontend-auth-guest
  - external/frontend-auth-models
  - external/ausbau-game-session
  - external/ausbau-ai-strategies
  - external/ausbau-room-as-self
---

# Contains

- [principal_id](../../functions/ausbau/room/principal_id.md)
- [Variant](../../classes/ausbau/room/Variant.md)
- [Seat](../../classes/ausbau/room/Seat.md)
- [display_name](../../functions/ausbau/room/Seat/display_name.md)
- [Spectator](../../classes/ausbau/room/Spectator.md)
- [make_code](../../functions/ausbau/room/make_code.md)
- [create_room](../../functions/ausbau/room/create_room.md)
- [get_room](../../functions/ausbau/room/get_room.md)
- [remove_room](../../functions/ausbau/room/remove_room.md)
- [_close_room](../../functions/ausbau/room/_close_room.md)
- [reap_rooms_once](../../functions/ausbau/room/reap_rooms_once.md)
- [reaper_loop](../../functions/ausbau/room/reaper_loop.md)
- [find_rooms_for_principal](../../functions/ausbau/room/find_rooms_for_principal.md)

# Imports

- `asyncio`
- `logging`
- `os`
- `secrets`
- `time`
- `dataclasses`
- `typing`
- `frontend.auth.guest`
- `frontend.auth.models`
- `ausbau.game_session`
- `ausbau.ai_strategies`
- `ausbau.room as _self`