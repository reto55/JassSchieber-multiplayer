"""
Example script demonstrating how to use the new utility modules.
"""
# Import database utilities
from db_utils import create_connection, create_schieber, create_spieler, get_game_stats

# Import card utilities
from card_utils import sort_trumpf, farbe_lang, grades_sum

# Import game utilities
from game_utils import format_game_duration, calculate_points, get_winner

# Import from Cards.py for game-specific objects
from Cards import Schieber, weis, spieler_id, Play

# Standard library imports
from datetime import datetime
from time import sleep


def demo_database_utils():
    """Demonstrate database utilities."""
    print("=== Database Utilities ===")
    
    # Create a connection
    conn = create_connection("example.db")
    if not conn:
        print("Failed to create database connection.")
        return
        
    print("Database connection created successfully.")
    
    # Create a new game session
    Schieber['date'] = datetime.now()
    game_id = create_schieber(conn, (Schieber['date'], Schieber['date'], 2500))
    print(f"Created new game session with ID: {game_id}")
    
    # Create a player
    player_id = create_spieler(conn, (5, "Example Player"))
    print(f"Created player with ID: {player_id}")
    
    # Get game stats
    stats = get_game_stats(conn, game_id)
    print(f"Game stats: {stats}")
    
    conn.close()
    print()


def demo_card_utils():
    """Demonstrate card utilities."""
    print("=== Card Utilities ===")
    
    # Create a dealer
    dealer = Play(1)
    
    # Sort cards by trump value
    print("Sorting cards by trump value...")
    for suit in ['Eicheln', 'Rosen', 'Schellen', 'Schilten']:
        sorted_cards = sort_trumpf(dealer.compo, suit)
        print(f"{suit}: {[card.name for card in sorted_cards]}")
    
    # Find the suit with the most cards
    longest_suit = farbe_lang(dealer.compo)
    print(f"Suit with the most cards: {longest_suit}")
    
    # Calculate sum of values
    values = [1, 5, 10, 20]
    total = grades_sum(values)
    print(f"Sum of values {values}: {total}")
    print()


def demo_game_utils():
    """Demonstrate game utilities."""
    print("=== Game Utilities ===")
    
    # Format game duration
    Schieber['date'] = datetime.now()
    # Simulate game duration of 1 hour, 30 minutes, 45 seconds
    Schieber['end_date'] = Schieber['date'].replace(
        hour=Schieber['date'].hour + 1,
        minute=Schieber['date'].minute + 30,
        second=Schieber['date'].second + 45
    )
    duration_str = format_game_duration(Schieber)
    print(f"Game duration: {duration_str}")
    
    # Demonstrate winner determination
    pointSN = 1500
    pointOW = 2000
    winner = get_winner(pointSN, pointOW)
    print(f"Game score - North-South: {pointSN}, East-West: {pointOW}")
    print(f"Winner: {winner}")
    print()


def main():
    """Run all demonstration functions."""
    print("Demonstrating the new utility modules...\n")
    
    try:
        demo_database_utils()
    except Exception as e:
        print(f"Error in database demo: {e}")
    
    try:
        demo_card_utils()
    except Exception as e:
        print(f"Error in card demo: {e}")
    
    try:
        demo_game_utils()
    except Exception as e:
        print(f"Error in game demo: {e}")
    
    print("Demonstration complete!")


if __name__ == "__main__":
    main()