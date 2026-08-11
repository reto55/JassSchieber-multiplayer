---
type: Python Function
title: read_guest_cookie
resource: frontend/auth/guest.py#L28-L38
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/frontend/auth/guest/_serializer
  called_by:
  - functions/ausbau/server/_get_principal
  - functions/ausbau/server/websocket_endpoint
  - functions/frontend/auth/app/whoami
  - functions/frontend/auth/deps/current_principal
  - functions/tests/auth/test_guest_cookie/test_issue_then_read_roundtrip
  - functions/tests/auth/test_guest_cookie/test_tampered_cookie_rejected
  - functions/tests/auth/test_guest_cookie/test_wrong_secret_rejected
  - functions/tests/auth/test_guest_cookie/test_garbage_cookie_rejected
---

# Signature

`def read_guest_cookie(cookie_value: str, secret: str) -> Guest:`

# Calls

- [_serializer](../../../../functions/frontend/auth/guest/_serializer.md)

# Called by

- [_get_principal](../../../../functions/ausbau/server/_get_principal.md)
- [websocket_endpoint](../../../../functions/ausbau/server/websocket_endpoint.md)
- [whoami](../../../../functions/frontend/auth/app/whoami.md)
- [current_principal](../../../../functions/frontend/auth/deps/current_principal.md)
- [test_issue_then_read_roundtrip](../../../../functions/tests/auth/test_guest_cookie/test_issue_then_read_roundtrip.md)
- [test_tampered_cookie_rejected](../../../../functions/tests/auth/test_guest_cookie/test_tampered_cookie_rejected.md)
- [test_wrong_secret_rejected](../../../../functions/tests/auth/test_guest_cookie/test_wrong_secret_rejected.md)
- [test_garbage_cookie_rejected](../../../../functions/tests/auth/test_guest_cookie/test_garbage_cookie_rejected.md)