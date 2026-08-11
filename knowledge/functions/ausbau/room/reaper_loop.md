---
type: Python Function
title: reaper_loop
resource: ausbau/room.py#L184-L200
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/room/reap_rooms_once
  called_by:
  - functions/ausbau/server/_lifespan
  - functions/tests/multiplayer/test_reaper/test_reaper_loop_iterates_under_fast_clock
  - functions/tests/multiplayer/test_reaper/test_reaper_loop_survives_iteration_exception
---

# Signature

`async def reaper_loop() -> None:`

# Calls

- [reap_rooms_once](../../../functions/ausbau/room/reap_rooms_once.md)

# Called by

- [_lifespan](../../../functions/ausbau/server/_lifespan.md)
- [test_reaper_loop_iterates_under_fast_clock](../../../functions/tests/multiplayer/test_reaper/test_reaper_loop_iterates_under_fast_clock.md)
- [test_reaper_loop_survives_iteration_exception](../../../functions/tests/multiplayer/test_reaper/test_reaper_loop_survives_iteration_exception.md)