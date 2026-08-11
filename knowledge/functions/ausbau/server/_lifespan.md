---
type: Python Function
title: _lifespan
resource: ausbau/server.py#L27-L41
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/server/_ensure_auth_initialised
  - functions/ausbau/server/_build_auth_app
  - functions/frontend/auth/db/init_db
  - functions/ausbau/room/reaper_loop
---

# Signature

`async def _lifespan(app: FastAPI): # Mount auth routes and create auth.db tables on first launch. Done here # (not at module load) so that importing ausbau.server during tests does # not require real auth env vars to be set.`

# Calls

- [_ensure_auth_initialised](../../../functions/ausbau/server/_ensure_auth_initialised.md)
- [_build_auth_app](../../../functions/ausbau/server/_build_auth_app.md)
- [init_db](../../../functions/frontend/auth/db/init_db.md)
- [reaper_loop](../../../functions/ausbau/room/reaper_loop.md)