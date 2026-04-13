"""
Database Manager for Schieber Card Game.
Provides a clean, object-oriented interface for all database operations.
"""
import sqlite3
from sqlite3 import Error
import os
from datetime import datetime


class DatabaseManager:
    """
    Manages all database operations for the Schieber card game.
    Provides connection handling, schema creation, and CRUD operations.
    """
    
    def __init__(self, db_path='schieber.db'):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """
        Create a database connection to the SQLite database.
        
        Returns:
            Connection object or None
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            return self.conn
        except Error as e:
            print(f"Database connection error: {e}")
            return None
            
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def __enter__(self):
        """Context manager entry point."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()
        
    def execute_query(self, query, params=None, commit=False):
        """
        Execute a SQL query.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
            commit (bool): Whether to commit after execution
            
        Returns:
            Cursor object or None
        """
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if commit:
                self.conn.commit()
                
            return cursor
        except Error as e:
            print(f"Query execution error: {e}")
            return None
            
    def execute_many(self, query, params_list, commit=True):
        """
        Execute many queries.
        
        Args:
            query (str): SQL query template
            params_list (list): List of parameter tuples
            commit (bool): Whether to commit after execution
            
        Returns:
            Cursor object or None
        """
        if not self.conn:
            self.connect()
            
        try:
            cursor = self.conn.cursor()
            cursor.executemany(query, params_list)
            
            if commit:
                self.conn.commit()
                
            return cursor
        except Error as e:
            print(f"Query execution error: {e}")
            return None
            
    def fetch_all(self, query, params=None):
        """
        Execute a query and fetch all results.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
            
        Returns:
            List of rows or None
        """
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return None
        
    def fetch_one(self, query, params=None):
        """
        Execute a query and fetch one result.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
            
        Returns:
            Row or None
        """
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None
    
    def create_schema(self):
        """Create the database schema if it doesn't exist."""
        if not self.conn:
            self.connect()
            
        # Check if tables already exist
        tables = self.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        
        if tables and len(tables) > 0:
            print("Schema already exists.")
            return
            
        # Create tables
        schema_queries = [
            """
            CREATE TABLE schieber(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                begin_date TEXT,
                end_date TEXT,
                end_sum INTEGER
            )
            """,
            """
            CREATE TABLE spieler(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE game(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schieber_id INTEGER,
                runde INTEGER,
                spiel INTEGER,
                zug INTEGER,
                spieler_id INTEGER,
                first TEXT,
                operator TEXT,
                Karte TEXT,
                FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                FOREIGN KEY (spieler_id) REFERENCES spieler (id)
            )
            """,
            """
            CREATE TABLE play(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                Schilten TEXT,
                FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                FOREIGN KEY (spieler_id) REFERENCES spieler (id)
            )
            """,
            """
            CREATE TABLE wys(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schieber_id INTEGER,
                runde INTEGER,
                spiel INTEGER,
                spieler_id INTEGER,
                first TEXT,
                wys TEXT,
                FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                FOREIGN KEY (spieler_id) REFERENCES spieler (id)
            )
            """,
            """
            CREATE TABLE wwys(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schieber_id INTEGER,
                runde INTEGER,
                spiel INTEGER,
                spieler_id INTEGER,
                first TEXT,
                wwys TEXT,
                FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                FOREIGN KEY (spieler_id) REFERENCES spieler (id)
            )
            """,
            """
            CREATE TABLE stich(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schieber_id INTEGER,
                runde INTEGER,
                spiel INTEGER,
                zug INTEGER,
                spieler_id INTEGER,
                stich TEXT,
                FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                FOREIGN KEY (spieler_id) REFERENCES spieler (id)
            )
            """
        ]
        
        # Execute all schema creation queries in a transaction
        try:
            self.conn.execute("BEGIN TRANSACTION")
            
            for query in schema_queries:
                self.execute_query(query)
                
            # Insert default players
            self.execute_query("INSERT INTO spieler VALUES(1, 'compo')", commit=False)
            self.execute_query("INSERT INTO spieler VALUES(2, 'compn')", commit=False)
            self.execute_query("INSERT INTO spieler VALUES(3, 'compe')", commit=False)
            self.execute_query("INSERT INTO spieler VALUES(4, 'comps')", commit=False)
            
            self.conn.commit()
            print("Schema created successfully.")
        except Error as e:
            self.conn.rollback()
            print(f"Schema creation error: {e}")
    
    # Game operations
    def create_schieber_game(self, end_sum=0):
        """
        Create a new Schieber game session.
        
        Args:
            end_sum (int): End sum target for the game
            
        Returns:
            int: The ID of the created game or None if failed
        """
        begin_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        end_date = None
        
        query = "INSERT INTO schieber (begin_date, end_date, end_sum) VALUES (?, ?, ?)"
        cursor = self.execute_query(query, (begin_date, end_date, end_sum), commit=True)
        
        if cursor:
            return cursor.lastrowid
        return None
        
    def update_schieber_game_end(self, schieber_id):
        """
        Update the end date of a Schieber game.
        
        Args:
            schieber_id (int): ID of the game to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "UPDATE schieber SET end_date = ? WHERE id = ?"
        cursor = self.execute_query(query, (end_date, schieber_id), commit=True)
        
        if cursor and cursor.rowcount > 0:
            return True
        return False
        
    def create_game_record(self, schieber_id, runde, spiel, zug, spieler_id, first, operator, karte):
        """
        Create a new game record.
        
        Args:
            schieber_id (int): ID of the Schieber game
            runde (int): Round number
            spiel (int): Game number
            zug (int): Move number
            spieler_id (int): ID of the player
            first (str): First player
            operator (str): Operator (trump)
            karte (str): Card played in JSON format
            
        Returns:
            int: ID of the created record or None if failed
        """
        query = """
        INSERT INTO game (schieber_id, runde, spiel, zug, spieler_id, first, operator, Karte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.execute_query(
            query,
            (schieber_id, runde, spiel, zug, spieler_id, first, operator, karte),
            commit=True
        )
        
        if cursor:
            return cursor.lastrowid
        return None
        
    def create_play_record(self, schieber_id, runde, spiel, zug, spieler_id, first, operator, 
                          realname, pointOW, pointSN, eicheln, rosen, schellen, schilten):
        """
        Create a new play record.
        
        Args:
            schieber_id (int): ID of the Schieber game
            runde (int): Round number
            spiel (int): Game number
            zug (int): Move number
            spieler_id (int): ID of the player
            first (str): First player
            operator (str): Operator (trump)
            realname (str): Real name of the player
            pointOW (int): Points for East-West
            pointSN (int): Points for North-South
            eicheln (str): Eicheln cards in JSON format
            rosen (str): Rosen cards in JSON format
            schellen (str): Schellen cards in JSON format
            schilten (str): Schilten cards in JSON format
            
        Returns:
            int: ID of the created record or None if failed
        """
        query = """
        INSERT INTO play (schieber_id, runde, spiel, zug, spieler_id, first, operator, realname, 
                         pointOW, pointSN, Eicheln, Rosen, Schellen, Schilten)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.execute_query(
            query,
            (schieber_id, runde, spiel, zug, spieler_id, first, operator, realname,
             pointOW, pointSN, eicheln, rosen, schellen, schilten),
            commit=True
        )
        
        if cursor:
            return cursor.lastrowid
        return None
        
    def create_stich_record(self, schieber_id, runde, spiel, zug, spieler_id, stich):
        """
        Create a new stich (trick) record.
        
        Args:
            schieber_id (int): ID of the Schieber game
            runde (int): Round number
            spiel (int): Game number
            zug (int): Move number
            spieler_id (int): ID of the player
            stich (str): Stich (trick) in JSON format
            
        Returns:
            int: ID of the created record or None if failed
        """
        query = """
        INSERT INTO stich (schieber_id, runde, spiel, zug, spieler_id, stich)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.execute_query(
            query,
            (schieber_id, runde, spiel, zug, spieler_id, stich),
            commit=True
        )
        
        if cursor:
            return cursor.lastrowid
        return None
        
    def create_wys_record(self, schieber_id, runde, spiel, spieler_id, first, wys):
        """
        Create a new wys record.
        
        Args:
            schieber_id (int): ID of the Schieber game
            runde (int): Round number
            spiel (int): Game number
            spieler_id (int): ID of the player
            first (str): First player
            wys (str): Wys (scoring) in JSON format
            
        Returns:
            int: ID of the created record or None if failed
        """
        query = """
        INSERT INTO wys (schieber_id, runde, spiel, spieler_id, first, wys)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.execute_query(
            query,
            (schieber_id, runde, spiel, spieler_id, first, wys),
            commit=True
        )
        
        if cursor:
            return cursor.lastrowid
        return None
        
    def create_wwys_record(self, schieber_id, runde, spiel, spieler_id, first, wwys):
        """
        Create a new wwys record.
        
        Args:
            schieber_id (int): ID of the Schieber game
            runde (int): Round number
            spiel (int): Game number
            spieler_id (int): ID of the player
            first (str): First player
            wwys (str): Wwys (special scoring) in JSON format
            
        Returns:
            int: ID of the created record or None if failed
        """
        query = """
        INSERT INTO wwys (schieber_id, runde, spiel, spieler_id, first, wwys)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor = self.execute_query(
            query,
            (schieber_id, runde, spiel, spieler_id, first, wwys),
            commit=True
        )
        
        if cursor:
            return cursor.lastrowid
        return None
    
    # Query operations
    def get_player_by_id(self, player_id):
        """
        Get a player by ID.
        
        Args:
            player_id (int): ID of the player
            
        Returns:
            tuple: Player data or None if not found
        """
        query = "SELECT id, name FROM spieler WHERE id = ?"
        return self.fetch_one(query, (player_id,))
        
    def get_spieler_id_by_name(self, name):
        """
        Get player ID by name.
        
        Args:
            name (str): Name of the player
            
        Returns:
            int: Player ID or None if not found
        """
        query = "SELECT id FROM spieler WHERE name = ?"
        result = self.fetch_one(query, (name,))
        
        if result:
            return result[0]
        return None
    
    def get_game_stats(self, schieber_id):
        """
        Get game statistics.
        
        Args:
            schieber_id (int): ID of the Schieber game
            
        Returns:
            dict: Game statistics
        """
        game_query = "SELECT begin_date, end_date, end_sum FROM schieber WHERE id = ?"
        game_data = self.fetch_one(game_query, (schieber_id,))
        
        if not game_data:
            return None
            
        # Get total points
        points_query = """
        SELECT MAX(pointOW) as ow_points, MAX(pointSN) as sn_points 
        FROM play 
        WHERE schieber_id = ?
        """
        points_data = self.fetch_one(points_query, (schieber_id,))
        
        # Get round count
        rounds_query = "SELECT COUNT(DISTINCT runde) FROM game WHERE schieber_id = ?"
        rounds_data = self.fetch_one(rounds_query, (schieber_id,))
        
        return {
            "begin_date": game_data[0],
            "end_date": game_data[1],
            "end_sum": game_data[2],
            "ow_points": points_data[0] if points_data else 0,
            "sn_points": points_data[1] if points_data else 0,
            "rounds": rounds_data[0] if rounds_data else 0
        }
        
    def get_last_game_id(self):
        """
        Get the ID of the last created game.
        
        Returns:
            int: ID of the last game or None if no games
        """
        query = "SELECT MAX(id) FROM schieber"
        result = self.fetch_one(query)
        
        if result and result[0]:
            return result[0]
        return None


# Example usage
if __name__ == "__main__":
    db = DatabaseManager("schieber.db")
    db.connect()
    db.create_schema()
    db.close()