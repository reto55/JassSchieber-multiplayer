---
type: Python Module
title: deps
resource: frontend/auth/deps.py#L1-L89
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/datetime
  - external/fastapi
  - external/sqlalchemy
  - external/sqlalchemy-ext-asyncio
  - external/frontend-auth-models
  - external/frontend-auth-guest
---

# Contains

- [make_current_user_dep](../../../functions/frontend/auth/deps/make_current_user_dep.md)
- [current_user](../../../functions/frontend/auth/deps/current_user.md)
- [make_require_admin_dep](../../../functions/frontend/auth/deps/make_require_admin_dep.md)
- [require_admin](../../../functions/frontend/auth/deps/require_admin.md)
- [make_current_principal_dep](../../../functions/frontend/auth/deps/make_current_principal_dep.md)
- [current_principal](../../../functions/frontend/auth/deps/current_principal.md)

# Imports

- `datetime`
- `fastapi`
- `sqlalchemy`
- `sqlalchemy.ext.asyncio`
- `frontend.auth.models`
- `frontend.auth.guest`