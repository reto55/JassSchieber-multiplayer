---
type: Python Module
title: test_reaper
resource: tests/multiplayer/test_reaper.py#L1-L347
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/asyncio
  - external/time
  - external/pytest
  - external/ausbau-game-session
  - external/ausbau-room
  - external/frontend-auth-guest
  - external/tests-multiplayer-conftest
  - external/ausbau
---

# Contains

- [_fresh_session](../../../functions/tests/multiplayer/test_reaper/_fresh_session.md)
- [test_reap_finished_room_after_linger](../../../functions/tests/multiplayer/test_reaper/test_reap_finished_room_after_linger.md)
- [test_reap_finished_room_inside_linger_kept](../../../functions/tests/multiplayer/test_reaper/test_reap_finished_room_inside_linger_kept.md)
- [test_reap_idle_room_after_linger](../../../functions/tests/multiplayer/test_reaper/test_reap_idle_room_after_linger.md)
- [test_reap_skip_active_room](../../../functions/tests/multiplayer/test_reaper/test_reap_skip_active_room.md)
- [test_reap_idle_inside_linger_kept](../../../functions/tests/multiplayer/test_reaper/test_reap_idle_inside_linger_kept.md)
- [test_reaper_closes_spectator_ws_before_remove](../../../functions/tests/multiplayer/test_reaper/test_reaper_closes_spectator_ws_before_remove.md)
- [test_reaper_does_not_crash_on_individual_room_exception](../../../functions/tests/multiplayer/test_reaper/test_reaper_does_not_crash_on_individual_room_exception.md)
- [selective_close](../../../functions/tests/multiplayer/test_reaper/selective_close.md)
- [test_idle_since_starts_none_in_init](../../../functions/tests/multiplayer/test_reaper/test_idle_since_starts_none_in_init.md)
- [test_idle_since_set_when_last_human_leaves_lobby](../../../functions/tests/multiplayer/test_reaper/test_idle_since_set_when_last_human_leaves_lobby.md)
- [test_idle_since_cleared_when_human_reclaims](../../../functions/tests/multiplayer/test_reaper/test_idle_since_cleared_when_human_reclaims.md)
- [test_idle_since_not_set_when_other_humans_remain](../../../functions/tests/multiplayer/test_reaper/test_idle_since_not_set_when_other_humans_remain.md)
- [test_finished_at_set_on_game_end](../../../functions/tests/multiplayer/test_reaper/test_finished_at_set_on_game_end.md)
- [fast_sleep](../../../functions/tests/multiplayer/test_reaper/fast_sleep.md)
- [test_reaper_loop_iterates_under_fast_clock](../../../functions/tests/multiplayer/test_reaper/test_reaper_loop_iterates_under_fast_clock.md)
- [test_reaper_loop_survives_iteration_exception](../../../functions/tests/multiplayer/test_reaper/test_reaper_loop_survives_iteration_exception.md)
- [flaky_reap](../../../functions/tests/multiplayer/test_reaper/flaky_reap.md)
- [test_reap_skips_finished_room_with_no_finished_at](../../../functions/tests/multiplayer/test_reaper/test_reap_skips_finished_room_with_no_finished_at.md)

# Imports

- `asyncio`
- `time`
- `pytest`
- `ausbau.game_session`
- `ausbau.room`
- `frontend.auth.guest`
- `tests.multiplayer.conftest`
- `ausbau`