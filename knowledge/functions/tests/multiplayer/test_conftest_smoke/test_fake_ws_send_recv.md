---
type: Python Function
title: test_fake_ws_send_recv
resource: tests/multiplayer/test_conftest_smoke.py#L8-L14
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/FakeWebSocket/send_json
  - functions/tests/multiplayer/conftest/FakeWebSocket/push
  - functions/tests/multiplayer/conftest/FakeWebSocket/receive_json
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_fake_ws_send_recv(fake_ws):`

# Calls

- [send_json](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/send_json.md)
- [push](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/push.md)
- [receive_json](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/receive_json.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)