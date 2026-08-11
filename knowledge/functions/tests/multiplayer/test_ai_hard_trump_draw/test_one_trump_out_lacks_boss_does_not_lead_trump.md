---
type: Python Function
title: test_one_trump_out_lacks_boss_does_not_lead_trump
resource: tests/multiplayer/test_ai_hard_trump_draw.py#L110-L123
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_hard_trump_draw/_make
---

# Signature

`def test_one_trump_out_lacks_boss_does_not_lead_trump(): # Schellen trump. comps holds the Schellen Koenig (trumpf=15) and a Rosen # Ass. Exactly one trump is outstanding — the trump Under (SEU, trumpf=18) — # which outranks our top trump. Leading trump can only lose the trick (an # opponent holds SEU) or waste partner's trump (partner holds it). The AI # must NOT lead trump; it cashes the guaranteed non-trump winner instead.`

# Calls

- [_make](../../../../functions/tests/multiplayer/test_ai_hard_trump_draw/_make.md)