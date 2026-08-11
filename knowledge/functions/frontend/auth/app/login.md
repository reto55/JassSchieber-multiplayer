---
type: Python Function
title: login
resource: frontend/auth/app.py#L101-L155
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/lockout/is_locked_out
  - functions/frontend/auth/lockout/record_attempt
  - functions/frontend/auth/lockout/clear_email_streak
---

# Signature

`async def login( request: Request, username: str = Form(...), password: str = Form(...), remember: str = Form(default=""), db: AsyncSession = Depends(get_session), manager=Depends(get_user_manager), ):`

# Calls

- [is_locked_out](../../../../functions/frontend/auth/lockout/is_locked_out.md)
- [record_attempt](../../../../functions/frontend/auth/lockout/record_attempt.md)
- [clear_email_streak](../../../../functions/frontend/auth/lockout/clear_email_streak.md)