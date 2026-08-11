---
type: Python Function
title: make_manager_dep
resource: frontend/auth/users.py#L32-L46
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/users/make_user_db_dep
  called_by:
  - functions/frontend/auth/app/build_app
  - functions/frontend/auth/users/make_fastapi_users
---

# Signature

`def make_manager_dep(get_session, settings: Settings, mail: MailBackend):`

# Calls

- [make_user_db_dep](../../../../functions/frontend/auth/users/make_user_db_dep.md)

# Called by

- [build_app](../../../../functions/frontend/auth/app/build_app.md)
- [make_fastapi_users](../../../../functions/frontend/auth/users/make_fastapi_users.md)