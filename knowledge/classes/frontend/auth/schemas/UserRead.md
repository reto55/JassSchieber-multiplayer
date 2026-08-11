---
type: Python Class
title: UserRead
resource: frontend/auth/schemas.py#L8-L13
generated:
  by: okf-rs/0.3.0
---

# Signature

`class UserRead(schemas.BaseUser[str]): # Override email to plain str so that test-style addresses (e.g. alice@test) # pass serialisation without requiring a TLD.`