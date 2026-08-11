---
type: Python Function
title: _serializer
resource: frontend/auth/guest.py#L19-L20
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/guest/issue_guest_cookie
  - functions/frontend/auth/guest/read_guest_cookie
---

# Signature

`def _serializer(secret: str) -> URLSafeSerializer:`

# Called by

- [issue_guest_cookie](../../../../functions/frontend/auth/guest/issue_guest_cookie.md)
- [read_guest_cookie](../../../../functions/frontend/auth/guest/read_guest_cookie.md)