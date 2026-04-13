"""
Example usage of the new DatabaseManager for the Schieber Card Game.
This script demonstrates how to use the new database layer.
"""
from database_manager import DatabaseManager
from datetime import datetime


def demonstrate_basic_operations():
    """Show basic database operations."""
    # Create a database manager instance
    db = DatabaseManager("example_schieber.db")
    db.connect()
    
    # Create schema
    db.create_schema()
    
    # Create a new game session
    print("Creating a new game session...")
    game_id = db.create_schieber_game(end_sum=2500)
    print(f"Created game with ID: {game_id}")
    
    # Add a new player
    print("Adding a new player...")
    db.execute_query(
        "INSERT INTO spieler (id, name) VALUES (?, ?)", 
        (5, "PlayerExample"),
        commit=True
    )
    
    # Get player by ID
    player = db.get_player_by_id(5)
    print(f"Retrieved player: {player}")
    
    # Create sample play record
    print("Creating a sample play record...")
    play_id = db.create_play_record(
        schieber_id=game_id,
        runde=1,
        spiel=1,
        zug=1,
        spieler_id=1,
        first="compo",
        operator="Eicheln",
        realname="Computer Ost",
        pointOW=0,
        pointSN=0,
        eicheln="[]",
        rosen="[]",
        schellen="[]",
        schilten="[]"
    )
    print(f"Created play record with ID: {play_id}")
    
    # Update game end date
    print("Updating game end date...")
    db.update_schieber_game_end(game_id)
    
    # Get game stats
    print("Getting game stats...")
    stats = db.get_game_stats(game_id)
    print(f"Game stats: {stats}")
    
    # Close the connection
    db.close()
    print("Database connection closed.")


def demonstrate_transaction():
    """Show how to use transactions."""
    db = DatabaseManager("example_schieber.db")
    db.connect()
    
    print("Demonstrating transaction handling...")
    
    # Start a transaction manually
    db.conn.execute("BEGIN TRANSACTION")
    
    try:
        # Create a new game session
        game_id = db.create_schieber_game(end_sum=1500)
        print(f"Created game with ID: {game_id}")
        
        # Create multiple records in the same transaction
        for i in range(1, 5):
            db.create_play_record(
                schieber_id=game_id,
                runde=1,
                spiel=1,
                zug=i,
                spieler_id=i,
                first="compo",
                operator="Eicheln",
                realname=f"Player {i}",
                pointOW=i * 10,
                pointSN=i * 20,
                eicheln="[]",
                rosen="[]",
                schellen="[]",
                schilten="[]"
            )
        
        # Commit the transaction
        db.conn.commit()
        print("Transaction committed successfully.")
    
    except Exception as e:
        # Rollback in case of error
        db.conn.rollback()
        print(f"Transaction failed, rolled back: {e}")
    
    # Close the connection
    db.close()


def demonstrate_context_manager():
    """Show how to use the database manager as a context manager."""
    print("Demonstrating context manager usage...")
    
    # Use with statement to automatically handle connection
    with DatabaseManager("example_schieber.db") as db:
        # Query for highest game ID
        last_game_id = db.get_last_game_id()
        print(f"Last game ID: {last_game_id}")
        
        # Query for total number of games
        result = db.fetch_one("SELECT COUNT(*) FROM schieber")
        print(f"Total number of games: {result[0]}")


if __name__ == "__main__":
    demonstrate_basic_operations()
    print("\n" + "-" * 50 + "\n")
    demonstrate_transaction()
    print("\n" + "-" * 50 + "\n")
    demonstrate_context_manager()
    
    print("\nDatabase examples completed successfully.")
    
    # Clean up example database
    import os
    if os.path.exists("example_schieber.db"):
        user_input = input("Remove example database? (y/n): ")
        if user_input.lower() == 'y':
            os.remove("example_schieber.db")
            print("Example database removed.")