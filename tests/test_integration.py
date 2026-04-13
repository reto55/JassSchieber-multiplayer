"""
Integration tests for the Schieber card game.
These tests verify the interaction between different modules.
"""
import unittest
import os
import sys
import sqlite3
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_utils import (
    create_connection, create_schieber, create_spieler, get_game_stats
)

from utils.card_utils import (
    sort_trumpf, add_card, move_cards
)

from utils.game_utils import (
    dauergame, format_game_duration, check_game_end
)


# Create a mock card class for testing
class MockCard:
    """Mock card class for testing."""
    
    def __init__(self, name, rank, suit, trumpf):
        """Initialize the mock card."""
        self.name = name
        self.rank = rank
        self.suit = suit
        self.trumpf = trumpf
        
    def grab_trumpf(self):
        """Get the trumpf value."""
        return self.trumpf
        
    def __repr__(self):
        """String representation."""
        return f"{self.name} of {self.suit}"


class TestIntegration(unittest.TestCase):
    """Integration test case for the Schieber card game."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create an in-memory database
        self.conn = create_connection(":memory:")
        
        # Create schema
        self._create_schema()
        
        # Set up game data
        self.game = {
            'date': datetime(2023, 1, 1, 10, 0, 0),
            'end_date': datetime(2023, 1, 1, 11, 30, 45)
        }
        
        # Set up cards
        self.cards = [
            MockCard("Sechs", 1, "Eicheln", 10),
            MockCard("Sieben", 2, "Eicheln", 11),
            MockCard("Acht", 3, "Eicheln", 12)
        ]
        
    def tearDown(self):
        """Clean up after the test."""
        if self.conn:
            self.conn.close()
            
    def _create_schema(self):
        """Create the database schema."""
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute("CREATE TABLE schieber(id INTEGER PRIMARY KEY, begin_date TEXT, end_date TEXT, end_sum INTEGER)")
        cursor.execute("CREATE TABLE spieler(id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("""
            CREATE TABLE game(
                id INTEGER PRIMARY KEY, 
                schieber_id INTEGER, 
                runde INTEGER, 
                spiel INTEGER, 
                zug INTEGER, 
                spieler_id INTEGER, 
                first TEXT, 
                operator TEXT, 
                Karte TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE play(
                id INTEGER PRIMARY KEY, 
                schieber_id INTEGER, 
                runde INTEGER, 
                spiel INTEGER, 
                zug INTEGER, 
                spieler_id INTEGER, 
                first TEXT, 
                operator TEXT, 
                realname TEXT, 
                pointOW INTEGER, 
                pointSN INTEGER, 
                Eicheln TEXT, 
                Rosen TEXT, 
                Schellen TEXT, 
                Schilten TEXT
            )
        """)
        
        self.conn.commit()
        
    def test_integration_database_and_game(self):
        """Test the integration between database and game utilities."""
        # Create a game in the database
        begin_date = self.game['date'].strftime("%Y-%m-%d %H:%M:%S")
        end_date = self.game['end_date'].strftime("%Y-%m-%d %H:%M:%S")
        end_sum = 2500
        
        game_id = create_schieber(self.conn, (begin_date, end_date, end_sum))
        
        # Add a player
        player_id = 1
        player_name = "TestPlayer"
        create_spieler(self.conn, (player_id, player_name))
        
        # Get game stats
        stats = get_game_stats(self.conn, game_id)
        
        # Calculate and format game duration
        hours, minutes, seconds = dauergame(self.game)
        formatted_duration = format_game_duration(self.game)
        
        # Check if game is over based on points
        pointSN = 2000
        pointOW = 1500
        is_game_over = check_game_end(pointSN, pointOW, end_sum)
        
        # Verify results
        self.assertEqual(stats["begin_date"], begin_date, "Begin date should match")
        self.assertEqual(stats["end_date"], end_date, "End date should match")
        self.assertEqual(stats["end_sum"], end_sum, "End sum should match")
        
        self.assertEqual(hours, 1, "Hours should be 1")
        self.assertEqual(minutes, 30, "Minutes should be 30")
        self.assertEqual(seconds, 45, "Seconds should be 45")
        
        self.assertEqual(formatted_duration, "1h 30m 45s", "Duration format should be correct")
        
        self.assertTrue(is_game_over, "Game should be over")
        
    def test_integration_card_and_game(self):
        """Test the integration between card and game utilities."""
        # Create a hand with cards
        hand = []
        
        # Add cards to the hand
        for card in self.cards:
            add_card(hand, card)
            
        # Sort the cards by trump value
        sorted_cards = sort_trumpf({"Eicheln": hand}, "Eicheln")
        
        # Verify that the hand has the correct cards
        self.assertEqual(len(hand), 3, "Hand should have 3 cards")
        self.assertEqual(hand[0].name, "Sechs", "First card should be Sechs")
        self.assertEqual(hand[1].name, "Sieben", "Second card should be Sieben")
        self.assertEqual(hand[2].name, "Acht", "Third card should be Acht")
        
        # Verify that sorting works correctly
        self.assertEqual(len(sorted_cards), 3, "Sorted cards should have 3 cards")
        self.assertEqual(sorted_cards[0].name, "Acht", "First card should be Acht (highest trump)")
        self.assertEqual(sorted_cards[1].name, "Sieben", "Second card should be Sieben")
        self.assertEqual(sorted_cards[2].name, "Sechs", "Third card should be Sechs (lowest trump)")
        
        # Move cards to a new hand
        new_hand = []
        move_cards(hand, new_hand, 2)
        
        # Verify that cards were moved correctly
        self.assertEqual(len(hand), 1, "Original hand should have 1 card")
        self.assertEqual(len(new_hand), 2, "New hand should have 2 cards")
        self.assertEqual(hand[0].name, "Acht", "Remaining card should be Acht")
        self.assertEqual(new_hand[0].name, "Sechs", "First moved card should be Sechs")
        self.assertEqual(new_hand[1].name, "Sieben", "Second moved card should be Sieben")


if __name__ == "__main__":
    unittest.main()