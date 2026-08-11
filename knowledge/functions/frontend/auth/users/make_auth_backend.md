---
type: Python Function
title: make_auth_backend
resource: frontend/auth/users.py#L49-L66
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/users/make_token_db_dep
  called_by:
  - functions/frontend/auth/users/make_fastapi_users
---

# Signature

`def make_auth_backend(get_session, secure: bool) -> AuthenticationBackend:`

# Calls

- [make_token_db_dep](../../../../functions/frontend/auth/users/make_token_db_dep.md)

# Called by

- [make_fastapi_users](../../../../functions/frontend/auth/users/make_fastapi_users.md)