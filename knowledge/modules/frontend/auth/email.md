---
type: Python Module
title: email
resource: frontend/auth/email.py#L1-L84
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/dataclasses
  - external/typing
  - external/aiosmtplib
  - external/email-message
---

# Contains

- [Mail](../../../classes/frontend/auth/email/Mail.md)
- [MailBackend](../../../classes/frontend/auth/email/MailBackend.md)
- [send](../../../functions/frontend/auth/email/MailBackend/send.md)
- [ConsoleMailBackend](../../../classes/frontend/auth/email/ConsoleMailBackend.md)
- [send](../../../functions/frontend/auth/email/ConsoleMailBackend/send.md)
- [SmtpMailBackend](../../../classes/frontend/auth/email/SmtpMailBackend.md)
- [send](../../../functions/frontend/auth/email/SmtpMailBackend/send.md)
- [render_verification](../../../functions/frontend/auth/email/render_verification.md)
- [render_reset](../../../functions/frontend/auth/email/render_reset.md)
- [render_change_email_confirm](../../../functions/frontend/auth/email/render_change_email_confirm.md)
- [render_change_email_notice](../../../functions/frontend/auth/email/render_change_email_notice.md)
- [mask_email](../../../functions/frontend/auth/email/mask_email.md)

# Imports

- `dataclasses`
- `typing`
- `aiosmtplib`
- `email.message`