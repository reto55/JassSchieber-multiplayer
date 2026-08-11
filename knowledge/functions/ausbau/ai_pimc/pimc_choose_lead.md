---
type: Python Function
title: pimc_choose_lead
resource: ausbau/ai_pimc.py#L198-L235
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/game_session/card_to_code
  - functions/ausbau/ai_pimc/DealSampler/sample
  - functions/ausbau/ai_pimc/rollout
  called_by:
  - functions/ausbau/ai_strategies/HardStrategy/_lead
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_prefers_boss_trump_over_ruffable_side_lead
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_returns_none_when_below_min_samples
  - functions/tests/multiplayer/test_ai_pimc/test_pimc_is_deterministic_under_seed
---

# Signature

`def pimc_choose_lead(state: EngineState, candidate_leads, *, deadline_s: float = PIMC_DEADLINE_S, rng=None, min_samples: int = PIMC_MIN_SAMPLES, n: int = PIMC_N) -> Optional[object]:`

# Calls

- [card_to_code](../../../functions/ausbau/game_session/card_to_code.md)
- [sample](../../../functions/ausbau/ai_pimc/DealSampler/sample.md)
- [rollout](../../../functions/ausbau/ai_pimc/rollout.md)

# Called by

- [_lead](../../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)
- [test_pimc_prefers_boss_trump_over_ruffable_side_lead](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_prefers_boss_trump_over_ruffable_side_lead.md)
- [test_pimc_returns_none_when_below_min_samples](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_returns_none_when_below_min_samples.md)
- [test_pimc_is_deterministic_under_seed](../../../functions/tests/multiplayer/test_ai_pimc/test_pimc_is_deterministic_under_seed.md)