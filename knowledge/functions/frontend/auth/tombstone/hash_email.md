---
type: Python Function
title: hash_email
resource: frontend/auth/tombstone.py#L4-L5
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/app/change_email
  - functions/frontend/auth/manager/UserManager/create
  - functions/tests/auth/test_tombstone/test_hash_email_lowercases
  - functions/tests/auth/test_tombstone/test_hash_email_strips_whitespace
  - functions/tests/auth/test_tombstone/test_hash_returns_64_hex
---

# Signature

`def hash_email(email: str) -> str:`

# Called by

- [change_email](../../../../functions/frontend/auth/app/change_email.md)
- [create](../../../../functions/frontend/auth/manager/UserManager/create.md)
- [test_hash_email_lowercases](../../../../functions/tests/auth/test_tombstone/test_hash_email_lowercases.md)
- [test_hash_email_strips_whitespace](../../../../functions/tests/auth/test_tombstone/test_hash_email_strips_whitespace.md)
- [test_hash_returns_64_hex](../../../../functions/tests/auth/test_tombstone/test_hash_returns_64_hex.md)