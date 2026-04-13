"""
Centralized imports for the Schieber card game.
Use this module to import all necessary components for the game.

This is the new version that uses the modular utils package.
"""
# Database utilities
from utils.db_utils import (
    create_connection, create_game, create_play, create_schieber,
    create_spieler, create_stich, create_wwys, create_wys, update_schieber,
    get_spieler_by_id, get_game_stats
)

# Card utilities
from utils.card_utils import (
    sort_unten, sort_oben, sort_trumpf, rsort_trumpf,
    add_card, pop_card, move_cards, grades_sum, farbe_lang
)

# Game utilities
from utils.game_utils import (
    dauergame, format_game_duration, calculate_points,
    check_game_end, get_winner, get_next_player, max_game
)

# Standard library imports
from time import sleep
from datetime import datetime

# Card imports
from Cards_refactored import (
    Schieber, weis, weis4, spsp, spieler_id,
    farb, laufen, Karten, KartenO, KartenU, KartenT, kar
)

# Make common variables available
from Cards_refactored import (
    t, end_game, restart_phrase
)

# For backward compatibility
# These will be removed in a future version
from Cards_refactored import *