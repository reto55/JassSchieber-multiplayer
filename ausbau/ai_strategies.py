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


def make_strategy(difficulty: str, position: str) -> AIStrategy:
    if difficulty == "easy":
        return EasyStrategy(position)
    if difficulty == "medium":
        return MediumStrategy(position)
    if difficulty == "hard":
        return HardStrategy(position)
    raise ValueError(f"unknown difficulty: {difficulty!r}")
