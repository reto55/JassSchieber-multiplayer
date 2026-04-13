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

def max_game(dealer, operator, first, game):
    """
    Determine the highest card in the current game state.
    
    This function is called before each move and from max_kard.
    It sets played cards in the farben dictionary to None.
    It returns the current highest card with player and suit information.
    It sets lastf[first] to the suit of the first card.
    
    Args:
        dealer: The dealer object
        operator: Trump suit or game mode
        first: First player
        game: Current game state
        
    Returns:
        Highest card information
    """
    dealer.lastf[first] = dealer.game[first][0].suit
    
    def game1(operator, first, game):
        if operator != 'Unten' and operator != 'Oben':
            if game[first][0].suit == operator:
                max_ = (game[first][0].trumpf, first, game[first][0].suit)
                dealer.farben[game[first][0].suit][game[first][0].rank] = None
                return max_
            else:
                max_ = (game[first][0].rank, first, game[first][0].suit)
                dealer.farben[game[first][0].suit][game[first][0].rank] = None
                return max_
        elif operator == 'Oben':
            max_ = (game[first][0].oben, first, game[first][0].suit)
            dealer.farben[game[first][0].suit][game[first][0].rank] = None
            return max_
        elif operator == 'Unten':
            max_ = (game[first][0].unten, first, game[first][0].suit)
            dealer.farben[game[first][0].suit][game[first][0].rank] = None
            return max_

    def game2(operator, first, game):
        dealer.lastf[dealer.folger[first]] = dealer.game[dealer.folger[first]][0].suit
        gross = list()
        dealer.farben[game[dealer.folger[first]][0].suit][game[dealer.folger[first]][0].rank] = None
        gama = game.copy()
        gamb = game.copy()
        gama[dealer.folger[first]] = ''
        gamb[first] = ''
        gross.append(game1(operator=operator, first=first, game=gama))
        gross.append(game1(operator=operator, first=dealer.folger[first], game=gamb))
        
        if (gross[1][2] != gross[0][2]) and (operator != 'Unten' and 'Oben' != operator):
            if gross[0][2] != operator and gross[1][2] != operator:
                max_ = gross[0]
            elif gross[0][2] != operator and gross[1][2] == operator:
                max_ = gross[1]
            elif gross[0][2] == operator and gross[1][2] != operator:
                max_ = gross[0]
        elif (gross[1][2] == gross[0][2]) and (operator != 'Unten' and 'Oben' != operator):
            max_ = max(gross, key=lambda xy: int(xy[0]))
        elif (gross[1][2] == gross[0][2]) and (operator == 'Unten' or 'Oben' == operator):
            max_ = max(gross, key=lambda xy: int(xy[0]))
        elif (gross[1][2] != gross[0][2]) and (operator == 'Unten' or 'Oben' == operator):
            max_ = gross[0]
            
        return max_

    def game3(operator, first, game):
        dealer.lastf[dealer.partner[first]] = dealer.game[dealer.partner[first]][0].suit
        gross = list()
        dealer.farben[game[dealer.partner[first]][0].suit][game[dealer.partner[first]][0].rank] = None
        gama = game.copy()
        gamb = game.copy()
        gamc = game.copy()
        gama[dealer.partner[first]] = ''
        gamb[first] = ''
        gamc[dealer.folger[first]] = ''
        
        # Calculate max for first and partner
        max_first_partner = game2(operator=operator, first=first, game=gama)
        
        # Calculate max for partner
        gross.append(max_first_partner)
        gross.append(game1(operator=operator, first=dealer.partner[first], game=gamb))
        
        if (gross[1][2] != gross[0][2]) and (operator != 'Unten' and 'Oben' != operator):
            if gross[0][2] != operator and gross[1][2] != operator:
                max_ = gross[0]
            elif gross[0][2] != operator and gross[1][2] == operator:
                max_ = gross[1]
            elif gross[0][2] == operator and gross[1][2] != operator:
                max_ = gross[0]
        elif (gross[1][2] == gross[0][2]) and (operator != 'Unten' and 'Oben' != operator):
            max_ = max(gross, key=lambda xy: int(xy[0]))
        elif (gross[1][2] == gross[0][2]) and (operator == 'Unten' or 'Oben' == operator):
            max_ = max(gross, key=lambda xy: int(xy[0]))
        elif (gross[1][2] != gross[0][2]) and (operator == 'Unten' or 'Oben' == operator):
            max_ = gross[0]
            
        return max_

    def game4(operator, first, game):
        dealer.lastf[dealer.folger[dealer.partner[first]]] = dealer.game[dealer.folger[dealer.partner[first]]][0].suit
        gross = list()
        dealer.farben[game[dealer.folger[dealer.partner[first]]][0].suit][game[dealer.folger[dealer.partner[first]]][0].rank] = None
        gama = game.copy()
        gamb = game.copy()
        gama[dealer.folger[dealer.partner[first]]] = ''
        
        # Calculate max for first three players
        max_first_three = game3(operator=operator, first=first, game=gama)
        
        # Calculate max for all four players
        gross.append(max_first_three)
        gross.append(game1(operator=operator, first=dealer.folger[dealer.partner[first]], game=gamb))
        
        if (gross[1][2] != gross[0][2]) and (operator != 'Unten' and 'Oben' != operator):
            if gross[0][2] != operator and gross[1][2] != operator:
                max_ = gross[0]
            elif gross[0][2] != operator and gross[1][2] == operator:
                max_ = gross[1]
            elif gross[0][2] == operator and gross[1][2] != operator:
                max_ = gross[0]
        elif (gross[1][2] == gross[0][2]) and (operator != 'Unten' and 'Oben' != operator):
            max_ = max(gross, key=lambda xy: int(xy[0]))
        elif (gross[1][2] == gross[0][2]) and (operator == 'Unten' or 'Oben' == operator):
            max_ = max(gross, key=lambda xy: int(xy[0]))
        elif (gross[1][2] != gross[0][2]) and (operator == 'Unten' or 'Oben' == operator):
            max_ = gross[0]
            
        return max_

    # Process based on number of players with cards
    players_with_cards = sum(1 for p in game.values() if p)
    
    if players_with_cards == 1:
        return game1(operator, first, game)
    elif players_with_cards == 2:
        return game2(operator, first, game)
    elif players_with_cards == 3:
        return game3(operator, first, game)
    elif players_with_cards == 4:
        return game4(operator, first, game)
    else:
        return None