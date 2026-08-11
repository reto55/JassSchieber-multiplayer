---
type: Python Module
title: users
resource: frontend/auth/users.py#L1-L73
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/fastapi
  - external/fastapi-users
  - external/fastapi-users-db-sqlalchemy
  - external/fastapi-users-authentication
  - external/fastapi-users-authentication-strategy-db
  - external/fastapi-users-db-sqlalchemy-access-token
  - external/sqlalchemy-ext-asyncio
  - external/frontend-auth-models
  - external/frontend-auth-manager
  - external/frontend-auth-email
  - external/frontend-auth-settings
---

# Contains

- [make_user_db_dep](../../../functions/frontend/auth/users/make_user_db_dep.md)
- [get_user_db](../../../functions/frontend/auth/users/get_user_db.md)
- [make_token_db_dep](../../../functions/frontend/auth/users/make_token_db_dep.md)
- [get_token_db](../../../functions/frontend/auth/users/get_token_db.md)
- [make_manager_dep](../../../functions/frontend/auth/users/make_manager_dep.md)
- [get_user_manager](../../../functions/frontend/auth/users/get_user_manager.md)
- [make_auth_backend](../../../functions/frontend/auth/users/make_auth_backend.md)
- [get_strategy](../../../functions/frontend/auth/users/get_strategy.md)
- [make_fastapi_users](../../../functions/frontend/auth/users/make_fastapi_users.md)

# Imports

- `fastapi`
- `fastapi_users`
- `fastapi_users_db_sqlalchemy`
- `fastapi_users.authentication`
- `fastapi_users.authentication.strategy.db`
- `fastapi_users_db_sqlalchemy.access_token`
- `sqlalchemy.ext.asyncio`
- `frontend.auth.models`
- `frontend.auth.manager`
- `frontend.auth.email`
- `frontend.auth.settings`