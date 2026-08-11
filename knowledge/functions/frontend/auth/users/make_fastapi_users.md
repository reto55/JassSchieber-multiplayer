---
type: Python Function
title: make_fastapi_users
resource: frontend/auth/users.py#L69-L73
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/users/make_manager_dep
  - functions/frontend/auth/users/make_auth_backend
  called_by:
  - functions/frontend/auth/app/build_app
---

# Signature

`def make_fastapi_users(get_session, settings: Settings, mail: MailBackend):`

# Calls

- [make_manager_dep](../../../../functions/frontend/auth/users/make_manager_dep.md)
- [make_auth_backend](../../../../functions/frontend/auth/users/make_auth_backend.md)

# Called by

- [build_app](../../../../functions/frontend/auth/app/build_app.md)