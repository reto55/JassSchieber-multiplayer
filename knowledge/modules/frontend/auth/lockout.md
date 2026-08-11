---
type: Python Module
title: lockout
resource: frontend/auth/lockout.py#L1-L45
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/datetime
  - external/sqlalchemy
  - external/sqlalchemy-ext-asyncio
  - external/frontend-auth-models
---

# Contains

- [is_locked_out](../../../functions/frontend/auth/lockout/is_locked_out.md)
- [record_attempt](../../../functions/frontend/auth/lockout/record_attempt.md)
- [clear_email_streak](../../../functions/frontend/auth/lockout/clear_email_streak.md)

# Imports

- `datetime`
- `sqlalchemy`
- `sqlalchemy.ext.asyncio`
- `frontend.auth.models`