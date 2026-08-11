---
type: Python Function
title: verify
resource: frontend/auth/app.py#L259-L278
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/change_password
  - functions/frontend/auth/app/change_email
  - functions/frontend/auth/app/delete_account
---

# Signature

`async def verify(token: str, session: AsyncSession = Depends(get_session)):`

# Called by

- [change_password](../../../../functions/frontend/auth/app/change_password.md)
- [change_email](../../../../functions/frontend/auth/app/change_email.md)
- [delete_account](../../../../functions/frontend/auth/app/delete_account.md)