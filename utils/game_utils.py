"""
Game utilities for the Schieber card game.
This module provides helper functions for game mechanics.
"""
from datetime import datetime

def game_duration(game):
    """
    Calculate the duration of a game.

    Args:
        game: Game dictionary with 'end_date' and 'date' keys

    Returns:
        Tuple of (hours, minutes, seconds)
    """
    duration = game['end_date'] - game['date']

    minutes, second = divmod(duration.seconds, 60)
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
    hours, minutes, seconds = game_duration(game)
    
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

