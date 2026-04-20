"""
Unit tests for game utilities.
"""
import unittest
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.game_utils import (
    game_duration, format_game_duration, calculate_points,
    check_game_end, get_winner, get_next_player,
)


# Create a mock card class for testing
class MockCard:
    """Mock card class for testing."""
    
    def __init__(self, suit, value, trumpf_value, oben_value, unten_value):
        """Initialize the mock card."""
        self.suit = suit
        self.value = value
        self.trumpf_value = trumpf_value
        self.oben_value = oben_value
        self.unten_value = unten_value


class TestGameUtils(unittest.TestCase):
    """Test case for game utilities."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create test data
        self.game = {
            'date': datetime(2023, 1, 1, 10, 0, 0),
            'end_date': datetime(2023, 1, 1, 11, 30, 45)
        }
        
        # Create mock stiche (tricks)
        self.stiche = [
            [MockCard("Eicheln", 10, 20, 5, 2), MockCard("Rosen", 5, 10, 3, 7)],
            [MockCard("Schellen", 8, 15, 4, 6), MockCard("Schilten", 3, 8, 2, 8)]
        ]
        
    def test_game_duration(self):
        """Test the game_duration function."""
        hours, minutes, seconds = game_duration(self.game)

        self.assertEqual(hours, 1, "Hours should be 1")
        self.assertEqual(minutes, 30, "Minutes should be 30")
        self.assertEqual(seconds, 45, "Seconds should be 45")

        # Test with a shorter duration
        game = {
            'date': datetime(2023, 1, 1, 10, 0, 0),
            'end_date': datetime(2023, 1, 1, 10, 15, 30)
        }

        hours, minutes, seconds = game_duration(game)
        
        self.assertEqual(hours, 0, "Hours should be 0")
        self.assertEqual(minutes, 15, "Minutes should be 15")
        self.assertEqual(seconds, 30, "Seconds should be 30")
        
    def test_format_game_duration(self):
        """Test the format_game_duration function."""
        # Test with hours, minutes, and seconds
        formatted = format_game_duration(self.game)
        self.assertEqual(formatted, "1h 30m 45s", "Format should be correct")
        
        # Test with only minutes and seconds
        game = {
            'date': datetime(2023, 1, 1, 10, 0, 0),
            'end_date': datetime(2023, 1, 1, 10, 15, 30)
        }
        
        formatted = format_game_duration(game)
        self.assertEqual(formatted, "15m 30s", "Format should be correct")
        
        # Test with only seconds
        game = {
            'date': datetime(2023, 1, 1, 10, 0, 0),
            'end_date': datetime(2023, 1, 1, 10, 0, 45)
        }
        
        formatted = format_game_duration(game)
        self.assertEqual(formatted, "45s", "Format should be correct")
        
    def test_calculate_points(self):
        """Test the calculate_points function."""
        # Test with trump suit (Eicheln)
        points = calculate_points(self.stiche, "Eicheln")
        # Expected: 20 (Eicheln trumpf) + 5 (Rosen) + 8 (Schellen) + 3 (Schilten) = 36
        self.assertEqual(points, 36, "Points with Eicheln as trump should be 36")
        
        # Test with Oben mode
        points = calculate_points(self.stiche, "Oben")
        # Expected: 5 (Eicheln oben) + 3 (Rosen oben) + 4 (Schellen oben) + 2 (Schilten oben) = 14
        self.assertEqual(points, 14, "Points in Oben mode should be 14")
        
        # Test with Unten mode
        points = calculate_points(self.stiche, "Unten")
        # Expected: 2 (Eicheln unten) + 7 (Rosen unten) + 6 (Schellen unten) + 8 (Schilten unten) = 23
        self.assertEqual(points, 23, "Points in Unten mode should be 23")
        
    def test_check_game_end(self):
        """Test the check_game_end function."""
        # Test when game is not over
        self.assertFalse(check_game_end(1000, 1500, 2000), "Game should not be over")
        
        # Test when North-South reached the end
        self.assertTrue(check_game_end(2000, 1500, 2000), "Game should be over")
        
        # Test when East-West reached the end
        self.assertTrue(check_game_end(1500, 2000, 2000), "Game should be over")
        
        # Test when both reached the end
        self.assertTrue(check_game_end(2000, 2000, 2000), "Game should be over")
        
        # Test with exact match
        self.assertTrue(check_game_end(2000, 1999, 2000), "Game should be over")
        
    def test_get_winner(self):
        """Test the get_winner function."""
        # Test when North-South wins
        self.assertEqual(get_winner(2000, 1500), "North-South", "North-South should win")
        
        # Test when East-West wins
        self.assertEqual(get_winner(1500, 2000), "East-West", "East-West should win")
        
        # Test when it's a tie
        self.assertEqual(get_winner(2000, 2000), "Tie", "It should be a tie")
        
    def test_get_next_player(self):
        """Test the get_next_player function."""
        player_order = {
            "compo": "compn",
            "compn": "compe",
            "compe": "comps",
            "comps": "compo"
        }
        
        # Test each player transition
        self.assertEqual(get_next_player("compo", player_order), "compn", "Next after compo should be compn")
        self.assertEqual(get_next_player("compn", player_order), "compe", "Next after compn should be compe")
        self.assertEqual(get_next_player("compe", player_order), "comps", "Next after compe should be comps")
        self.assertEqual(get_next_player("comps", player_order), "compo", "Next after comps should be compo")
        
        # Test with non-existent player
        self.assertIsNone(get_next_player("invalid", player_order), "Non-existent player should return None")


if __name__ == "__main__":
    unittest.main()