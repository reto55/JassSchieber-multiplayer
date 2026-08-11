---
type: Python Function
title: is_locked_out
resource: frontend/auth/lockout.py#L13-L27
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/login
---

# Signature

`async def is_locked_out(db: AsyncSession, *, email: str, ip: str) -> bool:`

# Called by

- [login](../../../../functions/frontend/auth/app/login.md)