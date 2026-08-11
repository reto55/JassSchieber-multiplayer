---
type: Python Function
title: test_one_trump_out_holds_boss_still_leads_trump
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L137-L147
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
---

# Signature

`def test_one_trump_out_holds_boss_still_leads_trump(): # Counterpart: exactly one trump out, but it is LOWER than our top trump — # we hold the boss. Rule A still fires: lead the boss to flush the last # outstanding trump. comps holds the trump Under (SEU, trumpf=18); the lone # outstanding trump is the Schellen Koenig (SEK, trumpf=15).`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)