---
type: Python Function
title: _ensure_auth_initialised
resource: ausbau/server.py#L61-L66
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/settings/load_settings
  - functions/frontend/auth/db/make_engine
  - functions/frontend/auth/db/make_session_factory
  called_by:
  - functions/ausbau/server/_lifespan
  - functions/ausbau/server/_build_auth_app
  - functions/ausbau/server/_get_principal
  - functions/ausbau/server/websocket_endpoint
---

# Signature

`def _ensure_auth_initialised():`

# Calls

- [load_settings](../../../functions/frontend/auth/settings/load_settings.md)
- [make_engine](../../../functions/frontend/auth/db/make_engine.md)
- [make_session_factory](../../../functions/frontend/auth/db/make_session_factory.md)

# Called by

- [_lifespan](../../../functions/ausbau/server/_lifespan.md)
- [_build_auth_app](../../../functions/ausbau/server/_build_auth_app.md)
- [_get_principal](../../../functions/ausbau/server/_get_principal.md)
- [websocket_endpoint](../../../functions/ausbau/server/websocket_endpoint.md)