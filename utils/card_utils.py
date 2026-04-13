"""
Card utilities for the Schieber card game.
This module provides helper functions for card sorting and manipulation.
"""

def sort_unten(spieler, suit):
    """
    Sort cards using the "unten" (bottom) value in descending order.
    
    Args:
        spieler: Player's cards
        suit: The suit to sort
        
    Returns:
        Sorted list of cards (highest first)
    """
    return sorted(spieler[suit], key=lambda xy: xy.grab_unten(), reverse=True)

def sort_oben(spieler, suit):
    """
    Sort cards using the "oben" (top) value in descending order.
    
    Args:
        spieler: Player's cards
        suit: The suit to sort
        
    Returns:
        Sorted list of cards (highest first)
    """
    return sorted(spieler[suit], key=lambda xy: xy.grab_oben(), reverse=True)

def sort_trumpf(spieler, suit):
    """
    Sort cards using the trump value in descending order.
    
    Args:
        spieler: Player's cards
        suit: The suit to sort
        
    Returns:
        Sorted list of cards (highest first)
    """
    return sorted(spieler[suit], key=lambda xy: xy.grab_trumpf(), reverse=True)

def rsort_trumpf(spieler, suit):
    """
    Sort cards using the trump value in ascending order.
    
    Args:
        spieler: Player's cards
        suit: The suit to sort
        
    Returns:
        Sorted list of cards (lowest first)
    """
    return sorted(spieler[suit], key=lambda xy: xy.grab_trumpf(), reverse=False)

def add_card(hand, card):
    """
    Add a card to a hand.
    
    Args:
        hand: The hand to add to
        card: The card to add
    """
    hand.append(card)

def pop_card(cards, i=0):
    """
    Remove and return a card from a list of cards.
    
    Args:
        cards: List of cards
        i: Index of the card to remove (default: 0)
        
    Returns:
        The removed card
    """
    return cards.pop(i)

def move_cards(cards, sp1, num):
    """
    Move multiple cards from one list to another.
    
    Args:
        cards: Source list of cards
        sp1: Destination list
        num: Number of cards to move
        
    Returns:
        The updated destination list
    """
    for u in range(num):
        add_card(sp1, pop_card(cards))
    return sp1

def grades_sum(grades):
    """
    Calculate the sum of values in a list.
    
    Args:
        grades: List of values
        
    Returns:
        Sum of the values
    """
    total = 0
    for grade in grades:
        total += grade
    return total

def farbe_lang(spieler):
    """
    Determine which suit has the most cards for a player.
    If multiple suits have the same number of cards, prioritize in order:
    Schilten > Schellen > Eicheln > Rosen
    
    Args:
        spieler: Player's cards
        
    Returns:
        The suit with the most cards
    """
    ei = set()
    ro = set()
    se = set()
    si = set()
    
    for value in spieler['Eicheln']:
        ei.add(value.oben)
    for value in spieler['Rosen']:
        ro.add(value.oben)
    for value in spieler['Schellen']:
        se.add(value.oben)
    for value in spieler['Schilten']:
        si.add(value.oben)
        
    max_len = len(ro)
    if max_len < len(ei) or max_len == len(ei):
        max_len = len(ei)
        if max_len < len(se) or max_len == len(se):
            max_len = len(se)
            if max_len < len(si) or max_len == len(si):
                return 'Schilten'
            else:
                return 'Schellen'
        elif max_len < len(si) or max_len == len(si):
            return 'Schilten'
        else:
            return 'Eicheln'
    elif max_len < len(se) or max_len == len(se):
        max_len = len(se)
        if max_len < len(si) or max_len == len(si):
            return 'Schilten'
        else:
            return 'Schellen'
    elif max_len < len(si) or max_len == len(si):
        return 'Schilten'
    else:
        return 'Rosen'