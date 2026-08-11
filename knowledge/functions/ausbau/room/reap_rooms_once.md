---
type: Python Function
title: reap_rooms_once
resource: ausbau/room.py#L139-L181
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/_close_room
  called_by:
  - functions/ausbau/room/reaper_loop
  - functions/tests/multiplayer/test_reaper/test_reap_finished_room_after_linger
  - functions/tests/multiplayer/test_reaper/test_reap_finished_room_inside_linger_kept
  - functions/tests/multiplayer/test_reaper/test_reap_idle_room_after_linger
  - functions/tests/multiplayer/test_reaper/test_reap_skip_active_room
  - functions/tests/multiplayer/test_reaper/test_reap_idle_inside_linger_kept
  - functions/tests/multiplayer/test_reaper/test_reaper_closes_spectator_ws_before_remove
  - functions/tests/multiplayer/test_reaper/test_reaper_does_not_crash_on_individual_room_exception
  - functions/tests/multiplayer/test_reaper/test_reap_skips_finished_room_with_no_finished_at
---

# Signature

`async def reap_rooms_once() -> list[str]:`

# Calls

- [_close_room](../../../functions/ausbau/room/_close_room.md)

# Called by

- [reaper_loop](../../../functions/ausbau/room/reaper_loop.md)
- [test_reap_finished_room_after_linger](../../../functions/tests/multiplayer/test_reaper/test_reap_finished_room_after_linger.md)
- [test_reap_finished_room_inside_linger_kept](../../../functions/tests/multiplayer/test_reaper/test_reap_finished_room_inside_linger_kept.md)
- [test_reap_idle_room_after_linger](../../../functions/tests/multiplayer/test_reaper/test_reap_idle_room_after_linger.md)
- [test_reap_skip_active_room](../../../functions/tests/multiplayer/test_reaper/test_reap_skip_active_room.md)
- [test_reap_idle_inside_linger_kept](../../../functions/tests/multiplayer/test_reaper/test_reap_idle_inside_linger_kept.md)
- [test_reaper_closes_spectator_ws_before_remove](../../../functions/tests/multiplayer/test_reaper/test_reaper_closes_spectator_ws_before_remove.md)
- [test_reaper_does_not_crash_on_individual_room_exception](../../../functions/tests/multiplayer/test_reaper/test_reaper_does_not_crash_on_individual_room_exception.md)
- [test_reap_skips_finished_room_with_no_finished_at](../../../functions/tests/multiplayer/test_reaper/test_reap_skips_finished_room_with_no_finished_at.md)