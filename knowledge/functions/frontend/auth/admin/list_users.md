---
type: Python Function
title: list_users
resource: frontend/auth/admin.py#L20-L40
generated:
  by: okf-rs/0.3.0
---

# Signature

`async def list_users( page: int = 1, q: str = "", admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session), ):`