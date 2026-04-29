"""AI strategies for Schieber (sub-project C).

Three difficulty levels — `easy`, `medium`, `hard` — each implementing
`pick_trump` and `pick_card` plus optional lifecycle hooks. Selected
per-seat via `Seat.ai_difficulty`; instantiated via `make_strategy`.
"""
from __future__ import annotations

import random
from typing import Optional


TRUMP_OPTIONS = ("Eicheln", "Rosen", "Schellen", "Schilten", "Oben", "Unten")


# Inverse of game_session.SUIT_PREFIX. Two-letter prefixes (`SE`, `SI`)
# come first in iteration so they're matched before single-letter `S`.
INVERSE_SUIT_PREFIX = {
    "SE": "Schellen",
    "SI": "Schilten",
    "E": "Eicheln",
    "R": "Rosen",
}


def _split_code(code: str) -> tuple[str, str]:
    """Return (suit_name, rank_suffix). 'SEK' → ('Schellen', 'K')."""
    for prefix in ("SE", "SI", "E", "R"):
        if code.startswith(prefix):
            return INVERSE_SUIT_PREFIX[prefix], code[len(prefix):]
    raise ValueError(f"bad card code: {code!r}")


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
        valid = get_valid_cards(hand, lead_suit, play.operator)
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
        card = ai_select_card(hand, lead_suit, play.operator)
        return {"type": "play_card", "card": card_to_code(card)}


class HardStrategy(AIStrategy):
    """Per-spiel card tracking + trump conservation + smarter trump pick.

    Implementation lands across Tasks 3-6.
    """

    def __init__(self, position: str):
        super().__init__(position)
        self._remaining_by_suit: dict[str, set[str]] = {}

    def on_spiel_start(self, play) -> None:
        """Rebuild _remaining_by_suit from the deck minus own hand."""
        from Cards_refactored import SUITS
        from ausbau.game_session import SUIT_PREFIX, RANK_SUFFIX, hand_to_codes
        self._remaining_by_suit = {suit: set() for suit in SUITS}
        own = set(hand_to_codes(getattr(play, self.position)))
        for suit in SUITS:
            for rank in range(1, 10):
                code = SUIT_PREFIX[suit] + RANK_SUFFIX[rank]
                if code not in own:
                    self._remaining_by_suit[suit].add(code)

    def on_card_played(self, player_position: str, card_code: str) -> None:
        """Remove a played card from tracking. No-op for own plays or unknowns."""
        if player_position == self.position:
            return
        try:
            suit, _ = _split_code(card_code)
        except ValueError:
            return
        self._remaining_by_suit.get(suit, set()).discard(card_code)

    def pick_trump(self, play, schieben_allowed: bool) -> dict:
        from Cards_refactored import SUITS
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
        from Cards_refactored import create_card
        from ausbau.game_session import RANK_SUFFIX
        inverse_rank = {v: k for k, v in RANK_SUFFIX.items()}
        my_strength = self._strength(card_obj, play.operator, lead_suit=card_obj.suit)
        for code in remaining_codes:
            if code == f"{card_obj.suit}":  # safety
                continue
            # Strip suit prefix to get rank
            from ausbau.ai_strategies import _split_code
            _, rank_suffix = _split_code(code)
            rank = inverse_rank[rank_suffix]
            other = create_card(rank, card_obj.suit)
            other_strength = self._strength(other, play.operator, lead_suit=card_obj.suit)
            if other_strength > my_strength:
                return False
        return True

    def pick_card(self, play, lead_suit: Optional[str], trick_so_far: list) -> dict:
        from ausbau.game_session import (
            get_valid_cards, find_card_in_hand, card_to_code,
        )
        hand = getattr(play, self.position)
        valid_codes = get_valid_cards(hand, lead_suit, play.operator)
        valid_cards = [find_card_in_hand(c, hand)[0] for c in valid_codes]

        # ── Leading ─────────────────────────────────────────────────────────
        if lead_suit is None:
            winners = [c for c in valid_cards if self._is_guaranteed_winner(c, play)]
            if winners:
                pick = max(winners, key=lambda c: self._card_value(c, play.operator))
                return {"type": "play_card", "card": card_to_code(pick)}
            pick = min(valid_cards, key=lambda c: self._card_value(c, play.operator))
            return {"type": "play_card", "card": card_to_code(pick)}

        # ── Following ──────────────────────────────────────────────────────
        # Implemented in Task 6.
        pick = min(valid_cards, key=lambda c: self._card_value(c, play.operator))
        return {"type": "play_card", "card": card_to_code(pick)}


def make_strategy(difficulty: str, position: str) -> AIStrategy:
    if difficulty == "easy":
        return EasyStrategy(position)
    if difficulty == "medium":
        return MediumStrategy(position)
    if difficulty == "hard":
        return HardStrategy(position)
    raise ValueError(f"unknown difficulty: {difficulty!r}")
