---
type: Python Function
title: test_forgot_known_email_sends_mail
resource: tests/auth/test_password_reset.py#L25-L30
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/auth/test_password_reset/_reset_token
---

# Signature

`async def test_forgot_known_email_sends_mail(client, mail):`

# Calls

- [_reset_token](../../../../functions/tests/auth/test_password_reset/_reset_token.md)