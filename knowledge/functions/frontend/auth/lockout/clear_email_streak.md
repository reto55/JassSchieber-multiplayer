---
type: Python Function
title: clear_email_streak
resource: frontend/auth/lockout.py#L39-L45
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/login
---

# Signature

`async def clear_email_streak(db: AsyncSession, *, email: str) -> None:`

# Called by

- [login](../../../../functions/frontend/auth/app/login.md)