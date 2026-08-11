---
type: Python Module
title: app
resource: frontend/auth/app.py#L1-L486
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/secrets
  - external/uuid-as-uuid
  - external/datetime
  - external/pathlib
  - external/types
  - external/fastapi
  - external/fastapi-responses
  - external/fastapi-templating
  - external/fastapi-users
  - external/slowapi-errors
  - external/slowapi-middleware
  - external/sqlalchemy
  - external/sqlalchemy-ext-asyncio
  - external/passlib-context
  - external/frontend-auth-users
  - external/frontend-auth-schemas
  - external/frontend-auth-email
  - external/frontend-auth-settings
  - external/frontend-auth-models
  - external/frontend-auth-tombstone
  - external/frontend-auth-lockout
  - external/frontend-auth-deps
  - external/frontend-auth-passwords
  - external/frontend-auth-ratelimit
  - external/frontend-auth-admin
  - external/frontend-auth-guest
---

# Contains

- [build_app](../../../functions/frontend/auth/app/build_app.md)
- [_rate_limit_handler](../../../functions/frontend/auth/app/_rate_limit_handler.md)
- [register](../../../functions/frontend/auth/app/register.md)
- [login](../../../functions/frontend/auth/app/login.md)
- [logout](../../../functions/frontend/auth/app/logout.md)
- [me](../../../functions/frontend/auth/app/me.md)
- [whoami](../../../functions/frontend/auth/app/whoami.md)
- [export_account](../../../functions/frontend/auth/app/export_account.md)
- [verify](../../../functions/frontend/auth/app/verify.md)
- [resend_verification](../../../functions/frontend/auth/app/resend_verification.md)
- [forgot](../../../functions/frontend/auth/app/forgot.md)
- [reset](../../../functions/frontend/auth/app/reset.md)
- [change_password](../../../functions/frontend/auth/app/change_password.md)
- [change_email](../../../functions/frontend/auth/app/change_email.md)
- [confirm_email](../../../functions/frontend/auth/app/confirm_email.md)
- [delete_account](../../../functions/frontend/auth/app/delete_account.md)
- [_page](../../../functions/frontend/auth/app/_page.md)

# Imports

- `secrets`
- `uuid as _uuid`
- `datetime`
- `pathlib`
- `types`
- `fastapi`
- `fastapi.responses`
- `fastapi.templating`
- `fastapi_users`
- `slowapi.errors`
- `slowapi.middleware`
- `sqlalchemy`
- `sqlalchemy.ext.asyncio`
- `passlib.context`
- `frontend.auth.users`
- `frontend.auth.schemas`
- `frontend.auth.email`
- `frontend.auth.settings`
- `frontend.auth.models`
- `frontend.auth.tombstone`
- `frontend.auth.lockout`
- `frontend.auth.deps`
- `frontend.auth.passwords`
- `frontend.auth.ratelimit`
- `frontend.auth.admin`
- `frontend.auth.guest`