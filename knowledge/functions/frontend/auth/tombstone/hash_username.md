---
type: Python Function
title: hash_username
resource: frontend/auth/tombstone.py#L8-L9
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/manager/UserManager/create
  - functions/tests/auth/test_tombstone/test_hash_username_lowercases
---

# Signature

`def hash_username(username: str) -> str:`

# Called by

- [create](../../../../functions/frontend/auth/manager/UserManager/create.md)
- [test_hash_username_lowercases](../../../../functions/tests/auth/test_tombstone/test_hash_username_lowercases.md)