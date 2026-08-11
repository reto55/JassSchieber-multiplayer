---
type: Python Function
title: _reset_token
resource: tests/auth/test_password_reset.py#L13-L17
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/tests/auth/test_password_reset/test_forgot_known_email_sends_mail
  - functions/tests/auth/test_password_reset/test_reset_revokes_all_sessions
  - functions/tests/auth/test_password_reset/test_reset_used_token
---

# Signature

`def _reset_token(mail):`

# Called by

- [test_forgot_known_email_sends_mail](../../../../functions/tests/auth/test_password_reset/test_forgot_known_email_sends_mail.md)
- [test_reset_revokes_all_sessions](../../../../functions/tests/auth/test_password_reset/test_reset_revokes_all_sessions.md)
- [test_reset_used_token](../../../../functions/tests/auth/test_password_reset/test_reset_used_token.md)