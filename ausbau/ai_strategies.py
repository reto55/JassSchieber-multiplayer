"""AI strategies for Schieber (sub-project C).

Three difficulty levels — `easy`, `medium`, `hard` — each implementing
`pick_trump` and `pick_card` plus optional lifecycle hooks. Selected
per-seat via `Seat.ai_difficulty`; instantiated via `make_strategy`.
"""
from __future__ import annotations

import random
from typing import Optional


TRUMP_OPTIONS = ("Eicheln", "Rosen", "Schellen", "Schilten", "Oben", "Unten")


class AIStrategy:
    """Abstract base. Subclasses override pick_trump / pick_card.

    Strategies are bound to a position string at construction so they can
    look up their own hand on the live `play` object via
    `getattr(play, self.position)`. They do NOT hold a reference to the
    Seat — `play` is passed on every call.
    """

    def __init__(self, position: str):
        self.position = position

    def pick_trump(self, play, schieben_allowed: bool) -> dict:
        raise NotImplementedError

    def pick_card(self, play, lead_suit: Optional[str], trick_so_far: list) -> dict:
        raise NotImplementedError

    def on_spiel_start(self, play) -> None:
        """Lifecycle hook fired by _run_spiel before trump phase. Default no-op."""

    def on_card_played(self, player_position: str, card_code: str) -> None:
        """Lifecycle hook fired after each card_played broadcast. Default no-op."""


class EasyStrategy(AIStrategy):
    """Pure-random AI. Picks any of the 6 trump modes uniformly; never schiebens.

    For card play, picks any valid card with equal probability.
    """

    def pick_trump(self, play, schieben_allowed: bool) -> dict:
        return {"type": "choose_trump", "operator": random.choice(TRUMP_OPTIONS)}

    def pick_card(self, play, lead_suit, trick_so_far) -> dict:
        from ausbau.game_session import get_valid_cards
        hand = getattr(play, self.position)
        valid = get_valid_cards(
            hand, lead_suit, play.operator, trick_so_far=trick_so_far,
        )
        return {"type": "play_card", "card": random.choice(valid)}


class MediumStrategy(AIStrategy):
    """Today's hard-coded heuristic. farbe_lang for trump; ai_select_card for play."""

    def pick_trump(self, play, schieben_allowed: bool) -> dict:
        from utils.card_utils import farbe_lang
        hand = getattr(play, self.position)
        return {"type": "choose_trump", "operator": farbe_lang(hand)}

    def pick_card(self, play, lead_suit, trick_so_far) -> dict:
        from ausbau.game_session import ai_select_card, card_to_code
        hand = getattr(play, self.position)
        card = ai_select_card(
            hand, lead_suit, play.operator, trick_so_far=trick_so_far,
        )
        return {"type": "play_card", "card": card_to_code(card)}


class HardStrategy(AIStrategy):
    """Per-spiel card tracking + trump conservation + smarter trump pick
    + trump-drawing ("Trumpf ziehen") leading logic.

    Implementation lands across Tasks 3-6 plus the trump-draw extension.
    """

    def __init__(self, position: str):
        super().__init__(position)
        self._remaining_by_suit: dict[str, set[str]] = {}
        # ── Trump-draw state (rebuilt every spiel in on_spiel_start) ──────
        # The active trump suit (play.operator) once known, else None. Cached
        # from pick_trump / pick_card so on_card_played — which does NOT
        # receive play — can resolve "trump led" / "is trump" questions.
        self._operator: Optional[str] = None
        # Per-opponent "is void in trump" flag. Partner is never tracked.
        self._opp_void_trump: dict[str, bool] = {}
        # Per-position set of suits each player has shown (played). Own plays
        # never populate it.
        self._opp_shown_suits: dict[str, set[str]] = {}
        # Ordered (position, code) list reconstructing the current trick.
        # Reset every 4 cards; the first entry's suit is the lead suit.
        self._running_trick: list = []

    def _opponents(self, play) -> list:
        """The two non-self, non-partner positions."""
        partner = play.partner.get(self.position)
        return [p for p in ("comps", "compo", "compn", "compe")
                if p != self.position and p != partner]

    def on_spiel_start(self, play) -> None:
        """Rebuild _remaining_by_suit (deck minus own hand) and reset all
        trump-draw tracking state."""
        from Cards_refactored import SUITS
        from ausbau.game_session import SUIT_PREFIX, RANK_SUFFIX, hand_to_codes
        self._remaining_by_suit = {suit: set() for suit in SUITS}
        own = set(hand_to_codes(getattr(play, self.position)))
        for suit in SUITS:
            for rank in range(1, 10):
                code = SUIT_PREFIX[suit] + RANK_SUFFIX[rank]
                if code not in own:
                    self._remaining_by_suit[suit].add(code)

        # Reset trump-draw state. operator may not yet be chosen at spiel
        # start; it is cached lazily once pick_trump / pick_card sees it.
        self._operator = play.operator or None
        self._opp_void_trump = {p: False for p in self._opponents(play)}
        self._opp_shown_suits = {
            p: set() for p in ("comps", "compo", "compn", "compe")
        }
        self._running_trick = []

    def on_card_played(self, player_position: str, card_code: str) -> None:
        """Update remaining-card tracking, void-in-trump detection,
        shown-suit tracking and current-trick reconstruction.

        Fired for ALL seats in play order, including this AI's own plays
        (see game_session._play_trick line ~1277). Self-plays must not feed
        the opponent-facing tracking (remaining/void/shown), but DO advance
        the running-trick cursor so the lead-suit / 4-card-boundary logic
        stays in sync with the real table order.
        """
        from Cards_refactored import SUITS
        from ausbau.game_session import code_to_card

        try:
            card = code_to_card(card_code)
        except (ValueError, KeyError):
            return
        suit = card.suit

        # Lead suit of the in-progress trick (None if this card opens it).
        is_lead = not self._running_trick
        lead_suit_name = None
        if not is_lead:
            try:
                lead_suit_name = code_to_card(self._running_trick[0][1]).suit
            except (ValueError, KeyError):
                lead_suit_name = None

        if player_position != self.position:
            # Remaining-card tracking: we already know our own hand.
            self._remaining_by_suit.get(suit, set()).discard(card_code)
            # Shown-suit tracking (any suit the opponent reveals).
            self._opp_shown_suits.setdefault(player_position, set()).add(suit)
            # Void-in-trump detection (house rule): a trump was led
            # (lead suit == operator) and this opponent discarded a non-trump
            # card → they hold no trump. Note: a player whose only trump is
            # the trump Under may legally discard under the Under-holdback
            # house rule and be flagged "void" here. That imprecision is
            # harmless — a lone trump Under can never be forced out by
            # leading trump anyway, so treating its holder as void costs
            # nothing.
            if (
                self._operator in SUITS
                and not is_lead
                and lead_suit_name == self._operator
                and suit != self._operator
                and player_position in self._opp_void_trump
            ):
                self._opp_void_trump[player_position] = True

        # Append to the running trick; reset on the 4-card boundary.
        self._running_trick.append((player_position, card_code))
        if len(self._running_trick) >= 4:
            self._running_trick = []

    def pick_trump(self, play, schieben_allowed: bool) -> dict:
        from Cards_refactored import SUITS
        self._operator = play.operator or None
        hand = getattr(play, self.position)

        # 1. Find longest trump-candidate suit (with farbe_lang tie-break).
        priority = ["Schilten", "Schellen", "Eicheln", "Rosen"]
        best_suit = max(priority, key=lambda s: (len(hand[s]),
                                                  -priority.index(s)))
        ranks_in_best = {c.__class__.__name__ for c in hand[best_suit]}

        # 2. Commit when the best suit is decent.
        if len(hand[best_suit]) >= 4 and (
            "Under" in ranks_in_best or "Neun" in ranks_in_best
        ):
            return {"type": "choose_trump", "operator": best_suit}

        # 3. Schieben if allowed.
        if schieben_allowed:
            return {"type": "schieben"}

        # 4. Forced commit: score all 6 modes, pick max.
        scores: dict[str, int] = {}
        for suit in SUITS:
            scores[suit] = sum(c.wtrumpf for c in hand[suit])
        scores["Oben"] = sum(c.woben for s in SUITS for c in hand[s])
        scores["Unten"] = sum(c.wunten for s in SUITS for c in hand[s])

        # Tie-break: priority order over trump suits, then Oben, then Unten.
        ordered = priority + ["Oben", "Unten"]
        best_op = max(ordered, key=lambda op: (scores[op], -ordered.index(op)))
        return {"type": "choose_trump", "operator": best_op}

    def _card_value(self, card_obj, operator: str) -> int:
        """Per-card point value under the active operator."""
        from Cards_refactored import SUITS
        if operator in SUITS:
            return card_obj.wtrumpf if card_obj.suit == operator else card_obj.wfarbe
        if operator == "Oben":
            return card_obj.woben
        return card_obj.wunten

    def _strength(self, card_obj, operator: str, lead_suit: Optional[str]):
        """Comparable strength tuple — higher beats lower in same trick."""
        from Cards_refactored import SUITS
        if operator in SUITS:
            if card_obj.suit == operator:
                return (2, card_obj.trumpf)
            if card_obj.suit == lead_suit:
                return (1, card_obj.rank)
            return (0, 0)
        if operator == "Oben":
            return (1, card_obj.oben) if (lead_suit is None or card_obj.suit == lead_suit) else (0, 0)
        return (1, card_obj.unten) if (lead_suit is None or card_obj.suit == lead_suit) else (0, 0)

    def _is_guaranteed_winner(self, card_obj, play) -> bool:
        """True if this card is the highest remaining of its suit under
        play.operator semantics — i.e., guaranteed to win an opening lead."""
        remaining_codes = self._remaining_by_suit.get(card_obj.suit, set())
        if not remaining_codes:
            return True  # No competing cards exist anywhere.
        # Reconstruct strengths for remaining codes vs ours.
        from ausbau.game_session import code_to_card
        my_strength = self._strength(card_obj, play.operator, lead_suit=card_obj.suit)
        for code in remaining_codes:
            other = code_to_card(code)
            other_strength = self._strength(other, play.operator, lead_suit=card_obj.suit)
            if other_strength > my_strength:
                return False
        return True

    def _both_opponents_void_trump(self, play) -> bool:
        """True once BOTH opponents are known to hold no trump."""
        opps = self._opponents(play)
        return bool(opps) and all(
            self._opp_void_trump.get(p, False) for p in opps
        )

    def _lead(self, play, valid_cards) -> dict:
        """Trump-drawing leading logic.

        Precedence (trump modes only):
          A. Draw trump — if at least one opponent may still hold trump AND we
             still hold trump, lead our HIGHEST trump by ``card.trumpf``
             (classic Trumpf ziehen, top-down). Fires naturally for the
             declaring side because Schieben does not change ``play.first``.
          B. Both opponents void in trump — never open with trump. Lead the
             highest-value guaranteed winner if we hold one; else dump a low
             card into a non-trump suit an opponent has shown (and that still
             has outstanding cards) so partner — a remaining trump holder —
             can trump in; else today's lowest-card fallback.
          C. We hold no trump — rule A cannot fire; falls through to B.

        Non-trump modes (Oben / Unten) keep today's behaviour unchanged.
        """
        from Cards_refactored import SUITS
        from ausbau.game_session import card_to_code

        operator = play.operator

        # Non-trump modes: today's behaviour unchanged.
        if operator not in SUITS:
            return self._lead_legacy(play, valid_cards)

        my_trumps = [c for c in valid_cards if c.suit == operator]
        both_void = self._both_opponents_void_trump(play)

        # ── A. Draw trump ────────────────────────────────────────────────
        if my_trumps and not both_void:
            pick = max(my_trumps, key=lambda c: c.trumpf)
            return {"type": "play_card", "card": card_to_code(pick)}

        # ── B / C. Drawing complete (or we hold no trump) ────────────────
        # Cash the highest-POINT guaranteed winner first (key is point value,
        # not trick rank — every guaranteed winner already takes the lead, so
        # among them we prefer the one that banks the most points).
        winners = [c for c in valid_cards if self._is_guaranteed_winner(c, play)]
        if winners:
            pick = max(winners, key=lambda c: self._card_value(c, operator))
            return {"type": "play_card", "card": card_to_code(pick)}

        if both_void:
            shown_suits = set()
            for opp in self._opponents(play):
                shown_suits |= self._opp_shown_suits.get(opp, set())
            candidates = [
                c for c in valid_cards
                if c.suit != operator
                and c.suit in shown_suits
                and self._remaining_by_suit.get(c.suit)
            ]
            if candidates:
                low_key = lambda c: (self._card_value(c, operator), c.rank)
                pick = min(candidates, key=low_key)
                return {"type": "play_card", "card": card_to_code(pick)}

        # Fallback: lowest-card lead. In a trump mode we reach here with trump
        # still in hand only when drawing is complete (both opponents void) —
        # rule A already returned otherwise. Rule B forbids re-opening with
        # trump once drawn, so prefer any non-trump card; lead trump only if the
        # whole hand is trump.
        pool = valid_cards
        non_trump = [c for c in valid_cards if c.suit != operator]
        if non_trump:
            pool = non_trump
        pick = min(pool, key=lambda c: self._card_value(c, operator))
        return {"type": "play_card", "card": card_to_code(pick)}

    def _lead_legacy(self, play, valid_cards) -> dict:
        """Pre-trump-draw leading behaviour (used for no-trump modes)."""
        from ausbau.game_session import card_to_code
        winners = [c for c in valid_cards if self._is_guaranteed_winner(c, play)]
        if winners:
            pick = max(winners, key=lambda c: self._card_value(c, play.operator))
            return {"type": "play_card", "card": card_to_code(pick)}
        pick = min(valid_cards, key=lambda c: self._card_value(c, play.operator))
        return {"type": "play_card", "card": card_to_code(pick)}

    def pick_card(self, play, lead_suit: Optional[str], trick_so_far: list) -> dict:
        from ausbau.game_session import (
            get_valid_cards, find_card_in_hand, card_to_code,
        )
        # Cache the active trump suit so on_card_played (which never sees
        # play) can resolve "trump led" / "is trump" questions.
        self._operator = play.operator
        hand = getattr(play, self.position)
        valid_codes = get_valid_cards(
            hand, lead_suit, play.operator, trick_so_far=trick_so_far,
        )
        valid_cards = [find_card_in_hand(c, hand)[0] for c in valid_codes]

        # ── Leading ─────────────────────────────────────────────────────────
        if lead_suit is None:
            return self._lead(play, valid_cards)

        # ── Following ──────────────────────────────────────────────────────
        from Cards_refactored import SUITS
        operator = play.operator

        # Determine current trick winner.
        played = trick_so_far  # [{position, card}, ...] — at most 3
        winner_position = self._winner_so_far(played, operator)
        partner_position = play.partner.get(self.position)
        partner_winning = (winner_position == partner_position)

        # Sum points already on the table.
        from ausbau.game_session import code_to_card, card_to_code

        trick_total = sum(
            self._card_value(code_to_card(p["card"]), operator) for p in played
        )

        # Stable "lowest" key: point value first, then rank — so that when
        # two cards tie on point value (e.g. Sechs and Neun off-suit, both 0)
        # the truly lower-ranked one is dumped.
        low_key = lambda c: (self._card_value(c, operator), c.rank)

        if partner_winning:
            # Dump lowest valid card.
            pick = min(valid_cards, key=low_key)
            return {"type": "play_card", "card": card_to_code(pick)}

        # Opponent winning. Try to beat cheaply.
        winning_card = code_to_card(
            next(p["card"] for p in played if p["position"] == winner_position)
        )
        winning_strength = self._strength(winning_card, operator, lead_suit)

        beaters = [c for c in valid_cards
                   if self._strength(c, operator, lead_suit) > winning_strength]
        if beaters:
            cheapest = min(beaters, key=low_key)
            # Cheap take threshold: cheap enough vs. trick value.
            if self._card_value(cheapest, operator) <= trick_total + 5:
                # Trump conservation overlay — see below before returning.
                pick = cheapest
            else:
                pick = min(valid_cards, key=low_key)
        else:
            pick = min(valid_cards, key=low_key)

        # Trump-conservation overlay: don't burn trump on a cheap trick when
        # we have a non-trump alternative.
        if (
            operator in SUITS
            and pick.suit == operator
            and lead_suit != operator
            and trick_total < 18
        ):
            non_trump_alts = [c for c in valid_cards if c.suit != operator]
            if non_trump_alts:
                pick = min(non_trump_alts, key=low_key)

        # High-value trump steal: if trick is rich and we can trump in.
        if (
            operator in SUITS
            and lead_suit != operator
            and trick_total >= 18
            and not partner_winning
        ):
            trump_cards = [c for c in valid_cards if c.suit == operator]
            if trump_cards:
                pick = min(trump_cards, key=low_key)

        return {"type": "play_card", "card": card_to_code(pick)}

    def _winner_so_far(self, played: list, operator: str) -> Optional[str]:
        """Return position of the current trick winner among `played`. None if empty."""
        if not played:
            return None
        from ausbau.game_session import code_to_card

        lead_card = code_to_card(played[0]["card"])
        lead_suit = lead_card.suit
        winner = played[0]["position"]
        best = self._strength(lead_card, operator, lead_suit)
        for entry in played[1:]:
            c = code_to_card(entry["card"])
            s = self._strength(c, operator, lead_suit)
            if s > best:
                best = s
                winner = entry["position"]
        return winner


def make_strategy(difficulty: str, position: str) -> AIStrategy:
    if difficulty == "easy":
        return EasyStrategy(position)
    if difficulty == "medium":
        return MediumStrategy(position)
    if difficulty == "hard":
        return HardStrategy(position)
    raise ValueError(f"unknown difficulty: {difficulty!r}")
