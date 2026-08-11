---
type: Python Function
title: render_verification
resource: frontend/auth/email.py#L50-L56
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/resend_verification
  - functions/frontend/auth/manager/UserManager/on_after_register
  - functions/tests/auth/test_email_backend/test_render_verification_contains_link
---

# Signature

`def render_verification(*, username: str, base_url: str, token: str) -> str:`

# Called by

- [resend_verification](../../../../functions/frontend/auth/app/resend_verification.md)
- [on_after_register](../../../../functions/frontend/auth/manager/UserManager/on_after_register.md)
- [test_render_verification_contains_link](../../../../functions/tests/auth/test_email_backend/test_render_verification_contains_link.md)