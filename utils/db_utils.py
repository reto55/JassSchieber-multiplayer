"""
Database utilities for the Schieber card game.
This module provides functions for database access and operations.
"""
import sqlite3 as db
from sqlite3 import Error

def create_connection(db_file):
    """ Create a database connection to the SQLite database
        specified by db_file
        
    Args:
        db_file (str): Path to the database file
        
    Returns:
        Connection object or None
    """
    try:
        conn = db.connect(db_file)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
    return None

def create_game(conn, game):
    """
    Create a new game record in the game table
    
    Args:
        conn: Database connection
        game: Tuple of (schieber_id, runde, spiel, zug, spieler_id, first, operator, Karte)
        
    Returns:
        The ID of the newly created record
    """
    sql = '''INSERT INTO game(schieber_id,runde,spiel,zug,spieler_id,first,operator,Karte)
             VALUES(?,?,?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, game)
    return cur.lastrowid

def create_play(conn, play):
    """
    Create a new play record in the play table
    
    Args:
        conn: Database connection
        play: Tuple of (schieber_id, runde, spiel, zug, spieler_id, first, operator, 
              realname, pointOW, pointSN, Eicheln, Rosen, Schellen, Schilten)
        
    Returns:
        The ID of the newly created record
    """
    sql = '''INSERT INTO play(schieber_id,runde,spiel,zug,spieler_id,first,operator,realname,
                            pointOW,pointSN,Eicheln,Rosen,Schellen,Schilten)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, play)
    return cur.lastrowid

def create_schieber(conn, schieber):
    """
    Create a new schieber game session
    
    Args:
        conn: Database connection
        schieber: Tuple of (begin_date, end_date, end_sum)
        
    Returns:
        The ID of the newly created record
    """
    sql = '''INSERT INTO schieber(begin_date,end_date,end_sum)
             VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, schieber)
    return cur.lastrowid

def create_spieler(conn, spieler):
    """
    Create a new player record
    
    Args:
        conn: Database connection
        spieler: Tuple of (id, name)
        
    Returns:
        The ID of the newly created record
    """
    sql = '''INSERT INTO spieler(id,name)
             VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(sql, spieler)
    return cur.lastrowid

def create_stich(conn, stich):
    """
    Create a new stich (trick) record
    
    Args:
        conn: Database connection
        stich: Tuple of (schieber_id, runde, spiel, zug, spieler_id, stich)
        
    Returns:
        The ID of the newly created record
    """
    sql = '''INSERT INTO stich(schieber_id,runde,spiel,zug,spieler_id,stich)
             VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, stich)
    return cur.lastrowid

def create_wwys(conn, wwys):
    """
    Create a new wwys (special scoring) record
    
    Args:
        conn: Database connection
        wwys: Tuple of (schieber_id, runde, spiel, spieler_id, first, wwys)
        
    Returns:
        The ID of the newly created record
    """
    sql = '''INSERT INTO wwys(schieber_id,runde,spiel,spieler_id,first,wwys)
             VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, wwys)
    return cur.lastrowid

def create_wys(conn, wys):
    """
    Create a new wys (scoring) record
    
    Args:
        conn: Database connection
        wys: Tuple of (schieber_id, runde, spiel, spieler_id, first, wys)
        
    Returns:
        The ID of the newly created record
    """
    sql = '''INSERT INTO wys(schieber_id,runde,spiel,spieler_id,first,wys)
             VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, wys)
    return cur.lastrowid

def update_schieber(conn, ende):
    """
    Update the end_date of a schieber game session
    
    Args:
        conn: Database connection
        ende: Tuple of (end_date, id)
    
    Returns:
        The ID of the updated record
    """
    sql = '''UPDATE schieber
             SET end_date = ?
             WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, ende)
    return cur.lastrowid

def get_spieler_by_id(conn, spieler_id):
    """
    Get a player record by ID
    
    Args:
        conn: Database connection
        spieler_id: The ID of the player
        
    Returns:
        The player record or None
    """
    sql = '''SELECT id, name FROM spieler WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (spieler_id,))
    return cur.fetchone()

def get_game_stats(conn, schieber_id):
    """
    Get game statistics for a schieber game session
    
    Args:
        conn: Database connection
        schieber_id: The ID of the schieber game
        
    Returns:
        Dictionary with game statistics
    """
    # Get game data
    sql = '''SELECT begin_date, end_date, end_sum FROM schieber WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (schieber_id,))
    game_data = cur.fetchone()
    
    if not game_data:
        return None
        
    # Get maximum points
    sql = '''SELECT MAX(pointOW) as ow_points, MAX(pointSN) as sn_points 
             FROM play 
             WHERE schieber_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (schieber_id,))
    points_data = cur.fetchone()
    
    # Get round count
    sql = '''SELECT COUNT(DISTINCT runde) FROM game WHERE schieber_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (schieber_id,))
    rounds_data = cur.fetchone()
    
    return {
        "begin_date": game_data[0],
        "end_date": game_data[1],
        "end_sum": game_data[2],
        "ow_points": points_data[0] if points_data else 0,
        "sn_points": points_data[1] if points_data else 0,
        "rounds": rounds_data[0] if rounds_data else 0
    }