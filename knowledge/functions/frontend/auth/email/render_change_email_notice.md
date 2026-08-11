---
type: Python Function
title: render_change_email_notice
resource: frontend/auth/email.py#L75-L79
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/change_email
  - functions/tests/auth/test_email_backend/test_render_change_email_notice_masks
---

# Signature

`def render_change_email_notice(*, masked_new_email: str) -> str:`

# Called by

- [change_email](../../../../functions/frontend/auth/app/change_email.md)
- [test_render_change_email_notice_masks](../../../../functions/tests/auth/test_email_backend/test_render_change_email_notice_masks.md)