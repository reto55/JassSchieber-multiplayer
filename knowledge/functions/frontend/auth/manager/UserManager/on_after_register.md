---
type: Python Method
title: on_after_register
resource: frontend/auth/manager.py#L65-L87
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/email/render_verification
  - functions/ausbau/html5/js/lobby/refresh
---

# Signature

`async def on_after_register(self, user: User, request: Optional[Request] = None):`

# Calls

- [render_verification](../../../../../functions/frontend/auth/email/render_verification.md)
- [refresh](../../../../../functions/ausbau/html5/js/lobby/refresh.md)