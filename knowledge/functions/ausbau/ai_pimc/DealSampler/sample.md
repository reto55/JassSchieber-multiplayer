---
type: Python Method
title: sample
resource: ausbau/ai_pimc.py#L83-L105
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/ai_pimc/DealSampler/_allowed_holders
  - functions/ausbau/ai_pimc/_to_hand_dict
  called_by:
  - functions/ausbau/ai_pimc/pimc_choose_lead
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_voids
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player
  - functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed
---

# Signature

`def sample(self, rng) -> dict:`

# Calls

- [_allowed_holders](../../../../functions/ausbau/ai_pimc/DealSampler/_allowed_holders.md)
- [_to_hand_dict](../../../../functions/ausbau/ai_pimc/_to_hand_dict.md)

# Called by

- [pimc_choose_lead](../../../../functions/ausbau/ai_pimc/pimc_choose_lead.md)
- [test_sampler_respects_capacities_and_partitions_unseen](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_capacities_and_partitions_unseen.md)
- [test_sampler_respects_voids](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_respects_voids.md)
- [test_sampler_under_holdback_only_under_to_voided_player](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_under_holdback_only_under_to_voided_player.md)
- [test_sampler_is_deterministic_under_seed](../../../../functions/tests/multiplayer/test_ai_pimc/test_sampler_is_deterministic_under_seed.md)