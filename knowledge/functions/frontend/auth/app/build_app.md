---
type: Python Function
title: build_app
resource: frontend/auth/app.py#L40-L486
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/ratelimit/make_limiter
  - functions/frontend/auth/users/make_fastapi_users
  - functions/frontend/auth/users/make_manager_dep
  - functions/frontend/auth/deps/make_current_user_dep
  - functions/frontend/auth/deps/make_require_admin_dep
  - functions/frontend/auth/admin/make_admin_router
  called_by:
  - functions/ausbau/server/_build_auth_app
  - functions/tests/auth/conftest/app
---

# Signature

`def build_app(*, get_session, settings: Settings, mail: MailBackend) -> FastAPI:`

# Calls

- [make_limiter](../../../../functions/frontend/auth/ratelimit/make_limiter.md)
- [make_fastapi_users](../../../../functions/frontend/auth/users/make_fastapi_users.md)
- [make_manager_dep](../../../../functions/frontend/auth/users/make_manager_dep.md)
- [make_current_user_dep](../../../../functions/frontend/auth/deps/make_current_user_dep.md)
- [make_require_admin_dep](../../../../functions/frontend/auth/deps/make_require_admin_dep.md)
- [make_admin_router](../../../../functions/frontend/auth/admin/make_admin_router.md)

# Called by

- [_build_auth_app](../../../../functions/ausbau/server/_build_auth_app.md)
- [app](../../../../functions/tests/auth/conftest/app.md)