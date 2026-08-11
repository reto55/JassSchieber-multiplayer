---
type: Python Module
title: manager
resource: frontend/auth/manager.py#L1-L108
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/datetime
  - external/typing
  - external/secrets
  - external/fastapi
  - external/fastapi-users
  - external/sqlalchemy-ext-asyncio
  - external/sqlalchemy
  - external/frontend-auth-models
  - external/frontend-auth-passwords
  - external/frontend-auth-tombstone
  - external/frontend-auth-email
  - external/frontend-auth-settings
---

# Contains

- [UserManager](../../../classes/frontend/auth/manager/UserManager.md)
- [parse_id](../../../functions/frontend/auth/manager/UserManager/parse_id.md)
- [validate_password](../../../functions/frontend/auth/manager/UserManager/validate_password.md)
- [create](../../../functions/frontend/auth/manager/UserManager/create.md)
- [on_after_register](../../../functions/frontend/auth/manager/UserManager/on_after_register.md)
- [on_after_forgot_password](../../../functions/frontend/auth/manager/UserManager/on_after_forgot_password.md)

# Imports

- `datetime`
- `typing`
- `secrets`
- `fastapi`
- `fastapi_users`
- `sqlalchemy.ext.asyncio`
- `sqlalchemy`
- `frontend.auth.models`
- `frontend.auth.passwords`
- `frontend.auth.tombstone`
- `frontend.auth.email`
- `frontend.auth.settings`