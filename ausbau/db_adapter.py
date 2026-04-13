"""
Database Adapter for Schieber Card Game.
Provides compatibility with the old database interface 
while using the new DatabaseManager implementation.
"""
from database_manager import DatabaseManager

# Global database manager instance
_db_manager = None


def get_db_manager(db_path='schieber.db'):
    """
    Get the global database manager instance.
    
    Args:
        db_path (str): Path to the SQLite database file
        
    Returns:
        DatabaseManager: The database manager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
        _db_manager.connect()
    return _db_manager


def create_connection(db_file):
    """
    Compatibility function for old code.
    Creates a connection to the database.
    
    Args:
        db_file (str): Database file path
        
    Returns:
        Connection object (for compatibility)
    """
    db = get_db_manager(db_file)
    return db


def create_game(conn, game):
    """
    Compatibility function for old code.
    Create a new game record.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        game: Tuple with game data
        
    Returns:
        int: ID of the created record
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    # Check if game data has the correct format
    if len(game) != 8:
        print("Warning: Invalid game data format")
        return None
        
    schieber_id, runde, spiel, zug, spieler_id, first, operator, karte = game
    return db.create_game_record(
        schieber_id, runde, spiel, zug, spieler_id, first, operator, karte
    )


def create_play(conn, play):
    """
    Compatibility function for old code.
    Create a new play record.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        play: Tuple with play data
        
    Returns:
        int: ID of the created record
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    # Check if play data has the correct format
    if len(play) != 14:
        print(f"Warning: Invalid play data format. Got {len(play)} fields, expected 14")
        return None
        
    (schieber_id, runde, spiel, zug, spieler_id, first, operator, 
     realname, pointOW, pointSN, eicheln, rosen, schellen, schilten) = play
     
    return db.create_play_record(
        schieber_id, runde, spiel, zug, spieler_id, first, operator,
        realname, pointOW, pointSN, eicheln, rosen, schellen, schilten
    )


def create_schieber(conn, schieber):
    """
    Compatibility function for old code.
    Create a new schieber game session.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        schieber: Tuple with schieber data (begin_date, end_date, end_sum)
        
    Returns:
        int: ID of the created game
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    # The new implementation uses automatic begin_date,
    # but we'll keep compatibility for now
    begin_date, end_date, end_sum = schieber
    
    query = "INSERT INTO schieber (begin_date, end_date, end_sum) VALUES (?, ?, ?)"
    cursor = db.execute_query(query, (begin_date, end_date, end_sum), commit=True)
    
    if cursor:
        return cursor.lastrowid
    return None


def create_spieler(conn, spieler):
    """
    Compatibility function for old code.
    Create a new spieler record.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        spieler: Tuple with spieler data (id, name)
        
    Returns:
        int: ID of the created record
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    # Check if spieler data has the correct format
    if len(spieler) != 2:
        print("Warning: Invalid spieler data format")
        return None
        
    player_id, name = spieler
    
    query = "INSERT INTO spieler (id, name) VALUES (?, ?)"
    cursor = db.execute_query(query, (player_id, name), commit=True)
    
    if cursor:
        return cursor.lastrowid
    return None


def create_stich(conn, stich):
    """
    Compatibility function for old code.
    Create a new stich record.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        stich: Tuple with stich data
        
    Returns:
        int: ID of the created record
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    # Check if stich data has the correct format
    if len(stich) != 6:
        print("Warning: Invalid stich data format")
        return None
        
    schieber_id, runde, spiel, zug, spieler_id, stich_data = stich
    return db.create_stich_record(
        schieber_id, runde, spiel, zug, spieler_id, stich_data
    )


def create_wwys(conn, wwys):
    """
    Compatibility function for old code.
    Create a new wwys record.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        wwys: Tuple with wwys data
        
    Returns:
        int: ID of the created record
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    # Check if wwys data has the correct format
    if len(wwys) != 6:
        print("Warning: Invalid wwys data format")
        return None
        
    schieber_id, runde, spiel, spieler_id, first, wwys_data = wwys
    return db.create_wwys_record(
        schieber_id, runde, spiel, spieler_id, first, wwys_data
    )


def create_wys(conn, wys):
    """
    Compatibility function for old code.
    Create a new wys record.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        wys: Tuple with wys data
        
    Returns:
        int: ID of the created record
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    # Check if wys data has the correct format
    if len(wys) != 6:
        print("Warning: Invalid wys data format")
        return None
        
    schieber_id, runde, spiel, spieler_id, first, wys_data = wys
    return db.create_wys_record(
        schieber_id, runde, spiel, spieler_id, first, wys_data
    )


def update_schieber(conn, ende):
    """
    Compatibility function for old code.
    Update a schieber game session.
    
    Args:
        conn: Connection object (can be DatabaseManager)
        ende: Tuple with (end_date, id)
        
    Returns:
        bool: True if successful
    """
    db = conn if isinstance(conn, DatabaseManager) else get_db_manager()
    
    end_date, schieber_id = ende
    
    query = "UPDATE schieber SET end_date = ? WHERE id = ?"
    cursor = db.execute_query(query, (end_date, schieber_id), commit=True)
    
    if cursor and cursor.rowcount > 0:
        return True
    return False


# Sample usage
if __name__ == "__main__":
    # Example of how to use the adapter
    conn = create_connection("schieber.db")
    
    # Old style code still works
    create_spieler(conn, (5, "TestPlayer"))
    
    # New style code is also available
    db = get_db_manager()
    player = db.get_player_by_id(5)
    print(f"Created player: {player}")