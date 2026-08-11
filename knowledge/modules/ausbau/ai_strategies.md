---
type: Python Module
title: ai_strategies
resource: ausbau/ai_strategies.py#L1-L581
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/logging
  - external/random
  - external/typing
  - external/ausbau-game-session
  - external/utils-card-utils
  - external/random-as-random
  - external/cards-refactored
  - external/ausbau-ai-pimc
  - external/ausbau-ai-pimc-as-ai-pimc
---

# Contains

- [AIStrategy](../../classes/ausbau/ai_strategies/AIStrategy.md)
- [__init__](../../functions/ausbau/ai_strategies/AIStrategy/__init__.md)
- [pick_trump](../../functions/ausbau/ai_strategies/AIStrategy/pick_trump.md)
- [pick_card](../../functions/ausbau/ai_strategies/AIStrategy/pick_card.md)
- [on_spiel_start](../../functions/ausbau/ai_strategies/AIStrategy/on_spiel_start.md)
- [on_card_played](../../functions/ausbau/ai_strategies/AIStrategy/on_card_played.md)
- [EasyStrategy](../../classes/ausbau/ai_strategies/EasyStrategy.md)
- [pick_trump](../../functions/ausbau/ai_strategies/EasyStrategy/pick_trump.md)
- [pick_card](../../functions/ausbau/ai_strategies/EasyStrategy/pick_card.md)
- [MediumStrategy](../../classes/ausbau/ai_strategies/MediumStrategy.md)
- [pick_trump](../../functions/ausbau/ai_strategies/MediumStrategy/pick_trump.md)
- [pick_card](../../functions/ausbau/ai_strategies/MediumStrategy/pick_card.md)
- [HardStrategy](../../classes/ausbau/ai_strategies/HardStrategy.md)
- [__init__](../../functions/ausbau/ai_strategies/HardStrategy/__init__.md)
- [_opponents](../../functions/ausbau/ai_strategies/HardStrategy/_opponents.md)
- [on_spiel_start](../../functions/ausbau/ai_strategies/HardStrategy/on_spiel_start.md)
- [on_card_played](../../functions/ausbau/ai_strategies/HardStrategy/on_card_played.md)
- [pick_trump](../../functions/ausbau/ai_strategies/HardStrategy/pick_trump.md)
- [_card_value](../../functions/ausbau/ai_strategies/HardStrategy/_card_value.md)
- [_strength](../../functions/ausbau/ai_strategies/HardStrategy/_strength.md)
- [_is_guaranteed_winner](../../functions/ausbau/ai_strategies/HardStrategy/_is_guaranteed_winner.md)
- [_both_opponents_void_trump](../../functions/ausbau/ai_strategies/HardStrategy/_both_opponents_void_trump.md)
- [_build_engine_state](../../functions/ausbau/ai_strategies/HardStrategy/_build_engine_state.md)
- [_lead](../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)
- [_lead_heuristic](../../functions/ausbau/ai_strategies/HardStrategy/_lead_heuristic.md)
- [_lead_legacy](../../functions/ausbau/ai_strategies/HardStrategy/_lead_legacy.md)
- [pick_card](../../functions/ausbau/ai_strategies/HardStrategy/pick_card.md)
- [_winner_so_far](../../functions/ausbau/ai_strategies/HardStrategy/_winner_so_far.md)
- [make_strategy](../../functions/ausbau/ai_strategies/make_strategy.md)

# Imports

- `logging`
- `random`
- `typing`
- `ausbau.game_session`
- `utils.card_utils`
- `random as _random`
- `Cards_refactored`
- `ausbau.ai_pimc`
- `ausbau.ai_pimc as ai_pimc`