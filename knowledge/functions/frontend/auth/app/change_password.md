---
type: Python Function
title: change_password
resource: frontend/auth/app.py#L351-L369
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/app/verify
---

# Signature

`async def change_password( payload: dict, request: Request, user: User = Depends(current_user_dep), session: AsyncSession = Depends(get_session), ):`

# Calls

- [verify](../../../../functions/frontend/auth/app/verify.md)