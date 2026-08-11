---
type: Python Function
title: export_account
resource: frontend/auth/app.py#L228-L256
generated:
  by: okf-rs/0.3.0
---

# Signature

`async def export_account( user: User = Depends(current_user_dep), session: AsyncSession = Depends(get_session), ):`