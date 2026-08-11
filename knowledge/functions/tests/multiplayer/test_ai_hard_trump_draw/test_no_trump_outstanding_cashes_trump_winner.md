---
type: Python Function
title: test_no_trump_outstanding_cashes_trump_winner
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L263-L273
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_play_out_trumps
---

# Signature

`def test_no_trump_outstanding_cashes_trump_winner(): # Counterpart: once NO trump is outstanding (partner void too), a trump # winner may be cashed when it banks the most points. Trump Under = 20 pts # beats Rosen Koenig = 4 pts.`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)
- [_play_out_trumps](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_play_out_trumps.md)