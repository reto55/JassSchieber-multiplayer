---
type: Python Function
title: whoami
resource: frontend/auth/app.py#L182-L225
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/guest/read_guest_cookie
  - functions/frontend/auth/guest/issue_guest_cookie
---

# Signature

`async def whoami( request: Request, response: Response, session: AsyncSession = Depends(get_session), ):`

# Calls

- [read_guest_cookie](../../../../functions/frontend/auth/guest/read_guest_cookie.md)
- [issue_guest_cookie](../../../../functions/frontend/auth/guest/issue_guest_cookie.md)