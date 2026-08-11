---
type: Python Function
title: _build_auth_app
resource: ausbau/server.py#L69-L94
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/server/_ensure_auth_initialised
  - functions/frontend/auth/app/build_app
  called_by:
  - functions/ausbau/server/_lifespan
---

# Signature

`def _build_auth_app():`

# Calls

- [_ensure_auth_initialised](../../../functions/ausbau/server/_ensure_auth_initialised.md)
- [build_app](../../../functions/frontend/auth/app/build_app.md)

# Called by

- [_lifespan](../../../functions/ausbau/server/_lifespan.md)