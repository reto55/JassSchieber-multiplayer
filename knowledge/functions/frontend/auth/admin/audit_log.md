---
type: Python Function
title: audit_log
resource: frontend/auth/admin.py#L122-L132
generated:
  by: okf-rs/0.3.0
---

# Signature

`async def audit_log( admin: User = Depends(require_admin), session: AsyncSession = Depends(get_session), ):`