---
type: Python Class
title: UserCreate
resource: frontend/auth/schemas.py#L16-L31
generated:
  by: okf-rs/0.3.0
---

# Signature

`class UserCreate(schemas.BaseUserCreate): # Override email to accept test-style addresses (e.g. alice@test) in addition # to standard RFC-5321 addresses. The underlying email_validator library # supports `test_environment=True` for domains without a TLD.`