---
type: Python Function
title: change_email
resource: frontend/auth/app.py#L372-L420
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/app/verify
  - functions/frontend/auth/tombstone/hash_email
  - functions/frontend/auth/email/render_change_email_confirm
  - functions/frontend/auth/email/render_change_email_notice
  - functions/frontend/auth/email/mask_email
---

# Signature

`async def change_email( payload: dict, request: Request, user: User = Depends(current_user_dep), session: AsyncSession = Depends(get_session), ):`

# Calls

- [verify](../../../../functions/frontend/auth/app/verify.md)
- [hash_email](../../../../functions/frontend/auth/tombstone/hash_email.md)
- [render_change_email_confirm](../../../../functions/frontend/auth/email/render_change_email_confirm.md)
- [render_change_email_notice](../../../../functions/frontend/auth/email/render_change_email_notice.md)
- [mask_email](../../../../functions/frontend/auth/email/mask_email.md)