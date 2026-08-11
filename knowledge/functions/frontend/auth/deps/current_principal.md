---
type: Python Function
title: current_principal
resource: frontend/auth/deps.py#L49-L87
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/guest/read_guest_cookie
  - functions/frontend/auth/guest/issue_guest_cookie
---

# Signature

`async def current_principal( request: Request, response: Response, session: AsyncSession = Depends(get_session), ): # Try authed user first`

# Calls

- [read_guest_cookie](../../../../functions/frontend/auth/guest/read_guest_cookie.md)
- [issue_guest_cookie](../../../../functions/frontend/auth/guest/issue_guest_cookie.md)