---
type: Python Function
title: test_commit_pending_swap_noop_when_no_pending
resource: tests/multiplayer/test_seat_swap.py#L160-L169
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/conftest/seat_4_humans
  - functions/ausbau/game_session/GameSession/_commit_pending_swap
  - functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type
---

# Signature

`async def test_commit_pending_swap_noop_when_no_pending():`

# Calls

- [seat_4_humans](../../../../functions/tests/multiplayer/conftest/seat_4_humans.md)
- [_commit_pending_swap](../../../../functions/ausbau/game_session/GameSession/_commit_pending_swap.md)
- [last_sent_of_type](../../../../functions/tests/multiplayer/conftest/FakeWebSocket/last_sent_of_type.md)