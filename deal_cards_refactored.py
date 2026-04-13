# -*- coding: UTF-8 -*-
"""
Refactored deal_cards.py file for the Schieber card game.
This module handles the game flow and card dealing logic.
"""
from imports_new import *
from time import sleep
from Cards_refactored import *

# Import the database manager if available, otherwise use adapter
try:
    from ausbau.database_manager import DatabaseManager
    USE_NEW_DB = True
except ImportError:
    from imports import create_connection, create_play, create_game, create_stich, create_wys, create_wwys
    USE_NEW_DB = False


class GameController:
    """
    Controls the flow of the Schieber card game.
    Handles dealing cards, managing turns, and scoring.
    """
    
    def __init__(self, db_connection, human=None, end_game=2500, time_delay=0, starting_round=0):
        """
        Initialize the game controller.
        
        Args:
            db_connection: Database connection or manager
            human (dict): Dictionary of human players
            end_game (int): Target score to end the game
            time_delay (int): Delay between game actions
            starting_round (int): Starting round number
        """
        self.conn = db_connection
        self.human = human or {}
        self.end_game = end_game
        self.time_delay = time_delay
        self.runde = starting_round
        self.pointSN = 0  # North-South points
        self.pointOW = 0  # East-West points
        
        # Get database connection if using new manager
        if USE_NEW_DB and isinstance(self.conn, DatabaseManager):
            self.db = self.conn
        else:
            self.db = None
            
    def _record_play(self, dealer, runde, game_num, turn_num):
        """
        Record play data to the database.
        
        Args:
            dealer: The dealer object
            runde (int): Round number
            game_num (int): Game number
            turn_num (int): Turn number
        """
        if USE_NEW_DB and self.db:
            # Use new database manager
            self.db.create_play_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=1,
                first=dealer.first,
                operator=dealer.operator,
                realname=self.human.get('compo', ''),
                pointOW=self.pointOW,
                pointSN=self.pointSN,
                eicheln=Card.to_json(dealer.compo['Eicheln']),
                rosen=Card.to_json(dealer.compo['Rosen']),
                schellen=Card.to_json(dealer.compo['Schellen']),
                schilten=Card.to_json(dealer.compo['Schilten'])
            )
            
            # Similar calls for other players...
            self.db.create_play_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=2,
                first=dealer.first,
                operator=dealer.operator,
                realname=self.human.get('compn', ''),
                pointOW=self.pointOW,
                pointSN=self.pointSN,
                eicheln=Card.to_json(dealer.compn['Eicheln']),
                rosen=Card.to_json(dealer.compn['Rosen']),
                schellen=Card.to_json(dealer.compn['Schellen']),
                schilten=Card.to_json(dealer.compn['Schilten'])
            )
            
            self.db.create_play_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=3,
                first=dealer.first,
                operator=dealer.operator,
                realname=self.human.get('compe', ''),
                pointOW=self.pointOW,
                pointSN=self.pointSN,
                eicheln=Card.to_json(dealer.compe['Eicheln']),
                rosen=Card.to_json(dealer.compe['Rosen']),
                schellen=Card.to_json(dealer.compe['Schellen']),
                schilten=Card.to_json(dealer.compe['Schilten'])
            )
            
            self.db.create_play_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=4,
                first=dealer.first,
                operator=dealer.operator,
                realname=self.human.get('comps', ''),
                pointOW=self.pointOW,
                pointSN=self.pointSN,
                eicheln=Card.to_json(dealer.comps['Eicheln']),
                rosen=Card.to_json(dealer.comps['Rosen']),
                schellen=Card.to_json(dealer.comps['Schellen']),
                schilten=Card.to_json(dealer.comps['Schilten'])
            )
        else:
            # Use old database functions
            create_play(self.conn, play=(
                Schieber['schieber_id'], runde, game_num, turn_num, 1, dealer.first, dealer.operator,
                self.human.get('compo', ''), self.pointOW, self.pointSN,
                Card.to_json(dealer.compo['Eicheln']), Card.to_json(dealer.compo['Rosen']),
                Card.to_json(dealer.compo['Schellen']), Card.to_json(dealer.compo['Schilten'])
            ))
            
            create_play(self.conn, play=(
                Schieber['schieber_id'], runde, game_num, turn_num, 2, dealer.first, dealer.operator,
                self.human.get('compn', ''), self.pointOW, self.pointSN,
                Card.to_json(dealer.compn['Eicheln']), Card.to_json(dealer.compn['Rosen']),
                Card.to_json(dealer.compn['Schellen']), Card.to_json(dealer.compn['Schilten'])
            ))
            
            create_play(self.conn, play=(
                Schieber['schieber_id'], runde, game_num, turn_num, 3, dealer.first, dealer.operator,
                self.human.get('compe', ''), self.pointOW, self.pointSN,
                Card.to_json(dealer.compe['Eicheln']), Card.to_json(dealer.compe['Rosen']),
                Card.to_json(dealer.compe['Schellen']), Card.to_json(dealer.compe['Schilten'])
            ))
            
            create_play(self.conn, play=(
                Schieber['schieber_id'], runde, game_num, turn_num, 4, dealer.first, dealer.operator,
                self.human.get('comps', ''), self.pointOW, self.pointSN,
                Card.to_json(dealer.comps['Eicheln']), Card.to_json(dealer.comps['Rosen']),
                Card.to_json(dealer.comps['Schellen']), Card.to_json(dealer.comps['Schilten'])
            ))
            
    def _record_game(self, dealer, runde, game_num, turn_num):
        """
        Record game data to the database.
        
        Args:
            dealer: The dealer object
            runde (int): Round number
            game_num (int): Game number
            turn_num (int): Turn number
        """
        if USE_NEW_DB and self.db:
            # Use new database manager
            self.db.create_game_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=spieler_id[dealer.first],
                first=dealer.first,
                operator=dealer.operator,
                karte=Card.to_jsons(dealer.game[dealer.first])
            )
            
            # Similar calls for other players...
            self.db.create_game_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=spieler_id[dealer.folger[dealer.first]],
                first=dealer.first,
                operator=dealer.operator,
                karte=Card.to_jsons(dealer.game[dealer.folger[dealer.first]])
            )
            
            self.db.create_game_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=spieler_id[dealer.partner[dealer.first]],
                first=dealer.first,
                operator=dealer.operator,
                karte=Card.to_jsons(dealer.game[dealer.partner[dealer.first]])
            )
            
            self.db.create_game_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=spieler_id[dealer.folger[dealer.partner[dealer.first]]],
                first=dealer.first,
                operator=dealer.operator,
                karte=Card.to_jsons(dealer.game[dealer.folger[dealer.partner[dealer.first]]])
            )
        else:
            # Use old database functions
            create_game(self.conn, game=(
                Schieber['schieber_id'], runde, game_num, turn_num,
                spieler_id[dealer.first], dealer.first, dealer.operator,
                Card.to_jsons(dealer.game[dealer.first])
            ))
            
            create_game(self.conn, game=(
                Schieber['schieber_id'], runde, game_num, turn_num,
                spieler_id[dealer.folger[dealer.first]], dealer.first, dealer.operator,
                Card.to_jsons(dealer.game[dealer.folger[dealer.first]])
            ))
            
            create_game(self.conn, game=(
                Schieber['schieber_id'], runde, game_num, turn_num,
                spieler_id[dealer.partner[dealer.first]], dealer.first, dealer.operator,
                Card.to_jsons(dealer.game[dealer.partner[dealer.first]])
            ))
            
            create_game(self.conn, game=(
                Schieber['schieber_id'], runde, game_num, turn_num,
                spieler_id[dealer.folger[dealer.partner[dealer.first]]], dealer.first, dealer.operator,
                Card.to_jsons(dealer.game[dealer.folger[dealer.partner[dealer.first]]])
            ))
            
    def _record_stich(self, dealer, runde, game_num, turn_num):
        """
        Record stich (trick) data to the database.
        
        Args:
            dealer: The dealer object
            runde (int): Round number
            game_num (int): Game number
            turn_num (int): Turn number
        """
        if USE_NEW_DB and self.db:
            # Use new database manager
            self.db.create_stich_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                zug=turn_num,
                spieler_id=spieler_id[dealer.first],
                stich=Card.to_jsons(dealer.stich[dealer.first])
            )
        else:
            # Use old database functions
            create_stich(self.conn, stich=(
                Schieber['schieber_id'], runde, game_num, turn_num,
                spieler_id[dealer.first], Card.to_jsons(dealer.stich[dealer.first])
            ))
            
    def _record_wys(self, runde, game_num, player_key, first, wys_value):
        """
        Record wys (scoring) data to the database.
        
        Args:
            runde (int): Round number
            game_num (int): Game number
            player_key (str): Player key
            first (str): First player
            wys_value: Wys value
        """
        if USE_NEW_DB and self.db:
            # Use new database manager
            self.db.create_wys_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                spieler_id=spieler_id[player_key],
                first=first,
                wys=wys_value
            )
        else:
            # Use old database functions
            create_wys(self.conn, wys=(
                Schieber['schieber_id'], runde, game_num,
                spieler_id[player_key], first, wys_value
            ))
            
    def _record_wwys(self, runde, game_num, satz, first):
        """
        Record wwys (special scoring) data to the database.
        
        Args:
            runde (int): Round number
            game_num (int): Game number
            satz (str): Satz text
            first (str): First player
        """
        if USE_NEW_DB and self.db:
            # Use new database manager
            self.db.create_wwys_record(
                schieber_id=Schieber['schieber_id'],
                runde=runde,
                spiel=game_num,
                spieler_id=spieler_id[satz[:5]],
                first=first,
                wwys=satz
            )
        else:
            # Use old database functions
            create_wwys(self.conn, wwys=(
                Schieber['schieber_id'], runde, game_num,
                spieler_id[satz[:5]], first, satz
            ))
            
    def display_player_cards(self, dealer):
        """
        Display cards for all players.
        
        Args:
            dealer: The dealer object
        """
        player_positions = {
            'compe': 'West',
            'compo': 'Ost',
            'compn': 'Nord',
            'comps': 'Sud'
        }
        
        for position, player_key in {'compe': 'compe', 'compo': 'compo', 'compn': 'compn', 'comps': 'comps'}.items():
            player_name = self.human.get(position, '') or player_positions[position]
            print(player_name)
            
            for suit in dealer.__dict__[player_key].keys():
                print(suit, dealer.__dict__[player_key][suit], '\n')
                
    def handle_human_first_player(self, dealer, game_num, turn_num):
        """
        Handle case when the first player is human.
        
        Args:
            dealer: The dealer object
            game_num (int): Game number
            turn_num (int): Turn number
        """
        # Display cards
        self.display_player_cards(dealer)
        
        # Record play
        self._record_play(dealer, self.runde, game_num, turn_num)
        
        # Play human first
        play_hum_first(dealer, dealer.__dict__[dealer.first], dealer.first)
        
    def handle_computer_first_player(self, dealer, game_num, turn_num):
        """
        Handle case when the first player is a computer.
        
        Args:
            dealer: The dealer object
            game_num (int): Game number
            turn_num (int): Turn number
        """
        # Display cards
        self.display_player_cards(dealer)
        
        if dealer.operator != 'Schieben':
            # Normal play
            print("Trumpf :", dealer.operator)
            
            # Record play
            self._record_play(dealer, self.runde, game_num, turn_num)
            
            # Play first card
            play_card_first_first(dealer, dealer.first, dealer.operator)
            display(dealer.game)
            sleep(self.time_delay)
        else:
            # Handle "Schieben" case
            if self.human.get(dealer.partner[dealer.first]):
                # Human partner decides trump
                schieb_hum(dealer, dealer.partner[dealer.first])
                dealer.starter = dealer.partner[dealer.first]
                
                # Record play
                self._record_play(dealer, self.runde, game_num, turn_num)
                
                # Play first card
                play_card_first_first(dealer, dealer.first, dealer.operator)
                display(dealer.game)
                sleep(self.time_delay)
            else:
                # Computer partner decides trump
                print(f'{dealer.first} Ost schiebt.')
                dealer.operator = trumpfs(dealer.__dict__[dealer.partner[dealer.first]])
                print(f"West macht {dealer.operator} Trumpf: ")
                dealer.starter = dealer.partner[dealer.first]
                
                # Record play
                self._record_play(dealer, self.runde, game_num, turn_num)
                
                # Play first card
                play_card_first_first(dealer, dealer.first, dealer.operator)
                display(dealer.game)
                sleep(self.time_delay)
                
    def handle_wiis(self, dealer, game_num):
        """
        Handle wiis (scoring) for the current game.
        
        Args:
            dealer: The dealer object
            game_num (int): Game number
        """
        # Show wiis
        show_wiis_first(dealer.first, dealer.wis, dealer.wis4)
        
        # Record wys
        for key in weis:
            for u in range(len(weis[key])):
                print("Weis ", key, weis[key][u][1])
                self._record_wys(self.runde, game_num, key, dealer.first, weis[key][u][1])
                
        # Record special wys (100 points)
        for key in weis4:
            if len(weis4[key]):
                print("100 von ", key)
                self._record_wys(self.runde, game_num, key, dealer.first, 100)
        
        # Calculate wiis result
        satz, self.pointSN, self.pointOW = wiis_result(
            dealer.operator, dealer.first, dealer.wis, dealer.wis4, 
            dealer, self.pointSN, self.pointOW
        )
        print(satz)
        
        # Record wwys if applicable
        if satz != "Kein Wiis im Spiel!":
            self._record_wwys(self.runde, game_num, satz, dealer.first)
            
    def play_turn(self, dealer, game_num, turn_num):
        """
        Play a single turn in the game.
        
        Args:
            dealer: The dealer object
            game_num (int): Game number
            turn_num (int): Turn number
        """
        # Skip if game is over
        if self.pointSN >= self.end_game or self.pointOW >= self.end_game:
            return False
            
        # Handle first player based on whether they're human or computer
        if self.human.get(dealer.first):
            self.handle_human_first_player(dealer, game_num, turn_num)
        else:
            self.handle_computer_first_player(dealer, game_num, turn_num)
            
        # Process wiis
        self.handle_wiis(dealer, game_num)
            
        # Record game state
        self._record_game(dealer, self.runde, game_num, turn_num)
            
        # Play next cards and make trick
        play_card_next_first(
            dealer, dealer.operator, dealer.first, 
            self.human, farbs=dealer.game[dealer.first][0].suit
        )
        
        # Make trick and update scores
        dealer.first, self.pointSN, self.pointOW = mach_stich(
            dealer, dealer.first, dealer.operator, dealer.game, 
            dealer.stich, dealer.farben, self.pointSN, self.pointOW
        )
        
        # Record stich
        self._record_stich(dealer, self.runde, game_num, turn_num)
        
        # Display points
        print(self.pointSN, self.pointOW)
        
        return True
            
    def play_game(self):
        """
        Play the entire Schieber card game.
        """
        # Increment round counter
        self.runde += 1
        
        # Use a context manager if using new database
        if USE_NEW_DB and isinstance(self.conn, DatabaseManager):
            with self.conn:
                self._play_game_internal()
        else:
            # Use old-style with block
            with self.conn:
                self._play_game_internal()
                
    def _play_game_internal(self):
        """
        Internal method to play the game, used by play_game.
        """
        # Loop through games (1-4)
        for game_num in range(1, 5):
            # Create dealer for this game
            dealer = Play(game_num)
            
            # Loop through turns (1-9)
            for turn_num in range(1, 10):
                if not self.play_turn(dealer, game_num, turn_num):
                    # Game is over due to points
                    return


def deal_card(conn, human=None, end_game=2500, pointSN=0, pointOW=0, t=0, runde=0):
    """
    Legacy function to maintain backward compatibility.
    This function deals out cards and sets up round.
    
    Args:
        conn: Database connection
        human (dict): Dictionary of human players
        end_game (int): Target score to end the game
        pointSN (int): Starting points for North-South
        pointOW (int): Starting points for East-West
        t (int): Time delay between actions
        runde (int): Starting round number
    """
    # Create game controller
    controller = GameController(
        conn, human=human or {}, end_game=end_game,
        time_delay=t, starting_round=runde
    )
    
    # Set initial points
    controller.pointSN = pointSN
    controller.pointOW = pointOW
    
    # Play the game
    controller.play_game()
    
    # Return final points (for backward compatibility)
    return controller.pointSN, controller.pointOW


# Testing code
if __name__ == "__main__":
    from imports import create_connection
    
    # Create a connection
    conn = create_connection("schieber.db")
    
    # Initialize test data
    Schieber['schieber_id'] = 1
    Schieber['date'] = datetime.now()
    
    # Play a game
    pointSN, pointOW = deal_card(conn, human={}, end_game=2500, t=1)
    
    print(f"Final score: North-South {pointSN}, East-West {pointOW}")