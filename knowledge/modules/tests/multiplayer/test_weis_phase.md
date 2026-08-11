---
type: Python Module
title: test_weis_phase
resource: tests/multiplayer/test_weis_phase.py#L1-L348
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/unittest-mock
  - external/pytest
  - external/cards-refactored
  - external/ausbau-game-session
  - external/ausbau-room
  - external/frontend-auth-guest
  - external/tests-multiplayer-conftest
---

# Contains

- [_empty_hand](../../../functions/tests/multiplayer/test_weis_phase/_empty_hand.md)
- [FakePlay](../../../classes/tests/multiplayer/test_weis_phase/FakePlay.md)
- [__init__](../../../functions/tests/multiplayer/test_weis_phase/FakePlay/__init__.md)
- [_fresh_session](../../../functions/tests/multiplayer/test_weis_phase/_fresh_session.md)
- [_describe_weis_per_position](../../../functions/tests/multiplayer/test_weis_phase/_describe_weis_per_position.md)
- [factory](../../../functions/tests/multiplayer/test_weis_phase/factory.md)
- [_impl](../../../functions/tests/multiplayer/test_weis_phase/_impl.md)
- [test_weis_request_per_seat_only_own_weis](../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_per_seat_only_own_weis.md)
- [test_weis_resolution_broadcasts_to_all](../../../functions/tests/multiplayer/test_weis_phase/test_weis_resolution_broadcasts_to_all.md)
- [test_weis_decline](../../../functions/tests/multiplayer/test_weis_phase/test_weis_decline.md)
- [test_weis_request_not_sent_to_spectator](../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_not_sent_to_spectator.md)
- [test_weis_phase_rejects_wrong_type_then_re_prompts](../../../functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts.md)
- [test_weis_no_cross_seat_leak](../../../functions/tests/multiplayer/test_weis_phase/test_weis_no_cross_seat_leak.md)

# Imports

- `unittest.mock`
- `pytest`
- `Cards_refactored`
- `ausbau.game_session`
- `ausbau.room`
- `frontend.auth.guest`
- `tests.multiplayer.conftest`