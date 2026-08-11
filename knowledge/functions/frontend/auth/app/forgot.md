---
type: Python Function
title: forgot
resource: frontend/auth/app.py#L306-L323
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/email/render_reset
---

# Signature

`async def forgot(request: Request, payload: dict, session: AsyncSession = Depends(get_session)):`

# Calls

- [render_reset](../../../../functions/frontend/auth/email/render_reset.md)