import sqlite3 as db
from sqlite3 import Error	
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = db.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None
	
def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def alter_table(conn, alter_table_sql):
    """ alter a table from the alter_table_sql statement
    :param conn: Connection object
    :param alter_table_sql: a ALTER TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(alter_table_sql)
    except Error as e:
        print(e)

def main():
    database = "schieber.db"

    sql_create_schieber_table = """ CREATE TABLE IF NOT EXISTS schieber (
                                        id integer PRIMARY KEY,
                                        begin_date text,
                                        end_date text,
                                        end_sum integer
                                    ); """
 
    sql_create_spieler_table = """ CREATE TABLE IF NOT EXISTS spieler (
                                        id integer PRIMARY KEY,
                                        name text
                                    ); """

    sql_create_play_table = """CREATE TABLE IF NOT EXISTS play (
                                    id integer PRIMARY KEY,
                                    schieber_id integer NOT NULL,
                                    runde integer NOT NULL,
                                    spiel integer NOT NULL,
                                    zug integer NOT NULL,
                                    spieler_id integer NOT NULL,
                                    first text NOT NULL,
                                    operator text NOT NULL,
                                    realname text Default Null,
                                    pointOW integer,
                                    pointSN integer,
                                    Eicheln text,
                                    Rosen text,
                                    Schellen text,
                                    Schilten text,
                                    FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                                    FOREIGN KEY (spieler_id) REFERENCES spieler (id)
                                );"""
    
    sql_create_game_table = """CREATE TABLE IF NOT EXISTS game (
                                    id integer PRIMARY KEY,
                                    schieber_id integer NOT NULL,
                                    runde integer NOT NULL,
                                    spiel integer NOT NULL,
                                    zug integer NOT NULL,
                                    spieler_id integer NOT NULL,
                                    first text NOT NULL,
                                    operator text NOT NULL,
                                    Karte text NOT NULL,
                                    FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                                    FOREIGN KEY (spieler_id) REFERENCES spieler (id)
                                );"""
 
    sql_create_wys_table = """CREATE TABLE IF NOT EXISTS wys (
                                    id integer PRIMARY KEY,
                                    schieber_id integer NOT NULL,
                                    runde integer NOT NULL,
                                    spiel integer NOT NULL,
                                    spieler_id integer NOT NULL,
                                    first text NOT NULL,
                                    wys text,
                                    FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                                    FOREIGN KEY (spieler_id) REFERENCES spieler (id)
                                );"""

    sql_create_wwys_table = """CREATE TABLE IF NOT EXISTS wwys (
                                    id integer PRIMARY KEY,
                                    schieber_id integer NOT NULL,
                                    runde integer NOT NULL,
                                    spiel integer NOT NULL,
                                    spieler_id integer NOT NULL,
                                    first text NOT NULL,
                                    wwys text,
                                    FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                                    FOREIGN KEY (spieler_id) REFERENCES spieler (id)
                                );"""

    sql_create_stich_table = """CREATE TABLE IF NOT EXISTS stich (
                                    id integer PRIMARY KEY,
                                    schieber_id integer NOT NULL,
                                    runde integer NOT NULL,
                                    spiel integer NOT NULL,
                                    zug integer NOT NULL,
                                    spieler_id integer NOT NULL,
                                    stich text, 
                                    FOREIGN KEY (schieber_id) REFERENCES schieber (id),
                                    FOREIGN KEY (spieler_id) REFERENCES spieler (id)
                                );"""



    #sql_alter_schieber_table = """ALTER TABLE schieber ADD COLUMN end_sum integer;"""
    # create a database connection
    conn = create_connection(database)
    
    if conn is not None:
        # create schieber table
        create_table(conn, sql_create_schieber_table)
        # create spieler table
        create_table(conn, sql_create_spieler_table)
        # create play table
        create_table(conn, sql_create_play_table)
        # create game table
        create_table(conn, sql_create_game_table)
        # create wys table
        create_table(conn, sql_create_wys_table)
        # create wwys table
        create_table(conn, sql_create_wwys_table)
        # create stich table
        create_table(conn, sql_create_stich_table)
    else:
        print("Error! cannot create the database connection.")

    #if conn is not None:
     #   alter_table(conn, sql_alter_schieber_table)
    #else:
        #print("Error! cannot create the database connection.")
if __name__ == '__main__':
    main()