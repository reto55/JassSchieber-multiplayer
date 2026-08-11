---
type: Python Method
title: last_sent_of_type
resource: tests/multiplayer/conftest.py#L47-L49
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/tests/multiplayer/test_conftest_smoke/test_fake_ws_send_recv
  - functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately
  - functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_host_triggers_transfer
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant
  - functions/tests/multiplayer/test_e2e_mixed_ai/test_e2e_mixed_difficulty_3_ai
  - functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human
  - functions/tests/multiplayer/test_host_transfer/test_reclaim_into_room_with_connected_host_does_not_promote
  - functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_transfers_host
  - functions/tests/multiplayer/test_host_transfer/test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target
  - functions/tests/multiplayer/test_host_transfer/test_kick_self_treated_as_leave_transfers_host
  - functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round
  - functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far
  - functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat
  - functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others
  - functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end
  - functions/tests/multiplayer/test_routing_helpers/test_send_to_seat_human
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_all_seats
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_except_seat
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_spectators
  - functions/tests/multiplayer/test_routing_helpers/test_broadcast_per_seat_factory
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_records_and_pushes
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_overwrites_prior_from_same_seat
  - functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands
  - functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_noop_when_no_pending
  - functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_ttl_fires_seat_swap_expired
  - functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_request_path
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_human_picks_eicheln
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner
  - functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state
  - functions/tests/multiplayer/test_weis_phase/test_weis_request_per_seat_only_own_weis
  - functions/tests/multiplayer/test_weis_phase/test_weis_resolution_broadcasts_to_all
  - functions/tests/multiplayer/test_weis_phase/test_weis_decline
  - functions/tests/multiplayer/test_weis_phase/test_weis_request_not_sent_to_spectator
  - functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts
  - functions/tests/multiplayer/test_weis_phase/test_weis_no_cross_seat_leak
---

# Signature

`def last_sent_of_type(self, t: str) -> dict | None:`

# Called by

- [test_fake_ws_send_recv](../../../../../functions/tests/multiplayer/test_conftest_smoke/test_fake_ws_send_recv.md)
- [test_disconnect_in_lobby_drops_to_ai_immediately](../../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately.md)
- [test_disconnect_in_lobby_host_triggers_transfer](../../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_host_triggers_transfer.md)
- [test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused](../../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused.md)
- [test_reconnect_timeout_flips_to_ai](../../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai.md)
- [test_reconnect_timeout_no_op_if_websocket_returned](../../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned.md)
- [test_disconnect_mid_game_host_triggers_transfer_after_timeout](../../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout.md)
- [test_e2e_4_humans_trumpf_bock_variant](../../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant.md)
- [test_e2e_mixed_difficulty_3_ai](../../../../../functions/tests/multiplayer/test_e2e_mixed_ai/test_e2e_mixed_difficulty_3_ai.md)
- [test_reclaim_into_hostless_room_promotes_reconnecting_human](../../../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_hostless_room_promotes_reconnecting_human.md)
- [test_reclaim_into_room_with_connected_host_does_not_promote](../../../../../functions/tests/multiplayer/test_host_transfer/test_reclaim_into_room_with_connected_host_does_not_promote.md)
- [test_host_leave_in_lobby_transfers_host](../../../../../functions/tests/multiplayer/test_host_transfer/test_host_leave_in_lobby_transfers_host.md)
- [test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target](../../../../../functions/tests/multiplayer/test_host_transfer/test_kick_lobby_happy_path_broadcasts_seat_kicked_and_closes_target.md)
- [test_kick_self_treated_as_leave_transfers_host](../../../../../functions/tests/multiplayer/test_host_transfer/test_kick_self_treated_as_leave_transfers_host.md)
- [test_play_trick_4_humans_one_round](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_4_humans_one_round.md)
- [test_play_trick_pending_carries_trick_so_far](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_pending_carries_trick_so_far.md)
- [test_play_trick_request_only_to_active_seat](../../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_request_only_to_active_seat.md)
- [test_reclaim_broadcasts_seat_reclaimed_to_others](../../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others.md)
- [test_replay_entry_carries_winner_and_points_matching_trick_end](../../../../../functions/tests/multiplayer/test_replay/test_replay_entry_carries_winner_and_points_matching_trick_end.md)
- [test_send_to_seat_human](../../../../../functions/tests/multiplayer/test_routing_helpers/test_send_to_seat_human.md)
- [test_broadcast_to_all_seats](../../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_all_seats.md)
- [test_broadcast_except_seat](../../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_except_seat.md)
- [test_broadcast_to_spectators](../../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_to_spectators.md)
- [test_broadcast_per_seat_factory](../../../../../functions/tests/multiplayer/test_routing_helpers/test_broadcast_per_seat_factory.md)
- [test_seat_swap_request_records_and_pushes](../../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_records_and_pushes.md)
- [test_seat_swap_request_overwrites_prior_from_same_seat](../../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_request_overwrites_prior_from_same_seat.md)
- [test_commit_pending_swap_swaps_principals_and_hands](../../../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands.md)
- [test_commit_pending_swap_noop_when_no_pending](../../../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_noop_when_no_pending.md)
- [test_commit_aborts_if_either_seat_disconnected_post_accept](../../../../../functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept.md)
- [test_seat_swap_ttl_fires_seat_swap_expired](../../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_ttl_fires_seat_swap_expired.md)
- [test_seat_swap_endpoint_happy_request_path](../../../../../functions/tests/multiplayer/test_seat_swap/test_seat_swap_endpoint_happy_request_path.md)
- [test_trump_phase_human_picks_eicheln](../../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_human_picks_eicheln.md)
- [test_trump_phase_schieben_transfers_to_partner](../../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_schieben_transfers_to_partner.md)
- [test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state](../../../../../functions/tests/multiplayer/test_trump_phase/test_trump_phase_invalid_type_re_prompts_without_losing_schieben_state.md)
- [test_weis_request_per_seat_only_own_weis](../../../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_per_seat_only_own_weis.md)
- [test_weis_resolution_broadcasts_to_all](../../../../../functions/tests/multiplayer/test_weis_phase/test_weis_resolution_broadcasts_to_all.md)
- [test_weis_decline](../../../../../functions/tests/multiplayer/test_weis_phase/test_weis_decline.md)
- [test_weis_request_not_sent_to_spectator](../../../../../functions/tests/multiplayer/test_weis_phase/test_weis_request_not_sent_to_spectator.md)
- [test_weis_phase_rejects_wrong_type_then_re_prompts](../../../../../functions/tests/multiplayer/test_weis_phase/test_weis_phase_rejects_wrong_type_then_re_prompts.md)
- [test_weis_no_cross_seat_leak](../../../../../functions/tests/multiplayer/test_weis_phase/test_weis_no_cross_seat_leak.md)