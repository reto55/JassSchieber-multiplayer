---
type: Python Module
title: game_session
resource: ausbau/game_session.py#L1-L1581
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/sys
  - external/os
  - external/asyncio
  - external/time
  - external/typing
  - external/cards-refactored
  - external/utils-game-utils
  - external/ausbau-room
  - external/ausbau-ai-strategies
  - external/logging
---

# Contains

- [card_to_code](../../functions/ausbau/game_session/card_to_code.md)
- [hand_to_codes](../../functions/ausbau/game_session/hand_to_codes.md)
- [find_card_in_hand](../../functions/ausbau/game_session/find_card_in_hand.md)
- [code_to_card](../../functions/ausbau/game_session/code_to_card.md)
- [get_valid_cards](../../functions/ausbau/game_session/get_valid_cards.md)
- [determine_trick_winner](../../functions/ausbau/game_session/determine_trick_winner.md)
- [strength](../../functions/ausbau/game_session/strength.md)
- [_mode_multiplier](../../functions/ausbau/game_session/_mode_multiplier.md)
- [trick_points](../../functions/ausbau/game_session/trick_points.md)
- [ai_select_card](../../functions/ausbau/game_session/ai_select_card.md)
- [point_value](../../functions/ausbau/game_session/point_value.md)
- [describe_weis](../../functions/ausbau/game_session/describe_weis.md)
- [detect_stock](../../functions/ausbau/game_session/detect_stock.md)
- [GameSession](../../classes/ausbau/game_session/GameSession.md)
- [__init__](../../functions/ausbau/game_session/GameSession/__init__.md)
- [_seat](../../functions/ausbau/game_session/GameSession/_seat.md)
- [_seat_for_principal](../../functions/ausbau/game_session/GameSession/_seat_for_principal.md)
- [_spectator_for_principal](../../functions/ausbau/game_session/GameSession/_spectator_for_principal.md)
- [_seat_to_dict](../../functions/ausbau/game_session/GameSession/_seat_to_dict.md)
- [_seated_human_count](../../functions/ausbau/game_session/GameSession/_seated_human_count.md)
- [_connected_human_count](../../functions/ausbau/game_session/GameSession/_connected_human_count.md)
- [_update_idle_since](../../functions/ausbau/game_session/GameSession/_update_idle_since.md)
- [_transfer_host](../../functions/ausbau/game_session/GameSession/_transfer_host.md)
- [send_to_seat](../../functions/ausbau/game_session/GameSession/send_to_seat.md)
- [broadcast](../../functions/ausbau/game_session/GameSession/broadcast.md)
- [broadcast_per_seat](../../functions/ausbau/game_session/GameSession/broadcast_per_seat.md)
- [_disconnect_seat](../../functions/ausbau/game_session/GameSession/_disconnect_seat.md)
- [_reconnect_timeout](../../functions/ausbau/game_session/GameSession/_reconnect_timeout.md)
- [_reclaim_seat](../../functions/ausbau/game_session/GameSession/_reclaim_seat.md)
- [_lead_suit_from_trick_so_far](../../functions/ausbau/game_session/GameSession/_lead_suit_from_trick_so_far.md)
- [_has_connected_host](../../functions/ausbau/game_session/GameSession/_has_connected_host.md)
- [_record_seat_swap_request](../../functions/ausbau/game_session/GameSession/_record_seat_swap_request.md)
- [_seat_swap_timeout](../../functions/ausbau/game_session/GameSession/_seat_swap_timeout.md)
- [_accept_seat_swap](../../functions/ausbau/game_session/GameSession/_accept_seat_swap.md)
- [_commit_pending_swap](../../functions/ausbau/game_session/GameSession/_commit_pending_swap.md)
- [_room_resume_message_for](../../functions/ausbau/game_session/GameSession/_room_resume_message_for.md)
- [_initial_state](../../functions/ausbau/game_session/GameSession/_initial_state.md)
- [_trump_phase](../../functions/ausbau/game_session/GameSession/_trump_phase.md)
- [_partner_of](../../functions/ausbau/game_session/GameSession/_partner_of.md)
- [_await_seat_action](../../functions/ausbau/game_session/GameSession/_await_seat_action.md)
- [_compute_ai_action](../../functions/ausbau/game_session/GameSession/_compute_ai_action.md)
- [_weis_phase](../../functions/ausbau/game_session/GameSession/_weis_phase.md)
- [_play_trick](../../functions/ausbau/game_session/GameSession/_play_trick.md)
- [_reset_spiel_trick_winners](../../functions/ausbau/game_session/GameSession/_reset_spiel_trick_winners.md)
- [_apply_match_bonus](../../functions/ausbau/game_session/GameSession/_apply_match_bonus.md)
- [_apply_stoeck](../../functions/ausbau/game_session/GameSession/_apply_stoeck.md)
- [_game_start_for](../../functions/ausbau/game_session/GameSession/_game_start_for.md)
- [_run_spiel](../../functions/ausbau/game_session/GameSession/_run_spiel.md)
- [_factory](../../functions/ausbau/game_session/_factory.md)
- [start_game](../../functions/ausbau/game_session/GameSession/start_game.md)

# Imports

- `sys`
- `os`
- `asyncio`
- `time`
- `typing`
- `Cards_refactored`
- `utils.game_utils`
- `ausbau.room`
- `ausbau.ai_strategies`
- `logging`