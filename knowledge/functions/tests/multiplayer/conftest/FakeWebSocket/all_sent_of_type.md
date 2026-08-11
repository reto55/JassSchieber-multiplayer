---
type: Python Method
title: all_sent_of_type
resource: tests/multiplayer/conftest.py#L51-L52
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant
  - functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round
  - functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far
  - functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat
  - functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading
  - functions/tests/multiplayer/test_run_spiel/test_start_game_runs_to_completion_4_ai
  - functions/tests/multiplayer/test_run_spiel/test_start_game_emits_game_start_per_spiel
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state
  - functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts
---

# Signature

`def all_sent_of_type(self, t: str) -> list[dict]:`

# Called by

- [test_e2e_4_humans_full_game](../../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game.md)
- [test_e2e_4_humans_trumpf_bock_variant](../../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant.md)
- [test_play_trick_4_humans_one_round](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round.md)
- [test_play_trick_invalid_card_re_prompts](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts.md)
- [test_play_trick_wrong_type_re_prompts](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts.md)
- [test_play_trick_pending_carries_trick_so_far](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far.md)
- [test_play_trick_request_only_to_active_seat](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat.md)
- [test_reclaim_sends_room_resume](../../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume.md)
- [test_reclaim_mid_turn_resends_play_request](../../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request.md)
- [test_reclaim_mid_turn_no_play_request_when_not_active_seat](../../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat.md)
- [test_reclaim_mid_turn_lead_suit_none_when_leading](../../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading.md)
- [test_start_game_runs_to_completion_4_ai](../../../../../functions/tests/multiplayer/test_run_spiel/test_start_game_runs_to_completion_4_ai.md)
- [test_start_game_emits_game_start_per_spiel](../../../../../functions/tests/multiplayer/test_run_spiel/test_start_game_emits_game_start_per_spiel.md)
- [test_trump_phase_schieben_transfers_to_partner](../../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner.md)
- [test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state](../../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state.md)
- [test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state](../../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state.md)
- [test_weis_phase_rejects_wrong_type_then_re_prompts](../../../../../functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts.md)