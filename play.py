# -*- coding: UTF-8 -*-
"""CLI entry point for the Schieber card game.

Launches an interactive session: prompts for speed, target score, number of
human players, and their names; then drives the game via the legacy
``deal_card`` controller. For the WebSocket/HTTP frontend, use
``ausbau/server.py`` (``uvicorn ausbau.server:app``) instead.
"""
from datetime import datetime
from time import sleep

from deal_cards_refactored import deal_card, Schieber
from utils.db_utils import create_connection, create_schieber


SEAT_KEYS = ['comps', 'compo', 'compn', 'compe']


def names_to_seat_map(player_names):
    """Zip seat keys with the supplied name strings into a ``{seat: name}`` dict.

    ``player_names`` is a list of exactly 4 strings; empty strings mark AI
    seats. The returned dict is consumed by :func:`deal_card` as its
    ``human`` argument.
    """
    return {seat: name for seat, name in zip(SEAT_KEYS, player_names)}


def intro():
    """Print a minimal welcome banner before prompting the user."""
    print("=" * 60)
    print("  Schieber — Swiss Jass card game")
    print("=" * 60)


def main():
    Schieber['date'] = datetime.now()
    intro()

    time_delay = int(input("Gib Geschwindigkeit Spiel ein 3 ist gute wahl:"))
    sleep(time_delay)
    end_game = int(input("Gib Punktzahl zu Spielende an:"))
    player_count = int(input("Gib Anzahl Spieler an: "))

    player_names = []
    for i in range(1, player_count + 1):
        player_names.append(str(input("Gib Namen vom " + str(i) + ". Spieler ein: ")))
    for _ in range(4 - player_count):
        player_names.append('')

    database = "schieber.db"
    conn = create_connection(database)
    Schieber['schieber_id'] = create_schieber(
        conn, schieber=(Schieber['date'], Schieber['date'], end_game)
    )
    deal_card(
        conn=conn,
        end_game=end_game,
        human=names_to_seat_map(player_names),
        t=time_delay,
        runde=0,
    )


if __name__ == "__main__":
    main()
