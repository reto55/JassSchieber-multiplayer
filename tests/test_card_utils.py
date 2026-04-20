"""
Unit tests for card utilities.
"""
import unittest
import os
import sys
from collections import namedtuple

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.card_utils import (
    sort_unten, sort_oben, sort_trumpf, rsort_trumpf,
    add_card, pop_card, move_cards, farbe_lang
)


# Create a simple Card class for testing
class MockCard:
    """Mock card class for testing."""
    
    def __init__(self, name, rank, suit, oben, unten, trumpf):
        """Initialize the mock card."""
        self.name = name
        self.rank = rank
        self.suit = suit
        self.oben = oben
        self.unten = unten
        self.trumpf = trumpf
        
    def grab_oben(self):
        """Get the oben value."""
        return self.oben
        
    def grab_unten(self):
        """Get the unten value."""
        return self.unten
        
    def grab_trumpf(self):
        """Get the trumpf value."""
        return self.trumpf
        
    def __repr__(self):
        """String representation."""
        return f"{self.name} of {self.suit}"


class TestCardUtils(unittest.TestCase):
    """Test case for card utilities."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock cards
        self.cards = [
            MockCard("Sechs", 1, "Eicheln", 1, 9, 10),
            MockCard("Sieben", 2, "Eicheln", 2, 8, 11),
            MockCard("Acht", 3, "Eicheln", 3, 7, 12),
            MockCard("Neun", 4, "Eicheln", 4, 6, 17),
            MockCard("Banner", 5, "Eicheln", 5, 5, 13),
            MockCard("Under", 6, "Eicheln", 6, 4, 18),
            MockCard("Ober", 7, "Eicheln", 7, 3, 14),
            MockCard("Koenig", 8, "Eicheln", 8, 2, 15),
            MockCard("Ass", 9, "Eicheln", 9, 1, 16)
        ]
        
        # Create a player's hand with cards in different suits
        self.player = {
            "Eicheln": [
                MockCard("Sechs", 1, "Eicheln", 1, 9, 10),
                MockCard("Neun", 4, "Eicheln", 4, 6, 17),
                MockCard("Ass", 9, "Eicheln", 9, 1, 16)
            ],
            "Rosen": [
                MockCard("Sieben", 2, "Rosen", 2, 8, 11),
                MockCard("Ober", 7, "Rosen", 7, 3, 14)
            ],
            "Schellen": [
                MockCard("Banner", 5, "Schellen", 5, 5, 13),
                MockCard("Under", 6, "Schellen", 6, 4, 18),
                MockCard("Koenig", 8, "Schellen", 8, 2, 15)
            ],
            "Schilten": [
                MockCard("Acht", 3, "Schilten", 3, 7, 12)
            ]
        }
        
    def test_sort_unten(self):
        """Test the sort_unten function."""
        sorted_cards = sort_unten(self.player, "Eicheln")
        
        # Check if cards are sorted by unten value in descending order
        self.assertEqual(len(sorted_cards), 3, "Should have 3 cards")
        self.assertEqual(sorted_cards[0].name, "Sechs", "First card should be Sechs")
        self.assertEqual(sorted_cards[1].name, "Neun", "Second card should be Neun")
        self.assertEqual(sorted_cards[2].name, "Ass", "Third card should be Ass")
        
    def test_sort_oben(self):
        """Test the sort_oben function."""
        sorted_cards = sort_oben(self.player, "Eicheln")
        
        # Check if cards are sorted by oben value in descending order
        self.assertEqual(len(sorted_cards), 3, "Should have 3 cards")
        self.assertEqual(sorted_cards[0].name, "Ass", "First card should be Ass")
        self.assertEqual(sorted_cards[1].name, "Neun", "Second card should be Neun")
        self.assertEqual(sorted_cards[2].name, "Sechs", "Third card should be Sechs")
        
    def test_sort_trumpf(self):
        """Test the sort_trumpf function."""
        sorted_cards = sort_trumpf(self.player, "Eicheln")
        
        # Check if cards are sorted by trumpf value in descending order
        self.assertEqual(len(sorted_cards), 3, "Should have 3 cards")
        self.assertEqual(sorted_cards[0].name, "Neun", "First card should be Neun")
        self.assertEqual(sorted_cards[1].name, "Ass", "Second card should be Ass")
        self.assertEqual(sorted_cards[2].name, "Sechs", "Third card should be Sechs")
        
    def test_rsort_trumpf(self):
        """Test the rsort_trumpf function."""
        sorted_cards = rsort_trumpf(self.player, "Eicheln")
        
        # Check if cards are sorted by trumpf value in ascending order
        self.assertEqual(len(sorted_cards), 3, "Should have 3 cards")
        self.assertEqual(sorted_cards[0].name, "Sechs", "First card should be Sechs")
        self.assertEqual(sorted_cards[1].name, "Ass", "Second card should be Ass")
        self.assertEqual(sorted_cards[2].name, "Neun", "Third card should be Neun")
        
    def test_add_card(self):
        """Test the add_card function."""
        hand = []
        card = MockCard("Sechs", 1, "Eicheln", 1, 9, 10)
        
        add_card(hand, card)
        
        self.assertEqual(len(hand), 1, "Hand should have 1 card")
        self.assertEqual(hand[0].name, "Sechs", "Card should be Sechs")
        
    def test_pop_card(self):
        """Test the pop_card function."""
        hand = [
            MockCard("Sechs", 1, "Eicheln", 1, 9, 10),
            MockCard("Sieben", 2, "Eicheln", 2, 8, 11)
        ]
        
        # Pop from the beginning (default)
        card = pop_card(hand)
        
        self.assertEqual(len(hand), 1, "Hand should have 1 card")
        self.assertEqual(card.name, "Sechs", "Popped card should be Sechs")
        self.assertEqual(hand[0].name, "Sieben", "Remaining card should be Sieben")
        
        # Pop from a specific index
        hand = [
            MockCard("Sechs", 1, "Eicheln", 1, 9, 10),
            MockCard("Sieben", 2, "Eicheln", 2, 8, 11)
        ]
        
        card = pop_card(hand, 1)
        
        self.assertEqual(len(hand), 1, "Hand should have 1 card")
        self.assertEqual(card.name, "Sieben", "Popped card should be Sieben")
        self.assertEqual(hand[0].name, "Sechs", "Remaining card should be Sechs")
        
    def test_move_cards(self):
        """Test the move_cards function."""
        source = [
            MockCard("Sechs", 1, "Eicheln", 1, 9, 10),
            MockCard("Sieben", 2, "Eicheln", 2, 8, 11),
            MockCard("Acht", 3, "Eicheln", 3, 7, 12)
        ]
        
        destination = []
        
        # Move 2 cards
        result = move_cards(source, destination, 2)
        
        self.assertEqual(len(source), 1, "Source should have 1 card")
        self.assertEqual(len(destination), 2, "Destination should have 2 cards")
        self.assertEqual(destination[0].name, "Sechs", "First moved card should be Sechs")
        self.assertEqual(destination[1].name, "Sieben", "Second moved card should be Sieben")
        self.assertEqual(result, destination, "Result should be the destination list")
        
    def test_farbe_lang(self):
        """Test the farbe_lang function."""
        # Test with the predefined player
        self.assertEqual(farbe_lang(self.player), "Schellen", "Schellen should be the longest suit")
        
        # Test with equal lengths, prioritizing Schilten
        player = {
            "Eicheln": [MockCard("Sechs", 1, "Eicheln", 1, 9, 10), MockCard("Sieben", 2, "Eicheln", 2, 8, 11)],
            "Rosen": [MockCard("Acht", 3, "Rosen", 3, 7, 12), MockCard("Neun", 4, "Rosen", 4, 6, 17)],
            "Schellen": [MockCard("Banner", 5, "Schellen", 5, 5, 13), MockCard("Under", 6, "Schellen", 6, 4, 18)],
            "Schilten": [MockCard("Ober", 7, "Schilten", 7, 3, 14), MockCard("Koenig", 8, "Schilten", 8, 2, 15)]
        }
        
        self.assertEqual(farbe_lang(player), "Schilten", "Schilten should be prioritized")
        
        # Test with priority: Schilten > Schellen > Eicheln > Rosen
        player = {
            "Eicheln": [MockCard("Sechs", 1, "Eicheln", 1, 9, 10), MockCard("Sieben", 2, "Eicheln", 2, 8, 11)],
            "Rosen": [MockCard("Acht", 3, "Rosen", 3, 7, 12), MockCard("Neun", 4, "Rosen", 4, 6, 17)],
            "Schellen": [],
            "Schilten": []
        }
        
        self.assertEqual(farbe_lang(player), "Eicheln", "Eicheln should be prioritized over Rosen")


if __name__ == "__main__":
    unittest.main()