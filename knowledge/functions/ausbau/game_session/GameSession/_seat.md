---
type: Python Method
title: _seat
resource: ausbau/game_session.py#L348-L352
visibility: private
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/game_session/GameSession/send_to_seat
  - functions/ausbau/game_session/GameSession/_disconnect_seat
  - functions/ausbau/game_session/GameSession/_reconnect_timeout
  - functions/ausbau/game_session/GameSession/_reclaim_seat
  - functions/ausbau/game_session/GameSession/_commit_pending_swap
  - functions/ausbau/game_session/GameSession/_await_seat_action
  - functions/ausbau/game_session/GameSession/_weis_phase
  - functions/ausbau/game_session/GameSession/_game_start_for
  - functions/tests/multiplayer/test_await_seat_action/test_await_human_returns_queued_message
  - functions/tests/multiplayer/test_await_seat_action/test_await_ai_computes_synchronously_no_queue_touched
  - functions/tests/multiplayer/test_await_seat_action/test_await_disconnected_seat_blocks_until_event_set
  - functions/tests/multiplayer/test_await_seat_action/test_compute_ai_trump_uses_farbe_lang
  - functions/tests/multiplayer/test_await_seat_action/test_compute_ai_play_uses_ai_select_card
  - functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused
  - functions/tests/multiplayer/test_disconnect/test_disconnect_idempotent_for_ai_or_already_disconnected
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai
  - functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned
  - functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout
  - functions/tests/multiplayer/test_disconnect/test_disconnect_state_event_set_wakes_awaiter
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game
  - functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant
  - functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid
  - functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts
  - functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts
  - functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task
  - functions/tests/multiplayer/test_reclaim/test_reclaim_seat_after_ai_takeover_restores_human
  - functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume
  - functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others
  - functions/tests/multiplayer/test_reclaim/test_reclaim_state_event_set
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat
  - functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading
  - functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick
  - functions/tests/multiplayer/test_seat_helpers/test_seat_by_position
  - functions/tests/multiplayer/test_seat_helpers/test_seat_by_position_invalid
  - functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands
  - functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept
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

`def _seat(self, position: str):`

# Called by

- [send_to_seat](../../../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [_disconnect_seat](../../../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reconnect_timeout](../../../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [_reclaim_seat](../../../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [_commit_pending_swap](../../../../functions/ausbau/game_session/GameSession/_commit_pending_swap.md)
- [_await_seat_action](../../../../functions/ausbau/game_session/GameSession/_await_seat_action.md)
- [_weis_phase](../../../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [_game_start_for](../../../../functions/ausbau/game_session/GameSession/_game_start_for.md)
- [test_await_human_returns_queued_message](../../../../functions/tests/multiplayer/test_await_seat_action/test_await_human_returns_queued_message.md)
- [test_await_ai_computes_synchronously_no_queue_touched](../../../../functions/tests/multiplayer/test_await_seat_action/test_await_ai_computes_synchronously_no_queue_touched.md)
- [test_await_disconnected_seat_blocks_until_event_set](../../../../functions/tests/multiplayer/test_await_seat_action/test_await_disconnected_seat_blocks_until_event_set.md)
- [test_compute_ai_trump_uses_farbe_lang](../../../../functions/tests/multiplayer/test_await_seat_action/test_compute_ai_trump_uses_farbe_lang.md)
- [test_compute_ai_play_uses_ai_select_card](../../../../functions/tests/multiplayer/test_await_seat_action/test_compute_ai_play_uses_ai_select_card.md)
- [test_disconnect_in_lobby_drops_to_ai_immediately](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_in_lobby_drops_to_ai_immediately.md)
- [test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_starts_60s_timer_and_broadcasts_paused.md)
- [test_disconnect_idempotent_for_ai_or_already_disconnected](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_idempotent_for_ai_or_already_disconnected.md)
- [test_reconnect_timeout_flips_to_ai](../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_flips_to_ai.md)
- [test_reconnect_timeout_no_op_if_websocket_returned](../../../../functions/tests/multiplayer/test_disconnect/test_reconnect_timeout_no_op_if_websocket_returned.md)
- [test_disconnect_mid_game_host_triggers_transfer_after_timeout](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_mid_game_host_triggers_transfer_after_timeout.md)
- [test_disconnect_state_event_set_wakes_awaiter](../../../../functions/tests/multiplayer/test_disconnect/test_disconnect_state_event_set_wakes_awaiter.md)
- [test_e2e_4_humans_full_game](../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_full_game.md)
- [test_e2e_4_humans_trumpf_bock_variant](../../../../functions/tests/multiplayer/test_e2e_4_humans/test_e2e_4_humans_trumpf_bock_variant.md)
- [_queue_seat_plays_first_valid](../../../../functions/tests/multiplayer/test_play_trick/_queue_seat_plays_first_valid.md)
- [test_play_trick_invalid_card_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_invalid_card_re_prompts.md)
- [test_play_trick_wrong_type_re_prompts](../../../../functions/tests/multiplayer/test_play_trick/test_play_trick_wrong_type_re_prompts.md)
- [test_reclaim_seat_cancels_pending_reconnect_task](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_cancels_pending_reconnect_task.md)
- [test_reclaim_seat_after_ai_takeover_restores_human](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_seat_after_ai_takeover_restores_human.md)
- [test_reclaim_sends_room_resume](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_sends_room_resume.md)
- [test_reclaim_broadcasts_seat_reclaimed_to_others](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_broadcasts_seat_reclaimed_to_others.md)
- [test_reclaim_state_event_set](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_state_event_set.md)
- [test_reclaim_mid_turn_resends_play_request](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_resends_play_request.md)
- [test_reclaim_mid_turn_no_play_request_when_not_active_seat](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_no_play_request_when_not_active_seat.md)
- [test_reclaim_mid_turn_lead_suit_none_when_leading](../../../../functions/tests/multiplayer/test_reclaim/test_reclaim_mid_turn_lead_suit_none_when_leading.md)
- [_queue_first_valid_for_trick](../../../../functions/tests/multiplayer/test_replay/_queue_first_valid_for_trick.md)
- [test_seat_by_position](../../../../functions/tests/multiplayer/test_seat_helpers/test_seat_by_position.md)
- [test_seat_by_position_invalid](../../../../functions/tests/multiplayer/test_seat_helpers/test_seat_by_position_invalid.md)
- [test_commit_pending_swap_swaps_principals_and_hands](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_pending_swap_swaps_principals_and_hands.md)
- [test_commit_aborts_if_either_seat_disconnected_post_accept](../../../../functions/tests/multiplayer/test_seat_swap/test_commit_aborts_if_either_seat_disconnected_post_accept.md)
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