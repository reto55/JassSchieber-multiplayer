"""
Unit tests for database utilities.
"""
import unittest
import os
import sqlite3
from datetime import datetime
import sys

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_utils import (
    create_connection, create_game, create_play, create_schieber,
    create_spieler, create_stich, create_wwys, create_wys, update_schieber,
    get_spieler_by_id, get_game_stats
)


class TestDatabaseUtils(unittest.TestCase):
    """Test case for database utilities."""
    
    def setUp(self):
        """Set up the test environment."""
        # Use an in-memory database for testing
        self.conn = create_connection(":memory:")
        self.assertIsNotNone(self.conn, "Connection should not be None")
        
        # Create schema
        self._create_schema()
        
        # Insert test data
        self._insert_test_data()
        
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
        cursor.execute("""
            CREATE TABLE wys(
                id INTEGER PRIMARY KEY, 
                schieber_id INTEGER, 
                runde INTEGER, 
                spiel INTEGER, 
                spieler_id INTEGER, 
                first TEXT, 
                wys TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE wwys(
                id INTEGER PRIMARY KEY, 
                schieber_id INTEGER, 
                runde INTEGER, 
                spiel INTEGER, 
                spieler_id INTEGER, 
                first TEXT, 
                wwys TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE stich(
                id INTEGER PRIMARY KEY, 
                schieber_id INTEGER, 
                runde INTEGER, 
                spiel INTEGER, 
                zug INTEGER, 
                spieler_id INTEGER, 
                stich TEXT
            )
        """)
        
        self.conn.commit()
        
    def _insert_test_data(self):
        """Insert test data into the database."""
        # Insert players
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO spieler VALUES (1, 'compo')")
        cursor.execute("INSERT INTO spieler VALUES (2, 'compn')")
        cursor.execute("INSERT INTO spieler VALUES (3, 'compe')")
        cursor.execute("INSERT INTO spieler VALUES (4, 'comps')")
        
        # Insert a schieber game
        cursor.execute(
            "INSERT INTO schieber VALUES (1, '2023-01-01 10:00:00', '2023-01-01 11:00:00', 2500)"
        )
        
        self.conn.commit()
        
    def test_create_connection(self):
        """Test the create_connection function."""
        # Test with in-memory database
        conn = create_connection(":memory:")
        self.assertIsNotNone(conn, "Connection should not be None")
        
        # Test with invalid database
        bad_conn = create_connection("/invalid/path/to/db.sqlite")
        self.assertIsNone(bad_conn, "Connection should be None for invalid path")
        
    def test_create_schieber(self):
        """Test the create_schieber function."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        schieber_id = create_schieber(self.conn, (now, now, 3000))
        
        # Check if the record was created
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM schieber WHERE id = ?", (schieber_id,))
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[1], now, "Begin date should match")
        self.assertEqual(record[2], now, "End date should match")
        self.assertEqual(record[3], 3000, "End sum should match")
        
    def test_create_spieler(self):
        """Test the create_spieler function."""
        player_id = 5
        player_name = "Test Player"
        
        create_spieler(self.conn, (player_id, player_name))
        
        # Check if the record was created
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM spieler WHERE id = ?", (player_id,))
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[0], player_id, "Player ID should match")
        self.assertEqual(record[1], player_name, "Player name should match")
        
    def test_create_game(self):
        """Test the create_game function."""
        game_data = (1, 1, 1, 1, 1, "compo", "Eicheln", "[]")
        
        game_id = create_game(self.conn, game_data)
        
        # Check if the record was created
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM game WHERE id = ?", (game_id,))
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[1], 1, "Schieber ID should match")
        self.assertEqual(record[2], 1, "Runde should match")
        self.assertEqual(record[3], 1, "Spiel should match")
        self.assertEqual(record[4], 1, "Zug should match")
        self.assertEqual(record[5], 1, "Spieler ID should match")
        self.assertEqual(record[6], "compo", "First should match")
        self.assertEqual(record[7], "Eicheln", "Operator should match")
        self.assertEqual(record[8], "[]", "Karte should match")
        
    def test_create_play(self):
        """Test the create_play function."""
        play_data = (1, 1, 1, 1, 1, "compo", "Eicheln", "Player1", 0, 0, "[]", "[]", "[]", "[]")
        
        play_id = create_play(self.conn, play_data)
        
        # Check if the record was created
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM play WHERE id = ?", (play_id,))
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[1], 1, "Schieber ID should match")
        self.assertEqual(record[7], "Eicheln", "Operator should match")
        self.assertEqual(record[8], "Player1", "Realname should match")
        
    def test_create_stich(self):
        """Test the create_stich function."""
        stich_data = (1, 1, 1, 1, 1, "[]")
        
        stich_id = create_stich(self.conn, stich_data)
        
        # Check if the record was created
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM stich WHERE id = ?", (stich_id,))
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[1], 1, "Schieber ID should match")
        self.assertEqual(record[5], 1, "Spieler ID should match")
        self.assertEqual(record[6], "[]", "Stich should match")
        
    def test_create_wys(self):
        """Test the create_wys function."""
        wys_data = (1, 1, 1, 1, "compo", "50")
        
        wys_id = create_wys(self.conn, wys_data)
        
        # Check if the record was created
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM wys WHERE id = ?", (wys_id,))
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[1], 1, "Schieber ID should match")
        self.assertEqual(record[4], 1, "Spieler ID should match")
        self.assertEqual(record[5], "compo", "First should match")
        self.assertEqual(record[6], "50", "Wys should match")
        
    def test_create_wwys(self):
        """Test the create_wwys function."""
        wwys_data = (1, 1, 1, 1, "compo", "100")
        
        wwys_id = create_wwys(self.conn, wwys_data)
        
        # Check if the record was created
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM wwys WHERE id = ?", (wwys_id,))
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[1], 1, "Schieber ID should match")
        self.assertEqual(record[4], 1, "Spieler ID should match")
        self.assertEqual(record[5], "compo", "First should match")
        self.assertEqual(record[6], "100", "Wwys should match")
        
    def test_update_schieber(self):
        """Test the update_schieber function."""
        new_end_date = "2023-01-01 12:00:00"
        
        update_schieber(self.conn, (new_end_date, 1))
        
        # Check if the record was updated
        cursor = self.conn.cursor()
        cursor.execute("SELECT end_date FROM schieber WHERE id = 1")
        record = cursor.fetchone()
        
        self.assertIsNotNone(record, "Record should exist")
        self.assertEqual(record[0], new_end_date, "End date should be updated")
        
    def test_get_spieler_by_id(self):
        """Test the get_spieler_by_id function."""
        # Test with existing player
        spieler = get_spieler_by_id(self.conn, 1)
        self.assertIsNotNone(spieler, "Player should exist")
        self.assertEqual(spieler[0], 1, "Player ID should match")
        self.assertEqual(spieler[1], "compo", "Player name should match")
        
        # Test with non-existing player
        spieler = get_spieler_by_id(self.conn, 999)
        self.assertIsNone(spieler, "Player should not exist")
        
    def test_get_game_stats(self):
        """Test the get_game_stats function."""
        # Insert some play data
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO play (schieber_id, pointOW, pointSN) VALUES (1, 100, 150)"
        )
        cursor.execute(
            "INSERT INTO play (schieber_id, pointOW, pointSN) VALUES (1, 200, 250)"
        )
        self.conn.commit()
        
        # Test with existing game
        stats = get_game_stats(self.conn, 1)
        self.assertIsNotNone(stats, "Stats should exist")
        self.assertEqual(stats["begin_date"], "2023-01-01 10:00:00", "Begin date should match")
        self.assertEqual(stats["end_date"], "2023-01-01 11:00:00", "End date should match")
        self.assertEqual(stats["end_sum"], 2500, "End sum should match")
        self.assertEqual(stats["ow_points"], 200, "OW points should match")
        self.assertEqual(stats["sn_points"], 250, "SN points should match")
        
        # Test with non-existing game
        stats = get_game_stats(self.conn, 999)
        self.assertIsNone(stats, "Stats should not exist")


if __name__ == "__main__":
    unittest.main()