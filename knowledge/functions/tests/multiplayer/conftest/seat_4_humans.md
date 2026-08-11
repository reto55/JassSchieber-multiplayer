---
type: Python Function
title: seat_4_humans
resource: tests/multiplayer/conftest.py#L60-L73
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout
  - functions/tests/multiplayer/test_disconnect/test_disconnect_state_event_set_wakes_awaiter
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant
  - functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round
  - functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far
  - functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat
  - functions/tests/multiplayer/test_play_trick/test_play_trick_updates_current_seat_turn_per_iteration
  - functions/tests/multiplayer/test_reaper/test_reap_skip_active_room
  - functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task
  - functions/tests/multiplayer/test_reclaim/test_reclaim_seat_after_ai_takeover_restores_human
  - functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume
  - functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others
  - functions/tests/multiplayer/test_reclaim/test_reclaim_state_event_set
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading
  - functions/tests/multiplayer/test_replay/test_replay_buffer_appends_one_trick
  - functions/tests/multiplayer/test_replay/test_replay_buffer_caps_at_three
  - functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_records_and_pushes
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_overwrites_prior_from_same_seat
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_accept_sets_pending_swap
  - functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands
  - functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_noop_when_no_pending
  - functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_ttl_fires_seat_swap_expired
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_human_picks_eicheln
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state
  - functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners
  - functions/tests/multiplayer/test_weis_phase/test_weis_request_per_seat_only_own_weis
  - functions/tests/multiplayer/test_weis_phase/test_weis_resolution_broadcasts_to_all
  - functions/tests/multiplayer/test_weis_phase/test_weis_decline
  - functions/tests/multiplayer/test_weis_phase/test_weis_request_not_sent_to_spectator
  - functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts
  - functions/tests/multiplayer/test_weis_phase/test_weis_no_cross_seat_leak
---

# Signature

`def seat_4_humans(s) -> dict[str, "FakeWebSocket"]:`

# Called by

- [test_disconnect_in_lobby_drops_to_ai_immediately](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately.md)
- [test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused.md)
- [test_reconnect_timeout_flips_to_ai](../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai.md)
- [test_reconnect_timeout_no_op_if_websocket_returned](../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned.md)
- [test_disconnect_mid_game_host_triggers_transfer_after_timeout](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout.md)
- [test_disconnect_state_event_set_wakes_awaiter](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_state_event_set_wakes_awaiter.md)
- [test_e2e_4_humans_full_game](../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game.md)
- [test_e2e_4_humans_trumpf_bock_variant](../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant.md)
- [test_play_trick_4_humans_one_round](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round.md)
- [test_play_trick_invalid_card_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts.md)
- [test_play_trick_wrong_type_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts.md)
- [test_play_trick_pending_carries_trick_so_far](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far.md)
- [test_play_trick_request_only_to_active_seat](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat.md)
- [test_play_trick_updates_current_seat_turn_per_iteration](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_updates_current_seat_turn_per_iteration.md)
- [test_reap_skip_active_room](../../../../functions/tests/multiplayer/test_reaper/test_reap_skip_active_room.md)
- [test_reclaim_seat_cancels_pending_reconnect_task](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task.md)
- [test_reclaim_seat_after_ai_takeover_restores_human](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_after_ai_takeover_restores_human.md)
- [test_reclaim_sends_room_resume](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume.md)
- [test_reclaim_broadcasts_seat_reclaimed_to_others](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others.md)
- [test_reclaim_state_event_set](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_state_event_set.md)
- [test_reclaim_mid_turn_resends_play_request](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request.md)
- [test_reclaim_mid_turn_no_play_request_when_not_active_seat](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat.md)
- [test_reclaim_mid_turn_lead_suit_none_when_leading](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading.md)
- [test_replay_buffer_appends_one_trick](../../../../functions/tests/multiplayer/test_replay/test_replay_buffer_appends_one_trick.md)
- [test_replay_buffer_caps_at_three](../../../../functions/tests/multiplayer/test_replay/test_replay_buffer_caps_at_three.md)
- [test_replay_entry_carries_winner_and_points_matching_trick_end](../../../../functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end.md)
- [test_seat_swap_request_records_and_pushes](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_records_and_pushes.md)
- [test_seat_swap_request_overwrites_prior_from_same_seat](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_overwrites_prior_from_same_seat.md)
- [test_seat_swap_accept_sets_pending_swap](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_accept_sets_pending_swap.md)
- [test_commit_pending_swap_swaps_principals_and_hands](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands.md)
- [test_commit_pending_swap_noop_when_no_pending](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_noop_when_no_pending.md)
- [test_commit_aborts_if_either_seat_disconnected_post_accept](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept.md)
- [test_seat_swap_ttl_fires_seat_swap_expired](../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_ttl_fires_seat_swap_expired.md)
- [test_trump_phase_human_picks_eicheln](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_human_picks_eicheln.md)
- [test_trump_phase_schieben_transfers_to_partner](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner.md)
- [test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state.md)
- [test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state](../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_operator_re_prompts_without_losing_schieben_state.md)
- [test_play_trick_appends_to_spiel_winners](../../../../functions/tests/multiplayer/test_variants/test_play_trick_appends_to_spiel_winners.md)
- [test_weis_request_per_seat_only_own_weis](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_per_seat_only_own_weis.md)
- [test_weis_resolution_broadcasts_to_all](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_resolution_broadcasts_to_all.md)
- [test_weis_decline](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_decline.md)
- [test_weis_request_not_sent_to_spectator](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_not_sent_to_spectator.md)
- [test_weis_phase_rejects_wrong_type_then_re_prompts](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts.md)
- [test_weis_no_cross_seat_leak](../../../../functions/tests/multiplayer/test_weis_phase/test_weis_no_cross_seat_leak.md)