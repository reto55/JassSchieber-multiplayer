---
type: Python Function
title: ban
resource: frontend/auth/admin.py#L43-L57
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/admin/audit
---

# Signature

`async def ban( user_id: str, request: Request, payload: Optional[dict] = None, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session), ):`

# Calls

- [audit](../../../../functions/frontend/auth/admin/audit.md)