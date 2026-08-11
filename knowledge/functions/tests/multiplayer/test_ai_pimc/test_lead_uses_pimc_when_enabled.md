---
type: Python Function
title: test_lead_uses_pimc_when_enabled
resource: tests/multiplayer/test_ai_pimc.py#L341-L355
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/tests/multiplayer/test_ai_pimc/_make_strat
  - functions/Cards_refactored/create_card
  - functions/ausbau/ai_strategies/HardStrategy/_lead
---

# Signature

`def test_lead_uses_pimc_when_enabled(monkeypatch):`

# Calls

- [_make_strat](../../../../functions/tests/multiplayer/test_ai_pimc/_make_strat.md)
- [create_card](../../../../functions/Cards_refactored/create_card.md)
- [_lead](../../../../functions/ausbau/ai_strategies/HardStrategy/_lead.md)