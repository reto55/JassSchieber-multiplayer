---
type: Python Function
title: audit
resource: frontend/auth/admin.py#L12-L17
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/frontend/auth/admin/ban
  - functions/frontend/auth/admin/unban
  - functions/frontend/auth/admin/promote
  - functions/frontend/auth/admin/demote
  - functions/frontend/auth/admin/force_verify
---

# Signature

`async def audit(session, *, admin_id, action, target_id, reason, ip):`

# Called by

- [ban](../../../../functions/frontend/auth/admin/ban.md)
- [unban](../../../../functions/frontend/auth/admin/unban.md)
- [promote](../../../../functions/frontend/auth/admin/promote.md)
- [demote](../../../../functions/frontend/auth/admin/demote.md)
- [force_verify](../../../../functions/frontend/auth/admin/force_verify.md)