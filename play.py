# -*- coding: UTF-8 -*-
from deal_cards_refactored import deal_card
from imports_new import *

def namen(listn):
    human = dict()
    listsp = ['comps', 'compo', 'compn', 'compe']
    human = {name[0]:name[1] for name in list(zip(listsp,listn))}
    return human

def main():
    Schieber['date']=datetime.now()
    intro()
    sleep(t)
    t = int(input("Gib Geschwindigkeit Spiel ein 3 ist gute wahl:"))
    end_game = int(input("Gib Punktzahl zu Spielende an:"))
    anzsp = int(input("Gib Anzahl Spieler an: "))
    listn=[]
    for i in range(1,anzsp+1):
        listn.append(str(input("Gib Namen vom " + str(i) + ". Spieler ein: ")))
    for i in range(4-anzsp):
        listn.append('')
    #print(end_game)
    #print(namen(listn))
    database = "schieber.db"
    # create a database connection
    conn = create_connection(database)
    Schieber['schieber_id']= create_schieber(conn, schieber=(Schieber['date'],Schieber['date'],end_game))
    deal_card(conn=conn, end_game=end_game, human=namen(listn), t=t, runde=runde)

if __name__ == "__main__":
    main()