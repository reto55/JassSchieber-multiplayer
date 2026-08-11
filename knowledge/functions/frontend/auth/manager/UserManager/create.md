---
type: Python Method
title: create
resource: frontend/auth/manager.py#L43-L63
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/tombstone/hash_email
  - functions/frontend/auth/tombstone/hash_username
  called_by:
  - functions/frontend/auth/app/register
---

# Signature

`async def create(self, user_create, safe=False, request=None): # Check for duplicate username (fastapi-users only checks email)`

# Calls

- [hash_email](../../../../../functions/frontend/auth/tombstone/hash_email.md)
- [hash_username](../../../../../functions/frontend/auth/tombstone/hash_username.md)

# Called by

- [register](../../../../../functions/frontend/auth/app/register.md)