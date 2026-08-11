---
type: Python Function
title: demote
resource: frontend/auth/admin.py#L90-L104
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/admin/audit
---

# Signature

`async def demote( user_id: str, request: Request, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session), ):`

# Calls

- [audit](../../../../functions/frontend/auth/admin/audit.md)