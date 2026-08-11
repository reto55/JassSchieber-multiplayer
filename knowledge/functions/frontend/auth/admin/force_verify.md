---
type: Python Function
title: force_verify
resource: frontend/auth/admin.py#L107-L119
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/admin/audit
---

# Signature

`async def force_verify( user_id: str, request: Request, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session), ):`

# Calls

- [audit](../../../../functions/frontend/auth/admin/audit.md)