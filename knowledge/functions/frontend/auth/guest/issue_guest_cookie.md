---
type: Python Function
title: issue_guest_cookie
resource: frontend/auth/guest.py#L23-L25
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/guest/_serializer
  called_by:
  - functions/ausbau/server/_get_principal
  - functions/frontend/auth/app/whoami
  - functions/frontend/auth/deps/current_principal
  - functions/tests/auth/test_guest_cookie/test_issue_then_read_roundtrip
  - functions/tests/auth/test_guest_cookie/test_tampered_cookie_rejected
  - functions/tests/auth/test_guest_cookie/test_wrong_secret_rejected
---

# Signature

`def issue_guest_cookie(secret: str) -> tuple[str, Guest]:`

# Calls

- [_serializer](../../../../functions/frontend/auth/guest/_serializer.md)

# Called by

- [_get_principal](../../../../functions/ausbau/server/_get_principal.md)
- [whoami](../../../../functions/frontend/auth/app/whoami.md)
- [current_principal](../../../../functions/frontend/auth/deps/current_principal.md)
- [test_issue_then_read_roundtrip](../../../../functions/tests/auth/test_guest_cookie/test_issue_then_read_roundtrip.md)
- [test_tampered_cookie_rejected](../../../../functions/tests/auth/test_guest_cookie/test_tampered_cookie_rejected.md)
- [test_wrong_secret_rejected](../../../../functions/tests/auth/test_guest_cookie/test_wrong_secret_rejected.md)