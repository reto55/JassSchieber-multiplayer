---
type: Python Function
title: test_seat_swap_request_records_and_pushes
resource: tests/multiplayer/test_seat_swap.py#L58-L75
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_record_seat_swap_request
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_seat_swap_request_records_and_pushes():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_record_seat_swap_request](../../../../functions/ausbau/game_session/GameSession/_record_seat_swap_request.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)