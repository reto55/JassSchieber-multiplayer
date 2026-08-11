---
type: Python Function
title: _blocklist
resource: frontend/auth/passwords.py#L13-L17
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/passwords/validate_password
---

# Signature

`def _blocklist() -> frozenset[str]:`

# Called by

- [validate_password](../../../../functions/frontend/auth/passwords/validate_password.md)