---
type: Python Function
title: delete_account
resource: frontend/auth/app.py#L445-L476
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/app/verify
---

# Signature

`async def delete_account( payload: dict = Body(...), user: User = Depends(current_user_dep), session: AsyncSession = Depends(get_session), ):`

# Calls

- [verify](../../../../functions/frontend/auth/app/verify.md)