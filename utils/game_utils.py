"""
Game utilities for the Schieber card game.
This module provides helper functions for game mechanics.
"""
from datetime import datetime

def dauergame(game):
    """
    Calculate the duration of a game.
    
    Args:
        game: Game dictionary with 'end_date' and 'date' keys
        
    Returns:
        Tuple of (hours, minutes, seconds)
    """
    dauer = game['end_date'] - game['date']
    
    minutes, second = divmod(dauer.seconds, 60)
    hour, minute = divmod(minutes, 60)
    return hour, minute, second

def format_game_duration(game):
    """
    Format the duration of a game as a string.
    
    Args:
        game: Game dictionary with 'end_date' and 'date' keys
        
    Returns:
        String representation of the game duration
    """
    hours, minutes, seconds = dauergame(game)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def calculate_points(stiche, operator):
    """
    Calculate points earned from a collection of tricks.
    
    Args:
        stiche: List of tricks
        operator: Trump suit or game mode
        
    Returns:
        Total points earned
    """
    total_points = 0
    
    for stich in stiche:
        for card in stich:
            # Points depend on the card value and the operator
            if operator in ['Eicheln', 'Rosen', 'Schellen', 'Schilten'] and card.suit == operator:
                # Trump suit points
                total_points += card.trumpf_value
            elif operator == 'Oben':
                # Oben mode points
                total_points += card.oben_value
            elif operator == 'Unten':
                # Unten mode points
                total_points += card.unten_value
            else:
                # Normal suit points
                total_points += card.value
                
    return total_points

def check_game_end(pointSN, pointOW, end_game):
    """
    Check if the game is over based on points.
    
    Args:
        pointSN: North-South points
        pointOW: East-West points
        end_game: Target points to end the game
        
    Returns:
        True if the game is over, False otherwise
    """
    if pointSN >= end_game or pointOW >= end_game:
        return True
    return False

def get_winner(pointSN, pointOW):
    """
    Determine the winner of the game.
    
    Args:
        pointSN: North-South points
        pointOW: East-West points
        
    Returns:
        "North-South" if North-South won, "East-West" if East-West won,
        "Tie" if the points are equal
    """
    if pointSN > pointOW:
        return "North-South"
    elif pointOW > pointSN:
        return "East-West"
    else:
        return "Tie"

def get_next_player(current_player, player_order):
    """
    Get the next player in order.
    
    Args:
        current_player: Current player
        player_order: Dictionary mapping each player to the next player
        
    Returns:
        The next player
    """
    return player_order.get(current_player)

def _card_strength(card, operator):
    """Return the ``(value, suit)``-pair used to rank a single card.

    ``value`` is the rank-in-mode that ``max_game`` puts at position 0 of its
    ``(value, player, suit)`` result tuple:

      * Trump game, trump card        → ``card.trumpf``
      * Trump game, non-trump card    → ``card.rank``
      * ``Oben`` mode                 → ``card.oben``
      * ``Unten`` mode                → ``card.unten``
    """
    if operator in ('Oben', 'Unten'):
        return card.oben if operator == 'Oben' else card.unten
    if card.suit == operator:
        return card.trumpf
    return card.rank


def _stronger_of(current, challenger, operator):
    """Return whichever of two ``(value, player, suit)`` tuples wins the trick.

    Mirrors the trick-resolution rules (see ``schieber-game-rules`` skill):

      * Trump game, suits differ: any card of ``operator`` beats a non-trump.
        Two non-trump suits → ``current`` holds (lead-suit wins over sluff).
      * Same suit (or trump mode Oben/Unten): higher rank-in-mode wins.
      * Oben/Unten, suits differ: ``current`` holds — off-suit cannot win.
    """
    cur_val, _, cur_suit = current
    new_val, _, new_suit = challenger

    if cur_suit == new_suit:
        return challenger if int(new_val) > int(cur_val) else current

    # Suits differ: only a trump can overtake in a trump game; otherwise hold.
    if operator not in ('Oben', 'Unten') and new_suit == operator:
        return challenger
    return current


def _apply_card_side_effects(dealer, player, card):
    """Record legacy-path bookkeeping: ``lastf`` and ``farben`` blanking."""
    dealer.lastf[player] = card.suit
    dealer.farben[card.suit][card.rank] = None


def _play_order(dealer, first, count):
    """Return the list of player keys in turn order, starting from ``first``."""
    order = [first]
    for _ in range(count - 1):
        order.append(dealer.folger[order[-1]])
    return order


def max_game(dealer, operator, first, game):
    """Determine the leading card/player in the trick so far.

    Called before each move (and from ``max_kard``). Walks the players in
    turn order starting at ``first`` through whichever of 1–4 of them have a
    card in ``game[player]``, folding the running winner via ``_stronger_of``.

    Side effects (preserved for the legacy path): ``dealer.lastf[p]`` is set
    to each played card's suit, and ``dealer.farben[suit][rank]`` is blanked.

    Args:
        dealer: ``Play`` (or compatible) object — supplies ``folger``,
            ``lastf``, ``farben``.
        operator: Trump suit (``'Eicheln'|'Rosen'|'Schellen'|'Schilten'``) or
            ``'Oben'`` / ``'Unten'``.
        first: Player key who led the trick.
        game: ``{player: [card] | []}`` — the cards played so far.

    Returns:
        ``(value, player, suit)`` of the currently winning card, or ``None``
        if no one has played yet.
    """
    played = [p for p in _play_order(dealer, first, 4) if game.get(p)]
    if not played:
        return None

    lead = game[played[0]][0]
    _apply_card_side_effects(dealer, played[0], lead)
    best = (_card_strength(lead, operator), played[0], lead.suit)

    for player in played[1:]:
        card = game[player][0]
        _apply_card_side_effects(dealer, player, card)
        challenger = (_card_strength(card, operator), player, card.suit)
        best = _stronger_of(best, challenger, operator)

    return best