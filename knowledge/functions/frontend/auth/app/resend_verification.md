---
type: Python Function
title: resend_verification
resource: frontend/auth/app.py#L281-L301
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/email/render_verification
---

# Signature

`async def resend_verification( user: User = Depends(current_user_dep), session: AsyncSession = Depends(get_session), ):`

# Calls

- [render_verification](../../../../functions/frontend/auth/email/render_verification.md)