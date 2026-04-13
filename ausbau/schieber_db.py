import sqlite3 as db

conn = db.connect('schieber.db')
cursor = conn.cursor()
cursor.execute("create table schieber(id int, start date, end date)")
cursor.execute("create table spieler(id int, name text)")
cursor.execute('insert into spieler values(1, "compo")')
cursor.execute('insert into spieler values(2, "compn")')
cursor.execute('insert into spieler values(3, "compe")')
cursor.execute('insert into spieler values(4, "comps")')
cursor.execute("create table game(schieber int, runde int, spiel int, zug int, spieler_id int, first text, operator text, Eicheln text, Rosen text, Schellen text, Schilten text)")
cursor.execute("create table play(schieber int, runde int, spiel int, zug int, spieler_id int, first text, operator text, human Boolean, realname text, pointOW int, pointSN int, Eicheln text, Rosen text, Schellen text, Schilten text)")
cursor.execute("create table wys(schieber int, runde int, spiel int, spieler_id int, Eicheln int, Rosen int, Schellen int, Schilten int)")
cursor.execute("create table wwys(schieber int, runde int, spiel int, spieler_id int, Eicheln int, Rosen int, Schellen int, Schilten int)")
cursor.execute("create table stich(schieber int, runde int, spiel int, zug int, spieler_id int, stich text)")
stocks = [
('GOOG', 100, 490.1),
('AAPL', 50, 545.75),
('FB', 150, 7.45),
('HPQ', 75, 33.2),]

c = conn.cursor()
#c.execute(if not exists portfolio: 'create table portfolio (symbol text, shares integer, price real)')

c.executemany('insert into portfolio values (?,?,?)', stocks)
conn.commit()

for row in conn.execute('select * from portfolio'):
    print(row)


min_price = 100
for row in conn.execute('select * from portfolio where price >= ?', (min_price,)):
    print(row)
