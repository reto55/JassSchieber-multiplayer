"""
Database Migration Script for Schieber Card Game.
This script helps migrate data from the old database format to the new one.
"""
import os
import sqlite3
from sqlite3 import Error
from database_manager import DatabaseManager


def migrate_database(old_db_path, new_db_path=None):
    """
    Migrate data from the old database to a new one with the improved schema.
    
    Args:
        old_db_path (str): Path to the old database
        new_db_path (str): Path to the new database (will be created)
        
    Returns:
        bool: True if migration was successful
    """
    if not os.path.exists(old_db_path):
        print(f"Error: Old database {old_db_path} does not exist")
        return False
        
    if new_db_path is None:
        # Create a new database with "_new" suffix
        file_name, file_ext = os.path.splitext(old_db_path)
        new_db_path = f"{file_name}_new{file_ext}"
    
    # Check if new database already exists
    if os.path.exists(new_db_path):
        user_input = input(f"Database {new_db_path} already exists. Overwrite? (y/n): ")
        if user_input.lower() != 'y':
            print("Migration aborted.")
            return False
        os.remove(new_db_path)
    
    try:
        # Connect to the old database
        old_conn = sqlite3.connect(old_db_path)
        old_cursor = old_conn.cursor()
        
        # Create the new database with the correct schema
        db_manager = DatabaseManager(new_db_path)
        db_manager.connect()
        db_manager.create_schema()
        
        # Migrate data from each table
        
        # 1. Migrate schieber data
        print("Migrating schieber table...")
        try:
            rows = old_cursor.execute("SELECT id, begin_date, end_date, end_sum FROM schieber").fetchall()
            for row in rows:
                schieber_id, begin_date, end_date, end_sum = row
                db_manager.execute_query(
                    "INSERT INTO schieber (id, begin_date, end_date, end_sum) VALUES (?, ?, ?, ?)",
                    (schieber_id, begin_date, end_date, end_sum),
                    commit=True
                )
        except Error as e:
            print(f"Error migrating schieber table: {e}")
        
        # 2. Migrate spieler data
        print("Migrating spieler table...")
        try:
            rows = old_cursor.execute("SELECT id, name FROM spieler").fetchall()
            for row in rows:
                player_id, name = row
                # Skip default players as they're already created by create_schema
                if player_id > 4:
                    db_manager.execute_query(
                        "INSERT INTO spieler (id, name) VALUES (?, ?)",
                        (player_id, name),
                        commit=True
                    )
        except Error as e:
            print(f"Error migrating spieler table: {e}")
        
        # 3. Migrate game data
        print("Migrating game table...")
        try:
            rows = old_cursor.execute(
                "SELECT schieber, runde, spiel, zug, spieler_id, first, operator, Karte FROM game"
            ).fetchall()
            if rows:
                for row in rows:
                    schieber_id, runde, spiel, zug, spieler_id, first, operator, karte = row
                    db_manager.create_game_record(
                        schieber_id, runde, spiel, zug, spieler_id, first, operator, karte
                    )
        except Error as e:
            print(f"Error migrating game table: {e}")
        
        # 4. Migrate play data
        print("Migrating play table...")
        try:
            rows = old_cursor.execute(
                """SELECT schieber, runde, spiel, zug, spieler_id, first, operator, 
                   realname, pointOW, pointSN, Eicheln, Rosen, Schellen, Schilten 
                   FROM play"""
            ).fetchall()
            if rows:
                for row in rows:
                    db_manager.create_play_record(*row)
        except Error as e:
            print(f"Error migrating play table: {e}")
        
        # 5. Migrate wys data
        print("Migrating wys table...")
        try:
            rows = old_cursor.execute(
                "SELECT schieber, runde, spiel, spieler_id, first, wys FROM wys"
            ).fetchall()
            if rows:
                for row in rows:
                    db_manager.create_wys_record(*row)
        except Error as e:
            print(f"Error migrating wys table: {e}")
        
        # 6. Migrate wwys data
        print("Migrating wwys table...")
        try:
            rows = old_cursor.execute(
                "SELECT schieber, runde, spiel, spieler_id, first, wwys FROM wwys"
            ).fetchall()
            if rows:
                for row in rows:
                    db_manager.create_wwys_record(*row)
        except Error as e:
            print(f"Error migrating wwys table: {e}")
        
        # 7. Migrate stich data
        print("Migrating stich table...")
        try:
            rows = old_cursor.execute(
                "SELECT schieber, runde, spiel, zug, spieler_id, stich FROM stich"
            ).fetchall()
            if rows:
                for row in rows:
                    db_manager.create_stich_record(*row)
        except Error as e:
            print(f"Error migrating stich table: {e}")
        
        # Close connections
        old_conn.close()
        db_manager.close()
        
        print(f"Migration completed successfully. New database: {new_db_path}")
        return True
    
    except Error as e:
        print(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    # Run the migration
    old_db = input("Enter path to the old database: ")
    new_db = input("Enter path for the new database (leave empty for auto-naming): ")
    
    if not new_db:
        new_db = None
        
    migrate_database(old_db, new_db)