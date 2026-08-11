---
type: Python Function
title: unban
resource: frontend/auth/admin.py#L60-L72
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/admin/audit
---

# Signature

`async def unban( user_id: str, request: Request, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session), ):`

# Calls

- [audit](../../../../functions/frontend/auth/admin/audit.md)