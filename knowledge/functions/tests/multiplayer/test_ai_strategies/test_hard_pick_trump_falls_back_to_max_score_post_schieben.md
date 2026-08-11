---
type: Python Function
title: test_hard_pick_trump_falls_back_to_max_score_post_schieben
resource: tests/multiplayer/test_ai_strategies.py#L202-L216
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_strategies/_hand_with_suits
---

# Signature

`def test_hard_pick_trump_falls_back_to_max_score_post_schieben(): # Post-schieben: same weak hand, but schieben_allowed=False forces commit. # With four Asses-and-Kings, Oben should score highest.`

# Calls

- [_hand_with_suits](../../../../functions/tests/multiplayer/test_ai_strategies/_hand_with_suits.md)