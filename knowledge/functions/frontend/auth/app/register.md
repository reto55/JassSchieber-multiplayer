---
type: Python Function
title: register
resource: frontend/auth/app.py#L78-L97
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/manager/UserManager/create
---

# Signature

`async def register( request: Request, response: Response, user_create: UserCreate, manager=Depends(get_user_manager), ):`

# Calls

- [create](../../../../functions/frontend/auth/manager/UserManager/create.md)