---
type: Python Function
title: render_change_email_confirm
resource: frontend/auth/email.py#L68-L72
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/change_email
  - functions/tests/auth/test_email_backend/test_render_change_email_confirm
---

# Signature

`def render_change_email_confirm(*, base_url: str, token: str) -> str:`

# Called by

- [change_email](../../../../functions/frontend/auth/app/change_email.md)
- [test_render_change_email_confirm](../../../../functions/tests/auth/test_email_backend/test_render_change_email_confirm.md)