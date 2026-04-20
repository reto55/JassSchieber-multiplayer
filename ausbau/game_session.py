import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from typing import Optional
from Cards_refactored import (
    Play, SUITS, PLAY_MODES, Card,
    determine_trumpf, trumpfs, wiis, wiis_gleiche,
)
from utils.game_utils import check_game_end

SUIT_PREFIX = {'Eicheln': 'E', 'Rosen': 'R', 'Schellen': 'SE', 'Schilten': 'SI'}
RANK_SUFFIX = {9: 'A', 8: 'K', 7: 'O', 6: 'U', 5: 'B', 4: '9', 3: '8', 2: '7', 1: '6'}

POSITION_NAMES = {'comps': 'Süd', 'compn': 'Nord', 'compo': 'Ost', 'compe': 'West'}
SN_PLAYERS = {'comps', 'compn'}
OW_PLAYERS = {'compo', 'compe'}
PLAYERS = ['comps', 'compo', 'compn', 'compe']


def card_to_code(card: Card) -> str:
    """Convert a Card object to its CSS code string, e.g. Ass(Eicheln) → 'EA'."""
    return SUIT_PREFIX[card.suit] + RANK_SUFFIX[card.rank]


def hand_to_codes(hand: dict) -> list:
    """Return list of card codes for all cards in a hand dict."""
    return [card_to_code(c) for suit in SUITS for c in hand[suit]]


def find_card_in_hand(code: str, hand: dict):
    """Find a card in a hand dict by code. Returns (Card, suit) or (None, None)."""
    for suit in SUITS:
        for card in hand[suit]:
            if card_to_code(card) == code:
                return card, suit
    return None, None


def get_valid_cards(hand: dict, lead_suit: Optional[str], operator: str) -> list:
    """Return card codes valid to play. lead_suit=None means player is leading."""
    all_cards = [c for suit in SUITS for c in hand[suit]]

    if lead_suit is None:
        return [card_to_code(c) for c in all_cards]

    follow_cards = hand.get(lead_suit, [])
    if not follow_cards:
        return [card_to_code(c) for c in all_cards]

    valid = list(follow_cards)
    # Trump Under (Bube) can always be played in a trump game
    if operator in SUITS:
        for c in hand.get(operator, []):
            if c.__class__.__name__ == 'Under' and c not in valid:
                valid.append(c)

    return [card_to_code(c) for c in valid]


def determine_trick_winner(trick: dict, first: str, operator: str, folger: dict) -> str:
    """Return the player key who wins the trick."""
    lead_suit = trick[first].suit

    def strength(card: Card):
        if operator in SUITS:
            if card.suit == operator:
                return (2, card.trumpf)
            elif card.suit == lead_suit:
                return (1, card.rank)
            return (0, 0)
        elif operator == 'Oben':
            return (1, card.oben) if card.suit == lead_suit else (0, 0)
        else:  # Unten
            return (1, card.unten) if card.suit == lead_suit else (0, 0)

    winner = first
    best = strength(trick[first])
    player = folger[first]
    for _ in range(3):
        s = strength(trick[player])
        if s > best:
            best = s
            winner = player
        player = folger[player]
    return winner


def trick_points(trick: dict, operator: str) -> int:
    """Sum point values of all cards in the trick for the given mode."""
    total = 0
    for card in trick.values():
        if operator in SUITS:
            total += card.wtrumpf if card.suit == operator else card.wfarbe
        elif operator == 'Oben':
            total += card.woben
        else:
            total += card.wunten
    return total


def ai_select_card(hand: dict, lead_suit: Optional[str], operator: str) -> Card:
    """Simple AI: lead=highest point value, follow=lowest point value."""
    valid_codes = get_valid_cards(hand, lead_suit, operator)
    valid_cards = [find_card_in_hand(code, hand)[0] for code in valid_codes]

    def point_value(card: Card) -> int:
        if operator in SUITS:
            return card.wtrumpf if card.suit == operator else card.wfarbe
        elif operator == 'Oben':
            return card.woben
        return card.wunten

    if lead_suit is None:
        return max(valid_cards, key=point_value)
    return min(valid_cards, key=point_value)


def describe_weis(weis_combos: list, weis_gleiche: list) -> list:
    """Convert raw wiis() / wiis_gleiche() output to human-readable dicts."""
    result = []
    SCORE_MAP = {3: ('Dreier', 20), 4: ('Vierter', 50)}
    for suit_idx, seq_len, _ in weis_combos:
        if seq_len is None or seq_len < 3:
            continue
        name, pts = SCORE_MAP.get(seq_len, (f'{seq_len}er', 100))
        result.append({'name': name, 'suit': SUITS[suit_idx], 'points': pts})
    if weis_gleiche:
        result.append({'name': 'Viererle', 'suit': None, 'points': 100})
    return result


def detect_stock(hand: dict, operator: str) -> bool:
    """True if hand has König + Ober of the trump suit (Stöck, 20pts)."""
    if operator not in SUITS:
        return False
    ranks = {c.__class__.__name__ for c in hand.get(operator, [])}
    return 'Koenig' in ranks and 'Ober' in ranks


class GameSession:
    def __init__(self, end_game: int = 1000):
        self.end_game = end_game
        self.point_sn = 0
        self.point_ow = 0

    def _initial_state(self, play: Play) -> dict:
        return {
            "type": "game_start",
            "hand": hand_to_codes(play.comps),
            "first_player": POSITION_NAMES[play.first],
            "players": [
                {
                    "name": POSITION_NAMES[p],
                    "position": p,
                    "is_partner": p == 'compn',
                    "card_count": 9,
                }
                for p in ['compe', 'compn', 'compo']
            ],
            "scores": {"sn": self.point_sn, "ow": self.point_ow},
            "target": self.end_game,
        }

    async def _trump_phase(self, websocket, play: Play) -> None:
        """Handle trump selection. Asks human if they are the lead or if AI schiebs to them.

        Per the schieber-protocol skill invariant §5 ("No silent failures…
        server responds with `error` and re-sends the most recent prompt"),
        the human may only reply with `choose_trump` (always) or `schieben`
        (only when the most recent `trump_request` offered `can_schieben=True`).
        Any other message `type` is rejected with an `error` payload followed
        by a re-send of the same `trump_request`. The loop continues until a
        valid reply arrives. Messages that happen to carry a `suit` key but
        the wrong `type` are NOT accepted — tightens defect D9.
        """
        if play.first == 'comps':
            # Human leads — choose_trump or schieben both allowed.
            prompt = {"type": "trump_request", "can_schieben": True}
            await websocket.send_json(prompt)
            while True:
                msg = await websocket.receive_json()
                mtype = msg.get('type')
                if mtype == 'schieben':
                    play.operator = trumpfs(play.compn)
                    play.starter = 'compn'
                    chooser = 'Nord'
                    break
                if mtype == 'choose_trump' and 'suit' in msg:
                    play.operator = msg['suit']
                    play.starter = 'comps'
                    chooser = 'Du'
                    break
                await websocket.send_json({
                    "type": "error",
                    "message": (
                        f"Erwartet: 'choose_trump' oder 'schieben', erhalten: {mtype!r}."
                    ),
                })
                await websocket.send_json(prompt)
        elif play.operator == 'Schieben':
            # AI lead wants to pass — check if partner is human
            partner = play.partner[play.first]
            if partner == 'comps':
                # Post-schieben: human must choose_trump; schieben is NOT allowed.
                prompt = {"type": "trump_request", "can_schieben": False}
                await websocket.send_json(prompt)
                while True:
                    msg = await websocket.receive_json()
                    mtype = msg.get('type')
                    if mtype == 'choose_trump' and 'suit' in msg:
                        play.operator = msg['suit']
                        play.starter = 'comps'
                        chooser = 'Du'
                        break
                    await websocket.send_json({
                        "type": "error",
                        "message": (
                            f"Erwartet: 'choose_trump', erhalten: {mtype!r}."
                        ),
                    })
                    await websocket.send_json(prompt)
            else:
                play.operator = trumpfs(play.__dict__[partner])
                play.starter = partner
                chooser = POSITION_NAMES[partner]
        else:
            # AI already chose — just inform client
            chooser = POSITION_NAMES[play.first]

        await websocket.send_json({
            "type": "trump_chosen",
            "suit": play.operator,
            "by": chooser,
        })

    async def _weis_phase(self, websocket, play: Play) -> None:
        """Handle weis declaration. Asks human if they have combinations; AI always announces."""
        human_weis = describe_weis(wiis(play.comps), wiis_gleiche(play.comps))
        weis_announce = {}

        if human_weis:
            await websocket.send_json({"type": "weis_request", "your_weis": human_weis})
            msg = await websocket.receive_json()
            if msg.get('announce'):
                # Subset selection per skill: if `weis` is a non-empty list,
                # announce only the entries whose `name` is in that list.
                # Empty / missing `weis` falls back to legacy all-announce.
                selected = msg.get('weis')
                if isinstance(selected, list) and selected:
                    selected_set = set(selected)
                    filtered = [w for w in human_weis if w['name'] in selected_set]
                    if filtered:
                        weis_announce['comps'] = filtered
                else:
                    weis_announce['comps'] = human_weis

        # AI players always announce if they have weis
        for player in ['compo', 'compn', 'compe']:
            pw = describe_weis(
                wiis(play.__dict__[player]),
                wiis_gleiche(play.__dict__[player]),
            )
            if pw:
                weis_announce[player] = pw

        sn_pts = sum(w['points'] for p in SN_PLAYERS if p in weis_announce
                     for w in weis_announce[p])
        ow_pts = sum(w['points'] for p in OW_PLAYERS if p in weis_announce
                     for w in weis_announce[p])
        self.point_sn += sn_pts
        self.point_ow += ow_pts

        announcements = [
            {
                "player": POSITION_NAMES[p],
                "weis": weis_announce[p],
                "points": sum(w['points'] for w in weis_announce[p]),
            }
            for p in PLAYERS if p in weis_announce
        ]
        await websocket.send_json({
            "type": "weis_result",
            "announcements": announcements,
            "scores": {"sn": self.point_sn, "ow": self.point_ow},
        })

    async def _play_trick(self, websocket, play: Play) -> tuple:
        """Play one trick.

        Returns a ``(winner_key, trick_points)`` tuple:
          * ``winner_key`` — internal player key of the trick winner.
          * ``trick_points`` — integer point value of *this* trick only
            (needed by ``_run_spiel`` to populate the ``trick_end.points``
            field mandated by the schieber-protocol skill).
        """
        trick = {}
        lead_suit = None
        player = play.first

        for i in range(4):
            card = None
            if player == 'comps':
                valid = get_valid_cards(play.comps, lead_suit, play.operator)
                await websocket.send_json({"type": "your_turn", "valid_cards": valid})
                while True:
                    msg = await websocket.receive_json()
                    if msg['type'] != 'play_card':
                        continue
                    found, suit = find_card_in_hand(msg['card'], play.comps)
                    if found is not None and msg['card'] in valid:
                        play.comps[suit].remove(found)
                        card = found
                        break
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Ungültige Karte: {msg.get('card')}",
                    })
                    await websocket.send_json({"type": "your_turn", "valid_cards": valid})
            else:
                card = ai_select_card(play.__dict__[player], lead_suit, play.operator)
                play.__dict__[player][card.suit].remove(card)
                await asyncio.sleep(0.8)

            if i == 0:
                lead_suit = card.suit
            trick[player] = card

            await websocket.send_json({
                "type": "card_played",
                "player": POSITION_NAMES[player],
                "player_key": player,
                "card": card_to_code(card),
            })
            player = play.folger[player]

        winner = determine_trick_winner(trick, play.first, play.operator, play.folger)
        pts = trick_points(trick, play.operator)
        if winner in SN_PLAYERS:
            self.point_sn += pts
        else:
            self.point_ow += pts
        return winner, pts

    async def _run_spiel(self, websocket, spiel_num: int) -> None:
        """Deal, trump, weis, then 9 tricks for one Spiel."""
        play = Play(spiel_num)
        await websocket.send_json(self._initial_state(play))
        await self._trump_phase(websocket, play)
        await self._weis_phase(websocket, play)

        for trick_num in range(9):
            winner, trick_pts = await self._play_trick(websocket, play)
            is_last = trick_num == 8
            if is_last:
                if winner in SN_PLAYERS:
                    self.point_sn += 5   # last trick bonus
                else:
                    self.point_ow += 5
            play.first = winner  # trick winner leads next
            await websocket.send_json({
                "type": "trick_end",
                "winner": POSITION_NAMES[winner],
                "winner_key": winner,
                "points": trick_pts,          # per-trick value (skill contract)
                "points_sn": self.point_sn,   # optional running team totals
                "points_ow": self.point_ow,
            })

        # round_end winner_team uses sn/ow/tie tokens (skill contract), not
        # the long strings returned by utils.game_utils.get_winner. It reflects
        # the team leading after THIS round's totals, not the game winner.
        if self.point_sn > self.point_ow:
            round_winner = "sn"
        elif self.point_ow > self.point_sn:
            round_winner = "ow"
        else:
            round_winner = "tie"
        await websocket.send_json({
            "type": "round_end",
            "score_sn": self.point_sn,
            "score_ow": self.point_ow,
            "winner_team": round_winner,
            "target": self.end_game,
        })

    async def run(self, websocket) -> None:
        """Main loop: cycles through 4 Spiele per round until end_game score is reached."""
        spiel_num = 0
        while True:
            spiel_num = (spiel_num % 4) + 1
            await self._run_spiel(websocket, spiel_num)
            if check_game_end(self.point_sn, self.point_ow, self.end_game):
                if self.point_sn > self.point_ow:
                    game_winner = "sn"
                elif self.point_ow > self.point_sn:
                    game_winner = "ow"
                else:
                    game_winner = "tie"
                await websocket.send_json({
                    "type": "game_end",
                    "winner_team": game_winner,
                    "final_scores": {"sn": self.point_sn, "ow": self.point_ow},
                })
                return
            await asyncio.sleep(2)  # pause between Spiele
