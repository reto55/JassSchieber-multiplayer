import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
import time
from typing import Optional
from Cards_refactored import (
    Play, SUITS, PLAY_MODES, Card,
    determine_trumpf, determine_trumpf_after_schieben, wiis, wiis_gleiche,
)
from utils.game_utils import check_game_end
from ausbau.room import RECONNECT_GRACE_SECONDS, principal_id

logger = logging.getLogger(__name__)

SUIT_PREFIX = {'Eicheln': 'E', 'Rosen': 'R', 'Schellen': 'SE', 'Schilten': 'SI'}
RANK_SUFFIX = {9: 'A', 8: 'K', 7: 'O', 6: 'U', 5: 'B', 4: '9', 3: '8', 2: '7', 1: '6'}

POSITION_NAMES = {'comps': 'Süd', 'compn': 'Nord', 'compo': 'Ost', 'compe': 'West'}
SN_PLAYERS = {'comps', 'compn'}
OW_PLAYERS = {'compo', 'compe'}
PLAYERS = ['comps', 'compo', 'compn', 'compe']
TRUMP_OPTIONS = ("Eicheln", "Rosen", "Schellen", "Schilten", "Oben", "Unten")


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
    def __init__(
        self,
        *,
        code: str = "",
        host_principal_id: str = "",
        variant=None,                     # type: Variant | None
        end_game: int = 1000,
        principal=None,                   # legacy: from sub-project B's WS principal injection
    ):
        from ausbau.room import POSITIONS, Seat, Variant
        self.code = code
        self.variant = variant if variant is not None else Variant()
        self.end_game = end_game
        self.host_principal_id = host_principal_id
        self.principal = principal        # legacy compatibility for old /ws code path

        # Lobby state
        self.seats = [Seat(position=POSITIONS[i]) for i in range(4)]
        self.spectators = []
        self.state = "lobby"

        # Game state (set when start() is called in Part 2)
        self.point_sn = 0
        self.point_ow = 0
        self.current_play = None

        # Concurrency primitives
        self._lock = asyncio.Lock()
        self._reconnect_tasks = {}
        self._game_task = None
        self._completed_tricks = []
        self._swap_requests = {}

    def _seat(self, position: str):
        for s in self.seats:
            if s.position == position:
                return s
        raise KeyError(f"unknown position: {position}")

    def _seat_for_principal(self, principal):
        from ausbau.room import principal_id
        pid = principal_id(principal)
        for s in self.seats:
            if s.principal is not None and principal_id(s.principal) == pid:
                return s
        return None

    def _spectator_for_principal(self, principal):
        from ausbau.room import principal_id
        pid = principal_id(principal)
        for spec in self.spectators:
            if principal_id(spec.principal) == pid:
                return spec
        return None

    def _seat_to_dict(self, seat) -> dict:
        from ausbau.room import principal_id
        return {
            "position": seat.position,
            "display_name": seat.display_name(),
            "is_ai": seat.is_ai,
            "connected": seat.websocket is not None and not seat.is_ai,
            "is_host": (
                seat.principal is not None
                and principal_id(seat.principal) == self.host_principal_id
            ),
            "principal_id": (
                principal_id(seat.principal) if seat.principal is not None else None
            ),
        }

    async def _transfer_host(self):
        """Pick oldest-connected human as new host. No-op if none connected."""
        from ausbau.room import principal_id
        candidates = [
            s for s in self.seats
            if not s.is_ai and s.websocket is not None and s.connected_since is not None
        ]
        if not candidates:
            return
        candidates.sort(key=lambda s: (s.connected_since, principal_id(s.principal)))
        new_host = candidates[0]
        old_host_pos = next(
            (s.position for s in self.seats
             if s.principal is not None and principal_id(s.principal) == self.host_principal_id),
            None
        )
        self.host_principal_id = principal_id(new_host.principal)
        msg = {
            "type": "host_changed",
            "old_host_position": old_host_pos,
            "new_host_position": new_host.position,
            "new_host_display_name": new_host.display_name(),
        }
        for seat in self.seats:
            if seat.websocket is not None and not seat.is_ai:
                try:
                    await seat.websocket.send_json(msg)
                except Exception:
                    pass
        for spec in list(self.spectators):
            try:
                if spec.websocket is not None:
                    await spec.websocket.send_json(msg)
            except Exception:
                pass

    async def send_to_seat(self, position: str, msg: dict) -> None:
        """Send a message to one seat's WS. No-op if AI or disconnected."""
        seat = self._seat(position)
        if seat.websocket is None or seat.is_ai:
            return
        try:
            await seat.websocket.send_json(msg)
        except Exception:
            await self._disconnect_seat(position)

    async def broadcast(self, msg: dict, *, except_seat: str | None = None) -> None:
        """Send to all seats + spectators. except_seat skips one seat."""
        for seat in self.seats:
            if seat.position != except_seat:
                await self.send_to_seat(seat.position, msg)
        for spec in list(self.spectators):
            try:
                if spec.websocket is not None:
                    await spec.websocket.send_json(msg)
            except Exception:
                self.spectators.remove(spec)

    async def broadcast_per_seat(self, msg_factory) -> None:
        """Each seat receives msg_factory(seat). Spectators receive msg_factory(None)."""
        for seat in self.seats:
            await self.send_to_seat(seat.position, msg_factory(seat))
        tv_msg = msg_factory(None)
        for spec in list(self.spectators):
            try:
                if spec.websocket is not None:
                    await spec.websocket.send_json(tv_msg)
            except Exception:
                self.spectators.remove(spec)

    async def _disconnect_seat(self, position: str) -> None:
        """Drop a seat's connection.

        - Idempotent for AI / already-disconnected seats (early return).
        - In ``lobby``: seat drops to AI immediately (no grace), broadcasts
          ``seat_changed`` with ``reason="disconnect"``. If the
          disconnecting seat was the host, transfer host.
        - Mid-game: schedule a 60s reconnect grace via
          ``_reconnect_timeout``, broadcast ``seat_paused`` with the
          countdown, and wake any phase awaiter via ``state_event.set()``.
        """
        seat = self._seat(position)
        if seat.is_ai or seat.websocket is None:
            return
        try:
            await seat.websocket.close()
        except Exception:
            pass
        seat.websocket = None
        seat.connected_since = None

        if self.state == "lobby":
            # No grace in lobby; drop seat to AI immediately.
            was_host = (
                seat.principal is not None
                and principal_id(seat.principal) == self.host_principal_id
            )
            seat.principal = None
            seat.is_ai = True
            seat.reconnect_deadline = None
            await self.broadcast({
                "type": "seat_changed",
                "seat": self._seat_to_dict(seat),
                "reason": "disconnect",
            })
            if was_host:
                await self._transfer_host()
            return

        # Mid-game: 60s grace window.
        seat.reconnect_deadline = time.monotonic() + RECONNECT_GRACE_SECONDS
        await self.broadcast({
            "type": "seat_paused",
            "position": position,
            "reconnect_deadline_secs": RECONNECT_GRACE_SECONDS,
            "display_name": seat.display_name(),
        })
        self._reconnect_tasks[position] = asyncio.create_task(
            self._reconnect_timeout(position),
            name=f"reconnect_timeout:{self.code}:{position}",
        )
        seat.state_event.set()  # wake any phase awaiter

    async def _reconnect_timeout(self, position: str) -> None:
        """Fires ``RECONNECT_GRACE_SECONDS`` after a mid-game disconnect.

        If the seat reclaimed in time (``websocket`` is not None) this is
        a no-op: the reclaiming code path is responsible for cancelling
        the timer task. Otherwise, flip the seat to AI but KEEP
        ``seat.principal`` so the original human can still reclaim by
        reconnecting later. If the timed-out seat was host, transfer
        host (per spec §8.2).
        """
        try:
            await asyncio.sleep(RECONNECT_GRACE_SECONDS)
        except asyncio.CancelledError:
            return
        seat = self._seat(position)
        if seat.websocket is not None:
            return  # raced; reclaimed before timeout
        was_host = (
            seat.principal is not None
            and principal_id(seat.principal) == self.host_principal_id
        )
        seat.is_ai = True
        seat.reconnect_deadline = None
        self._reconnect_tasks.pop(position, None)
        await self.broadcast({"type": "seat_ai_takeover", "position": position})
        if was_host:
            await self._transfer_host()
        seat.state_event.set()

    async def _reclaim_seat(self, position: str, websocket, principal) -> None:
        """Stub — full implementation in Task 13."""
        seat = self._seat(position)
        seat.websocket = websocket
        seat.is_ai = False
        seat.principal = principal
        # Cancel any pending reconnect timer
        task = self._reconnect_tasks.pop(position, None)
        if task is not None and not task.done():
            task.cancel()

    def _room_resume_message_for(self, position):
        """Stub — full implementation in Task 15."""
        return {
            "type": "room_resume",
            "phase": self.state,
            "your_position": position,
            "scores": {"sn": self.point_sn, "ow": self.point_ow},
        }

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

    async def _trump_phase(self, play: Play) -> None:
        """Multi-seat trump selection.

        The seat whose turn it is to choose receives `trump_request`.
        Other seats + spectators receive `trump_pending`.
        On invalid input the same seat is re-prompted (state preserved:
        if a `schieben` already happened, schieben_allowed stays False).
        Final choice is broadcast as `trump_chosen`.
        """
        target_position = play.first
        schieben_used = False

        # Initial prompt for the lead.
        await self.send_to_seat(target_position, {
            "type": "trump_request",
            "schieben_allowed": True,
        })
        await self.broadcast({
            "type": "trump_pending",
            "by_position": target_position,
        }, except_seat=target_position)

        while True:
            schieben_allowed = not schieben_used
            msg = await self._await_seat_action(target_position, valid_actions={
                "type": "trump",
                "options": list(TRUMP_OPTIONS),
                "schieben_allowed": schieben_allowed,
                # Hand is needed by `_compute_ai_action` for AI seats; humans
                # ignore it. The phase still owns validation of the reply.
                # `getattr(..., None)` keeps `FakePlay` test doubles working.
                "hand": getattr(play, target_position, None),
            })

            mtype = msg.get("type") if isinstance(msg, dict) else None

            if mtype == "schieben" and schieben_allowed:
                schieben_used = True
                target_position = self._partner_of(target_position)
                await self.send_to_seat(target_position, {
                    "type": "trump_request",
                    "schieben_allowed": False,
                })
                await self.broadcast({
                    "type": "trump_pending",
                    "by_position": target_position,
                }, except_seat=target_position)
                continue

            if mtype != "choose_trump":
                await self.send_to_seat(target_position, {
                    "type": "error",
                    "message": f"invalid action: {mtype!r}",
                })
                # Re-prompt the same seat with current schieben state.
                await self.send_to_seat(target_position, {
                    "type": "trump_request",
                    "schieben_allowed": schieben_allowed,
                })
                continue

            operator = msg.get("operator") if isinstance(msg, dict) else None
            if operator not in TRUMP_OPTIONS:
                await self.send_to_seat(target_position, {
                    "type": "error",
                    "message": f"invalid trump: {operator}",
                })
                await self.send_to_seat(target_position, {
                    "type": "trump_request",
                    "schieben_allowed": schieben_allowed,
                })
                continue

            play.operator = operator
            await self.broadcast({
                "type": "trump_chosen",
                "by_position": target_position,
                "operator": operator,
            })
            return

    def _partner_of(self, position: str) -> str:
        partners = {"compo": "compe", "compe": "compo",
                    "compn": "comps", "comps": "compn"}
        return partners[position]

    async def _await_seat_action(self, position: str, valid_actions: dict) -> dict:
        """Wait for an action from a seat. Routes to AI or human queue.

        - AI seats compute synchronously via ``_compute_ai_action``.
        - Human + connected seats dequeue ONE message from
          ``seat.incoming`` and return it. The phase loop owns
          validation and may re-prompt.
        - Human + disconnected seats (``websocket is None``) block on
          ``seat.state_event`` until a reclaim or AI-takeover (Task 14)
          flips the state, then re-evaluate.

        The queue read does NOT raise WS errors — the WS reader task
        feeds the queue and dies separately on disconnect; the
        ``state_event`` wait covers the disconnect-mid-await case.
        """
        seat = self._seat(position)
        while True:
            if seat.is_ai:
                return self._compute_ai_action(seat, valid_actions)
            if seat.websocket is None:
                seat.state_event.clear()
                await seat.state_event.wait()
                continue
            # Human + connected: pull one message from the per-seat queue.
            msg = await seat.incoming.get()
            return msg

    def _compute_ai_action(self, seat, valid_actions: dict) -> dict:
        """Compute a synchronous AI action from a phase prompt.

        ``trump`` → use ``utils.card_utils.farbe_lang`` over the seat's
        hand (passed in via ``valid_actions["hand"]``) to pick the
        longest suit; AI never schiebens at this stage.

        ``play_card`` → use ``ai_select_card(hand, lead_suit, operator)``
        from this module. ``hand`` comes via ``valid_actions["hand"]``.

        Anything else (or missing hand) returns a safe ``noop`` /
        first-valid fallback. Phases that drive the AI MUST pass
        ``hand`` in ``valid_actions``.
        """
        action_type = valid_actions.get("type")
        if action_type == "trump":
            hand = valid_actions.get("hand")
            if hand is None:
                # Defensive fallback — phase should always provide hand.
                return {"type": "choose_trump", "operator": "Eicheln"}
            from utils.card_utils import farbe_lang
            operator = farbe_lang(hand)
            return {"type": "choose_trump", "operator": operator}
        if action_type == "play_card":
            hand = valid_actions.get("hand")
            if hand is None:
                valid = valid_actions.get("valid_cards") or []
                if valid:
                    return {"type": "play_card", "card": valid[0]}
                return {"type": "noop"}
            lead_suit = valid_actions.get("lead_suit")
            operator = valid_actions.get("operator", "")
            card = ai_select_card(hand, lead_suit, operator)
            return {"type": "play_card", "card": card_to_code(card)}
        return {"type": "noop"}

    async def _trump_phase_legacy(self, websocket, play: Play) -> None:
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
                    play.operator = determine_trumpf_after_schieben(play.compn)
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
                play.operator = determine_trumpf_after_schieben(play.__dict__[partner])
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

    async def _weis_phase(self, play: Play) -> None:
        """Multi-seat weis declaration.

        Per the schieber-protocol skill:

          - Each seat receives a private ``weis_request`` carrying ONLY
            their own eligible weis as ``your_weis`` (per-seat redaction;
            never reveal another seat's weis here).
          - Each seat replies with
            ``{"type": "announce_weis", "announce": bool, "weis": ?}``.
            ``announce=False`` (or empty ``weis`` list) → seat declines.
            ``announce=True`` with no/None ``weis`` → announce all of
            ``your_weis``. ``announce=True`` with a list of names →
            announce only the matching subset (entries not present in
            ``your_weis`` are dropped).
          - AI seats auto-announce all their eligible weis.
          - The team with the higher sum of declared weis points wins
            (``winning_team`` ∈ {"sn", "ow", "tie"}). On a tie no team
            scores.  (Task 11 simplification — full strongest-weis
            tiebreak per Schieber rules is left for a later task.)
          - Server broadcasts ``weis_resolution`` with
            ``weis_by_position`` populated only for seats that declared.
        """
        # Per-position eligible weis (used to validate declarations and as
        # the AI auto-announce default).
        hand_for = {pos: getattr(play, pos) for pos in PLAYERS}
        eligible: dict[str, list] = {}
        for pos in PLAYERS:
            eligible[pos] = describe_weis(
                wiis(hand_for[pos]),
                wiis_gleiche(hand_for[pos]),
            )

        # Send each seat their (and only their) prompt.
        for pos in PLAYERS:
            await self.send_to_seat(pos, {
                "type": "weis_request",
                "your_weis": eligible[pos],
            })

        # Collect announcements per seat. Mirror `_trump_phase`'s tight
        # contract: the only acceptable shape is
        # ``{"type": "announce_weis", "announce": bool, "weis": ?}``. Any
        # other type or non-dict payload triggers an `error` reply followed
        # by a fresh `weis_request` for the SAME seat (per-seat re-prompt
        # loop). `announce` MUST be a bool — missing or wrong type also
        # re-prompts. Only a valid `announce_weis` message proceeds.
        declared: dict[str, list] = {}
        for pos in PLAYERS:
            seat = self._seat(pos)
            own = eligible[pos]
            if seat.is_ai:
                # TODO(future): support bluffing / strategic withholding when sub-project C lands.
                # AI auto-announces everything eligible.
                if own:
                    declared[pos] = own
                continue

            while True:
                msg = await self._await_seat_action(pos, valid_actions={
                    "type": "weis",
                })
                if not isinstance(msg, dict):
                    await self.send_to_seat(pos, {
                        "type": "error",
                        "message": (
                            f"Erwartet: 'announce_weis', erhalten: {msg!r}."
                        ),
                    })
                    await self.send_to_seat(pos, {
                        "type": "weis_request",
                        "your_weis": own,
                    })
                    continue
                mtype = msg.get("type")
                if mtype != "announce_weis":
                    await self.send_to_seat(pos, {
                        "type": "error",
                        "message": (
                            f"Erwartet: 'announce_weis', erhalten: {mtype!r}."
                        ),
                    })
                    await self.send_to_seat(pos, {
                        "type": "weis_request",
                        "your_weis": own,
                    })
                    continue
                announce = msg.get("announce")
                if not isinstance(announce, bool):
                    await self.send_to_seat(pos, {
                        "type": "error",
                        "message": (
                            f"Erwartet: 'announce' als bool, erhalten: {announce!r}."
                        ),
                    })
                    await self.send_to_seat(pos, {
                        "type": "weis_request",
                        "your_weis": own,
                    })
                    continue
                # Valid `announce_weis` — process it and break the per-seat loop.
                if not announce:
                    break
                selected = msg.get("weis")
                if isinstance(selected, list) and selected:
                    names = set(selected)
                    filtered = [w for w in own if w["name"] in names]
                    if filtered:
                        declared[pos] = filtered
                elif own:
                    # announce=True with no/empty selection → announce all.
                    declared[pos] = own
                break

        # Tally per team.
        sn_pts = sum(w["points"] for p in SN_PLAYERS if p in declared
                     for w in declared[p])
        ow_pts = sum(w["points"] for p in OW_PLAYERS if p in declared
                     for w in declared[p])

        if sn_pts > ow_pts:
            winning_team = "sn"
            self.point_sn += sn_pts
        elif ow_pts > sn_pts:
            winning_team = "ow"
            self.point_ow += ow_pts
        else:
            # Tie (covers the both-zero case too) → no points awarded.
            winning_team = "tie"

        await self.broadcast({
            "type": "weis_resolution",
            "winning_team": winning_team,
            "weis_by_position": declared,
        })

    async def _weis_phase_legacy(self, websocket, play: Play) -> None:
        """Handle weis declaration. Asks human if they have combinations; AI always announces.

        Legacy single-WS path. Multi-seat callers use ``_weis_phase``.
        """
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

    async def _play_trick(self, play: Play) -> tuple:
        """Multi-seat trick loop (Task 12).

        Drives one trick across all four seats:

          - The active seat receives ``play_request`` with their own
            ``valid_cards`` and the cumulative ``trick_so_far``.
          - Other seats + spectators receive ``play_pending`` with the
            same ``trick_so_far`` snapshot and ``by_position`` set to
            the active seat.
          - Each completed play is broadcast as ``card_played``.
          - At trick close, ``trick_end`` is broadcast with
            ``{winner_position, winner_team, points}`` per the
            ``schieber-protocol`` skill (multi-seat shape — no running
            totals; those go in ``spiel_end`` / ``game_end``).

        Validation invariants mirror the trump / weis phases: malformed
        ``play_card`` messages trigger an ``error`` reply followed by a
        fresh ``play_request`` on the SAME seat. Only a valid
        ``play_card`` whose ``card`` resolves to a card in the seat's
        own valid-cards list breaks the per-seat loop.

        AI seats route through ``_compute_ai_action`` (synchronous —
        no artificial delay; tests run zero-latency).

        Returns ``(winner_position, trick_points)``.
        """
        trick: dict = {}
        lead_suit: Optional[str] = None
        player = play.first
        trick_order: list[dict] = []  # cumulative [{"position", "card"}, ...]

        for i in range(4):
            hand = getattr(play, player)
            valid = get_valid_cards(hand, lead_suit, play.operator)

            request_payload = {
                "type": "play_request",
                "trick_so_far": list(trick_order),
                "lead_suit": lead_suit,
                "valid_cards": valid,
            }

            await self.send_to_seat(player, request_payload)
            await self.broadcast({
                "type": "play_pending",
                "by_position": player,
                "trick_so_far": list(trick_order),
            }, except_seat=player)

            # Per-seat receive loop with re-prompt on malformed input.
            while True:
                msg = await self._await_seat_action(player, valid_actions={
                    "type": "play_card",
                    "lead_suit": lead_suit,
                    "operator": play.operator,
                    "valid_cards": valid,
                    # AI seats need the live hand to pick a card via
                    # `ai_select_card`. Humans ignore it.
                    "hand": hand,
                })

                if not isinstance(msg, dict):
                    await self.send_to_seat(player, {
                        "type": "error",
                        "message": (
                            f"Erwartet: 'play_card', erhalten: {msg!r}."
                        ),
                    })
                    await self.send_to_seat(player, request_payload)
                    continue
                mtype = msg.get("type")
                if mtype != "play_card":
                    await self.send_to_seat(player, {
                        "type": "error",
                        "message": (
                            f"Erwartet: 'play_card', erhalten: {mtype!r}."
                        ),
                    })
                    await self.send_to_seat(player, request_payload)
                    continue
                code = msg.get("card")
                if not isinstance(code, str):
                    await self.send_to_seat(player, {
                        "type": "error",
                        "message": (
                            "Ungültige Karte: 'card' fehlt oder ist kein String."
                        ),
                    })
                    await self.send_to_seat(player, request_payload)
                    continue
                if code not in valid:
                    await self.send_to_seat(player, {
                        "type": "error",
                        "message": f"Ungültige Karte: {code!r}.",
                    })
                    await self.send_to_seat(player, request_payload)
                    continue
                found, suit = find_card_in_hand(code, hand)
                if found is None:
                    await self.send_to_seat(player, {
                        "type": "error",
                        "message": f"Karte nicht im Blatt: {code}.",
                    })
                    await self.send_to_seat(player, request_payload)
                    continue
                hand[suit].remove(found)
                card = found
                break

            if i == 0:
                lead_suit = card.suit
            trick[player] = card
            trick_order.append({"position": player, "card": card_to_code(card)})

            await self.broadcast({
                "type": "card_played",
                "by_position": player,
                "card": card_to_code(card),
            })
            player = play.folger[player]

        winner = determine_trick_winner(trick, play.first, play.operator, play.folger)
        pts = trick_points(trick, play.operator)
        if winner in SN_PLAYERS:
            self.point_sn += pts
            winner_team = "sn"
        else:
            self.point_ow += pts
            winner_team = "ow"

        await self.broadcast({
            "type": "trick_end",
            "winner_position": winner,
            "winner_team": winner_team,
            "points": pts,
        })

        return winner, pts

    async def _play_trick_legacy(self, websocket, play: Play) -> tuple:
        """Legacy single-WS trick loop.

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
                prompt = {"type": "your_turn", "valid_cards": valid}
                await websocket.send_json(prompt)
                while True:
                    msg = await websocket.receive_json()
                    # Tolerate any shape: mirror the hardening in
                    # `_trump_phase` / `_weis_phase`. Per the schieber-protocol
                    # skill invariant §5 ("No silent failures…server responds
                    # with `error` and re-sends the most recent prompt"),
                    # malformed messages must be rejected with an `error`
                    # payload followed by a fresh `your_turn`. Only a valid
                    # `play_card` with a `card` string pointing to a card in
                    # the valid list breaks the loop.
                    if not isinstance(msg, dict):
                        await websocket.send_json({
                            "type": "error",
                            "message": "Ungültige Nachricht. Erwartet: 'play_card'.",
                        })
                        await websocket.send_json(prompt)
                        continue
                    mtype = msg.get('type')
                    if mtype != 'play_card':
                        await websocket.send_json({
                            "type": "error",
                            "message": (
                                f"Erwartet: 'play_card', erhalten: {mtype!r}."
                            ),
                        })
                        await websocket.send_json(prompt)
                        continue
                    code = msg.get('card')
                    if not isinstance(code, str):
                        await websocket.send_json({
                            "type": "error",
                            "message": "Ungültige Karte: 'card' fehlt oder ist kein String.",
                        })
                        await websocket.send_json(prompt)
                        continue
                    found, suit = find_card_in_hand(code, play.comps)
                    if found is not None and code in valid:
                        play.comps[suit].remove(found)
                        card = found
                        break
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Ungültige Karte: {code}",
                    })
                    await websocket.send_json(prompt)
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
        await self._trump_phase_legacy(websocket, play)
        await self._weis_phase_legacy(websocket, play)

        for trick_num in range(9):
            winner, trick_pts = await self._play_trick_legacy(websocket, play)
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
        name = (
            getattr(self.principal, "display_name", None)
            or getattr(self.principal, "username", None)
            or "anonymous"
        )
        logger.info("game start by %s", name)
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
