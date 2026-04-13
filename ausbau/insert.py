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

def create_game(conn, game):
    """
    Create a new game into the game table
    :param conn:
    :param game:
    :return: gamer id
    """
    sql = ''' INSERT INTO game(schieber_id,runde,spiel,zug,spieler_id,first,operator,Karte)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, game)
    return cur.lastrowid

def create_play(conn, play):
    """
    Create a new play into the play table
    :param conn:
    :param play:
    :return: play id
    """
    sql = ''' INSERT INTO play(schieber_id,runde,spiel,zug,spieler_id,first,operator,realname,pointOW,pointSN,Eicheln,Rosen,Schellen,Schilten)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, play)
    return cur.lastrowid

def create_schieber(conn, schieber):
    """
    Create a new schieber into the schieber table
    :param conn:
    :param schieber:
    :return: schieber id
    """
    sql = ''' INSERT INTO schieber(begin_date,end_date,end_sum)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, schieber)
    return cur.lastrowid

def create_spieler(conn, spieler):
    """
    Create a new spieler into the spieler table
    :param conn:
    :param spieler:
    :return: spieler id
    """
    sql = ''' INSERT INTO spieler(id,name)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, spieler)
    return cur.lastrowid

def create_stich(conn, stich):
    """
    Create a new stich into the stich table
    :param conn:
    :param stich:
    :return: stich id
    """
    sql = ''' INSERT INTO stich(schieber_id,runde,spiel,zug,spieler_id,stich)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, stich)
    return cur.lastrowid

def create_wwys(conn, wwys):
    """
    Create a new wwys into the wwys table
    :param conn:
    :param wwys:
    :return: wwys id
    """
    sql = ''' INSERT INTO wwys(schieber_id,runde,spiel,spieler_id,first,wwys)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, wwys)
    return cur.lastrowid

def create_wys(conn, wys):
    """
    Create a new wys into the wys table
    :param conn:
    :param wys:
    :return: wys id
    """
    sql = ''' INSERT INTO wys(schieber_id,runde,spiel,spieler_id,first,wys)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, wys)
    return cur.lastrowid

def update_schieber(conn,end_date):
    """
    Updates end_date in the schieber table
    :param conn:
    :param end_date:
    """
    sql = ''' UPDATE schieber
              SET end_date = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, end_date)
    return cur.lastrowid

def main():
    database = "schieber.db"
 
    # create a database connection
    conn = create_connection(database)
    with conn:
        # create a new spieler
        #spieler = (4,'comps')
        #print(create_spieler(conn, spieler))
        #create a new schieber
        #schieber =  ('2015-01-04', '2015-01-06',2500)
        #schieber_id = create_schieber(conn,schieber)
        #print(schieber_id)
        update_schieber(conn,('2015-01-04',1))
"""   # tasks
        task_1 = ('Analyze the requirements of the app', 1, 1, project_id, '2015-01-01', '2015-01-02')
        task_2 = ('Confirm with user about the top requirements', 1, 1, project_id, '2015-01-03', '2015-01-05')
 
        # create tasks
        create_task(conn, task_1)
        create_task(conn, task_2)
    cur = conn.cursor()
    cur.execute(sql, task)
    return cur.lastrowid
"""
if __name__ == '__main__':
    main()