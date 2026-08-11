---
type: Python Function
title: render_reset
resource: frontend/auth/email.py#L59-L65
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/forgot
  - functions/frontend/auth/manager/UserManager/on_after_forgot_password
  - functions/tests/auth/test_email_backend/test_render_reset_contains_link
---

# Signature

`def render_reset(*, username: str, base_url: str, token: str) -> str:`

# Called by

- [forgot](../../../../functions/frontend/auth/app/forgot.md)
- [on_after_forgot_password](../../../../functions/frontend/auth/manager/UserManager/on_after_forgot_password.md)
- [test_render_reset_contains_link](../../../../functions/tests/auth/test_email_backend/test_render_reset_contains_link.md)