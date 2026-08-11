---
type: Python Function
title: test_stops_trump_when_all_outstanding_trumps_played
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L243-L260
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_play_out_trumps
---

# Signature

`def test_stops_trump_when_all_outstanding_trumps_played(): # Regression (removed in 941397e, restored): if all trumps outside our # hand are gone, the AI must stop drawing even though no opponent was # ever flagged void through a non-trump discard on a trump lead. # Schellen trump. comps holds Schellen 6, plus Rosen Ass.`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)
- [_play_out_trumps](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_play_out_trumps.md)