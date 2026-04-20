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
    check_game_end, get_winner, get_next_player, max_game
)
from Cards_refactored import (
    Ass, Koenig, Ober, Under, Banner, Neun, Acht, Sieben, Sechs, SUITS,
    CARD_ATTRIBUTES,
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


class _FakeDealer:
    """Minimal stand-in for ``Play`` for exercising ``max_game``.

    Only the attributes that ``max_game`` touches are populated:
    ``game``, ``folger``, ``partner``, ``lastf``, ``farben``.
    """

    def __init__(self, game):
        # ``game`` maps player key -> list containing the played card (or [] if not played).
        self.game = game
        self.folger = {
            'comps': 'compo', 'compo': 'compn',
            'compn': 'compe', 'compe': 'comps',
        }
        self.partner = {
            'comps': 'compn', 'compn': 'comps',
            'compo': 'compe', 'compe': 'compo',
        }
        self.lastf = {p: '' for p in ('comps', 'compo', 'compn', 'compe')}
        self.farben = {
            s: [CARD_ATTRIBUTES[y] for y in range(1, 11)] for s in SUITS
        }


def _trick_from_plays(first, plays):
    """Build a ``dealer.game``-shaped dict from a list of (player, card) plays.

    ``plays`` is given in turn order starting with ``first``. Players who have
    not played yet receive an empty list (signalling no card). This mirrors the
    state of ``dealer.game`` at the moment ``max_game`` is called for
    1/2/3/4-player scenarios.
    """
    game = {p: [] for p in ('comps', 'compo', 'compn', 'compe')}
    for player, card in plays:
        game[player] = [card]
    return game


class TestMaxGame(unittest.TestCase):
    """Exhaustive branch coverage for ``max_game`` (trick-winner logic).

    Covers 1/2/3/4-player states × {trump, Oben, Unten} × {lead-suit, off-suit}.
    Also asserts the two side effects ``max_game`` relies on:

      * ``dealer.lastf[player]`` gets set to the suit each player's card was.
      * ``dealer.farben[suit][rank]`` of each played card becomes ``None``.
    """

    # --- 1-player (just the leader has played) ---

    def test_1p_trump_lead_is_trump_suit(self):
        card = Ass(9, 'Eicheln')
        game = _trick_from_plays('comps', [('comps', card)])
        dealer = _FakeDealer(game)
        val, winner, suit = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'comps')
        self.assertEqual(suit, 'Eicheln')
        # trump game, lead is trump → value is trumpf rank (Ass trumpf=16)
        self.assertEqual(val, 16)
        self.assertEqual(dealer.lastf['comps'], 'Eicheln')
        # max_game indexes ``farben[suit]`` by ``card.rank`` directly (1..9).
        self.assertIsNone(dealer.farben['Eicheln'][card.rank])

    def test_1p_trump_lead_is_non_trump(self):
        card = Ass(9, 'Rosen')
        game = _trick_from_plays('comps', [('comps', card)])
        dealer = _FakeDealer(game)
        val, winner, suit = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'comps')
        self.assertEqual(suit, 'Rosen')
        # non-trump lead in trump game → value is base rank (Ass rank=9)
        self.assertEqual(val, 9)

    def test_1p_oben_mode(self):
        card = Koenig(8, 'Rosen')
        game = _trick_from_plays('comps', [('comps', card)])
        dealer = _FakeDealer(game)
        val, winner, suit = max_game(dealer, 'Oben', 'comps', game)
        self.assertEqual(winner, 'comps')
        self.assertEqual(val, 8)  # Koenig.oben = 8

    def test_1p_unten_mode(self):
        card = Sechs(1, 'Rosen')
        game = _trick_from_plays('comps', [('comps', card)])
        dealer = _FakeDealer(game)
        val, winner, suit = max_game(dealer, 'Unten', 'comps', game)
        self.assertEqual(winner, 'comps')
        self.assertEqual(val, 9)  # Sechs.unten = 9 (highest in Unten)

    # --- 2-player ---

    def test_2p_trump_trump_beats_lead_suit(self):
        # Leader plays Ass of Rosen (lead), follower plays 6 of Eicheln (trump).
        lead = Ass(9, 'Rosen')
        trump = Sechs(1, 'Eicheln')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', trump)])
        dealer = _FakeDealer(game)
        _, winner, suit = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'compo')
        self.assertEqual(suit, 'Eicheln')

    def test_2p_trump_lead_suit_higher_wins(self):
        # Both play lead suit; higher rank wins.
        lead = Koenig(8, 'Rosen')
        follow = Ass(9, 'Rosen')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', follow)])
        dealer = _FakeDealer(game)
        _, winner, suit = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'compo')
        self.assertEqual(suit, 'Rosen')

    def test_2p_trump_lead_suit_lower_loses(self):
        lead = Ass(9, 'Rosen')
        follow = Koenig(8, 'Rosen')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', follow)])
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'comps')

    def test_2p_trump_off_suit_non_trump_cannot_win(self):
        # Follower sluffs a third suit — cannot beat the lead.
        lead = Sechs(1, 'Rosen')
        off = Ass(9, 'Schellen')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', off)])
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'comps')

    def test_2p_oben_off_suit_cannot_win(self):
        lead = Sechs(1, 'Rosen')
        off = Ass(9, 'Schellen')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', off)])
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Oben', 'comps', game)
        self.assertEqual(winner, 'comps')

    def test_2p_oben_lead_suit_higher_wins(self):
        lead = Koenig(8, 'Rosen')
        follow = Ass(9, 'Rosen')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', follow)])
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Oben', 'comps', game)
        self.assertEqual(winner, 'compo')

    def test_2p_unten_sechs_beats_ass(self):
        # In Unten, Sechs has unten=9 (highest), Ass has unten=1 (lowest).
        lead = Ass(9, 'Rosen')
        follow = Sechs(1, 'Rosen')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', follow)])
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Unten', 'comps', game)
        self.assertEqual(winner, 'compo')

    def test_2p_sets_lastf_for_both_players(self):
        lead = Ass(9, 'Rosen')
        follow = Koenig(8, 'Eicheln')
        game = _trick_from_plays('comps', [('comps', lead), ('compo', follow)])
        dealer = _FakeDealer(game)
        max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(dealer.lastf['comps'], 'Rosen')
        self.assertEqual(dealer.lastf['compo'], 'Eicheln')

    # --- 3-player ---

    def test_3p_trump_trumps_another_winning_lead(self):
        lead = Ass(9, 'Rosen')
        follower = Koenig(8, 'Rosen')  # higher lead-suit card would win so far
        partner_card = Sechs(1, 'Eicheln')  # but partner plays trump
        game = _trick_from_plays(
            'comps',
            [('comps', lead), ('compo', follower), ('compn', partner_card)],
        )
        dealer = _FakeDealer(game)
        _, winner, suit = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'compn')
        self.assertEqual(suit, 'Eicheln')

    def test_3p_trump_higher_trump_overtakes(self):
        # comps leads Rosen, compo trumps with Eicheln low, compn overtrumps.
        lead = Ass(9, 'Rosen')
        t1 = Sechs(1, 'Eicheln')  # trumpf=10
        t2 = Under(6, 'Eicheln')  # trumpf=18 (highest trump)
        game = _trick_from_plays(
            'comps', [('comps', lead), ('compo', t1), ('compn', t2)]
        )
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'compn')

    def test_3p_oben_running_max_among_lead_suit(self):
        a = Neun(4, 'Rosen')
        b = Banner(5, 'Rosen')
        c = Ober(7, 'Rosen')
        game = _trick_from_plays(
            'comps', [('comps', a), ('compo', b), ('compn', c)]
        )
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Oben', 'comps', game)
        self.assertEqual(winner, 'compn')

    def test_3p_unten_lowest_oben_wins(self):
        # Sechs has unten=9 → highest. Others Sieben=8, Acht=7.
        sechs = Sechs(1, 'Rosen')
        sieben = Sieben(2, 'Rosen')
        acht = Acht(3, 'Rosen')
        game = _trick_from_plays(
            'comps', [('comps', acht), ('compo', sieben), ('compn', sechs)]
        )
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Unten', 'comps', game)
        self.assertEqual(winner, 'compn')

    # --- 4-player ---

    def test_4p_trump_highest_trump_wins(self):
        lead = Ass(9, 'Rosen')
        other = Koenig(8, 'Rosen')
        t_low = Sechs(1, 'Eicheln')
        t_high = Neun(4, 'Eicheln')  # trumpf=17 (2nd-highest trump)
        game = _trick_from_plays(
            'comps',
            [('comps', lead), ('compo', t_low),
             ('compn', other), ('compe', t_high)],
        )
        dealer = _FakeDealer(game)
        _, winner, suit = max_game(dealer, 'Eicheln', 'comps', game)
        self.assertEqual(winner, 'compe')
        self.assertEqual(suit, 'Eicheln')

    def test_4p_oben_highest_lead_suit_wins(self):
        cards = [Neun(4, 'Rosen'), Banner(5, 'Rosen'),
                 Ober(7, 'Rosen'), Ass(9, 'Rosen')]
        players = ['comps', 'compo', 'compn', 'compe']
        game = _trick_from_plays('comps', list(zip(players, cards)))
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Oben', 'comps', game)
        self.assertEqual(winner, 'compe')  # Ass highest

    def test_4p_unten_sechs_wins(self):
        cards = [Ass(9, 'Rosen'), Koenig(8, 'Rosen'),
                 Ober(7, 'Rosen'), Sechs(1, 'Rosen')]
        players = ['comps', 'compo', 'compn', 'compe']
        game = _trick_from_plays('comps', list(zip(players, cards)))
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Unten', 'comps', game)
        self.assertEqual(winner, 'compe')

    def test_4p_all_off_suit_leader_holds(self):
        # Oben mode, leader plays a low lead-suit card; everyone else sluffs.
        lead = Sechs(1, 'Rosen')
        cards = [lead, Ass(9, 'Eicheln'), Ass(9, 'Schellen'), Ass(9, 'Schilten')]
        players = ['comps', 'compo', 'compn', 'compe']
        game = _trick_from_plays('comps', list(zip(players, cards)))
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Oben', 'comps', game)
        self.assertEqual(winner, 'comps')

    def test_4p_side_effects_all_players(self):
        cards = [Ass(9, 'Rosen'), Koenig(8, 'Rosen'),
                 Ober(7, 'Eicheln'), Sechs(1, 'Schellen')]
        players = ['comps', 'compo', 'compn', 'compe']
        game = _trick_from_plays('comps', list(zip(players, cards)))
        dealer = _FakeDealer(game)
        max_game(dealer, 'Eicheln', 'comps', game)
        # Each player's lastf is their card's suit.
        self.assertEqual(dealer.lastf['comps'], 'Rosen')
        self.assertEqual(dealer.lastf['compo'], 'Rosen')
        self.assertEqual(dealer.lastf['compn'], 'Eicheln')
        self.assertEqual(dealer.lastf['compe'], 'Schellen')
        # Each played card is blanked in ``farben`` by its rank slot.
        for card in cards:
            self.assertIsNone(dealer.farben[card.suit][card.rank])

    def test_4p_starter_not_comps(self):
        # Verify it works regardless of who leads — use compo as first.
        cards = [Ass(9, 'Rosen'), Koenig(8, 'Rosen'),
                 Ober(7, 'Rosen'), Banner(5, 'Rosen')]
        players = ['compo', 'compn', 'compe', 'comps']  # folger order from compo
        game = _trick_from_plays('compo', list(zip(players, cards)))
        dealer = _FakeDealer(game)
        _, winner, _ = max_game(dealer, 'Eicheln', 'compo', game)
        self.assertEqual(winner, 'compo')  # Ass highest in lead Rosen


if __name__ == "__main__":
    unittest.main()