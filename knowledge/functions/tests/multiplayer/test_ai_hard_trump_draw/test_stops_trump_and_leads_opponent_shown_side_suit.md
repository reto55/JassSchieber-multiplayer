---
type: Python Function
title: test_stops_trump_and_leads_opponent_shown_side_suit
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L176-L187
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void
---

# Signature

`def test_stops_trump_and_leads_opponent_shown_side_suit(): # No guaranteed winner; dump into a non-trump suit an opponent has shown # so partner (still holding trump) can trump in. Never lead the trump Six.`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)
- [_drive_both_opponents_void](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_drive_both_opponents_void.md)