---
type: Python Function
title: promote
resource: frontend/auth/admin.py#L75-L87
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/admin/audit
---

# Signature

`async def promote( user_id: str, request: Request, admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session), ):`

# Calls

- [audit](../../../../functions/frontend/auth/admin/audit.md)