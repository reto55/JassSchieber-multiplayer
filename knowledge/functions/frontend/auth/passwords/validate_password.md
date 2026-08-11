---
type: Python Function
title: validate_password
resource: frontend/auth/passwords.py#L20-L33
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/passwords/_blocklist
---

# Signature

`def validate_password(password: str, *, username: str, email: str) -> None:`

# Calls

- [_blocklist](../../../../functions/frontend/auth/passwords/_blocklist.md)