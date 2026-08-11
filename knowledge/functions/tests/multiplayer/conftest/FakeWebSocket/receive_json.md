---
type: Python Method
title: receive_json
resource: tests/multiplayer/conftest.py#L34-L35
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/server/websocket_endpoint
  - functions/tests/multiplayer/test_conftest_smoke/test_fake_ws_send_recv
---

# Signature

`async def receive_json(self) -> dict:`

# Called by

- [websocket_endpoint](../../../../../functions/ausbau/server/websocket_endpoint.md)
- [test_fake_ws_send_recv](../../../../../functions/tests/multiplayer/test_conftest_smoke/test_fake_ws_send_recv.md)