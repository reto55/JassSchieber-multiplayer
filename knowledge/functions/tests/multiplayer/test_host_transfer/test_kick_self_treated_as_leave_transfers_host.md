---
type: Python Function
title: test_kick_self_treated_as_leave_transfers_host
resource: tests/multiplayer/test_host_transfer.py#L327-L361
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/get_room
  - functions/ausbau/room/principal_id
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_kick_self_treated_as_leave_transfers_host(client, client_other):`

# Calls

- [get_room](../../../../functions/ausbau/room/get_room.md)
- [principal_id](../../../../functions/ausbau/room/principal_id.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)