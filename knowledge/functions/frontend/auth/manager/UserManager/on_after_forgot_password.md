---
type: Python Method
title: on_after_forgot_password
resource: frontend/auth/manager.py#L89-L108
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/email/render_reset
---

# Signature

`async def on_after_forgot_password(self, user: User, token: str, request=None): # fastapi-users issues its own JWT token; we replace with our own DB-backed # token to keep audit + revocation simple`

# Calls

- [render_reset](../../../../../functions/frontend/auth/email/render_reset.md)