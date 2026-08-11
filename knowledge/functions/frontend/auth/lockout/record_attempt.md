---
type: Python Function
title: record_attempt
resource: frontend/auth/lockout.py#L30-L36
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/login
---

# Signature

`async def record_attempt(db: AsyncSession, *, email: str, ip: str, success: bool) -> None:`

# Called by

- [login](../../../../functions/frontend/auth/app/login.md)