---
type: Python Module
title: ai_pimc
resource: ausbau/ai_pimc.py#L1-L235
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/time
  - external/dataclasses
  - external/typing
  - external/cards-refactored
  - external/ausbau-game-session
  - external/random-as-random
---

# Contains

- [SamplingError](../../classes/ausbau/ai_pimc/SamplingError.md)
- [EngineState](../../classes/ausbau/ai_pimc/EngineState.md)
- [_to_hand_dict](../../functions/ausbau/ai_pimc/_to_hand_dict.md)
- [DealSampler](../../classes/ausbau/ai_pimc/DealSampler.md)
- [__init__](../../functions/ausbau/ai_pimc/DealSampler/__init__.md)
- [_allowed_holders](../../functions/ausbau/ai_pimc/DealSampler/_allowed_holders.md)
- [sample](../../functions/ausbau/ai_pimc/DealSampler/sample.md)
- [_clone_hand](../../functions/ausbau/ai_pimc/_clone_hand.md)
- [_remove_card](../../functions/ausbau/ai_pimc/_remove_card.md)
- [_order_from](../../functions/ausbau/ai_pimc/_order_from.md)
- [rollout](../../functions/ausbau/ai_pimc/rollout.md)
- [pimc_choose_lead](../../functions/ausbau/ai_pimc/pimc_choose_lead.md)

# Imports

- `time`
- `dataclasses`
- `typing`
- `Cards_refactored`
- `ausbau.game_session`
- `random as _random`