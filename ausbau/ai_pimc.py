"""Perfect-Information Monte Carlo (PIMC) engine for the Hard AI's leading
decision in trump modes.

Standalone and stateless: callers build an :class:`EngineState`, then call
:func:`pimc_choose_lead`. The engine samples deals consistent with the
observed constraints, rolls each out to the end of the spiel with the
heuristic playout policy, and returns the highest expected-value lead.

See docs/superpowers/specs/2026-06-15-schieber-ai-pimc-design.md.
"""
from dataclasses import dataclass
from typing import Optional

from Cards_refactored import SUITS, Under
from ausbau.game_session import (
    SN_PLAYERS, ai_select_card, determine_trick_winner, trick_points,
    card_to_code, _mode_multiplier,
)

# Tuning constants (see spec §6). Synchronous, time-boxed.
PIMC_DEADLINE_S = 0.12     # wall-clock budget per leading decision
PIMC_N = 80                # max sampled deals
PIMC_MIN_SAMPLES = 10      # below this, signal heuristic fallback


class SamplingError(Exception):
    """Raised when DealSampler cannot place all unseen cards under constraints."""


@dataclass
class EngineState:
    me: str                       # my position key, e.g. "comps"
    operator: str                 # trump suit (always in SUITS for PIMC use)
    partner: dict                 # play.partner mapping
    folger: dict                  # play.folger turn-order mapping
    my_hand: dict                 # {suit: [Card,...]} my known hand
    others: list                  # the 3 non-self positions (partner + 2 opps)
    hand_sizes: dict              # {position: int} remaining cards, the 3 others
    voids: dict                   # {position: set(suit)} known hard voids
    no_trump_except_under: set    # positions: "no trump except possibly Under"
    unseen: list                  # [Card,...] cards to distribute among `others`


def _to_hand_dict(cards) -> dict:
    """Group a flat list of Card objects into a {suit: [Card,...]} dict."""
    h = {s: [] for s in SUITS}
    for c in cards:
        h[c.suit].append(c)
    return h


class DealSampler:
    """Samples the 3 hidden hands consistent with an EngineState's constraints."""

    MAX_ATTEMPTS = 200

    def __init__(self, state: EngineState):
        self.state = state

    def _allowed_holders(self, card) -> list:
        """Positions that may legally hold `card` (ignoring capacity)."""
        st = self.state
        out = []
        for p in st.others:
            if card.suit in st.voids.get(p, set()):
                continue
            if (card.suit == st.operator
                    and p in st.no_trump_except_under
                    and not isinstance(card, Under)):
                continue
            out.append(p)
        return out

    def sample(self, rng) -> dict:
        """Return {position: {suit: [Card,...]}} for the 3 others. Raises
        SamplingError if no consistent assignment is found in MAX_ATTEMPTS."""
        st = self.state
        # Precompute allowed holders once; order most-constrained first.
        allowed = [(c, self._allowed_holders(c)) for c in st.unseen]
        allowed.sort(key=lambda pair: len(pair[1]))
        for _ in range(self.MAX_ATTEMPTS):
            cap = dict(st.hand_sizes)
            result = {p: [] for p in st.others}
            ok = True
            for card, holders in allowed:
                pool = [p for p in holders if cap[p] > 0]
                if not pool:
                    ok = False
                    break
                p = rng.choice(pool)
                result[p].append(card)
                cap[p] -= 1
            if ok and all(v == 0 for v in cap.values()):
                return {p: _to_hand_dict(result[p]) for p in st.others}
        raise SamplingError(
            f"no consistent deal in {self.MAX_ATTEMPTS} attempts")


def _clone_hand(hand: dict) -> dict:
    """Shallow-copy a {suit: [Card,...]} hand (Card objects are immutable here)."""
    return {s: list(hand.get(s, [])) for s in SUITS}


def _remove_card(hand: dict, card) -> None:
    """Remove `card` from a hand dict by code identity."""
    code = card_to_code(card)
    bucket = hand[card.suit]
    for i, c in enumerate(bucket):
        if card_to_code(c) == code:
            del bucket[i]
            return
    raise KeyError(f"{code} not in hand")


def _order_from(leader: str, folger: dict) -> list:
    """The 4 positions in play order starting at `leader`."""
    order = [leader]
    p = folger[leader]
    while p != leader:
        order.append(p)
        p = folger[p]
    return order


def rollout(state: EngineState, deal: dict, lead_card) -> int:
    """Play the spiel out from the current position with `lead_card` led by
    `state.me`; return state.me's TEAM points for the remainder.

    Every seat (including state.me's later plays) uses the heuristic
    ai_select_card policy. Reuses determine_trick_winner / trick_points so
    trick resolution matches the live game exactly.
    """
    operator, folger, me = state.operator, state.folger, state.me
    hands = {me: _clone_hand(state.my_hand)}
    for p in state.others:
        hands[p] = _clone_hand(deal[p])

    _remove_card(hands[me], lead_card)
    my_is_sn = me in SN_PLAYERS
    my_points = 0
    leader = me
    first_trick = True
    last_winner = me

    while any(any(h[s] for s in SUITS) for h in hands.values()):
        order = _order_from(leader, folger)
        trick = {}
        lead_suit = None
        for i, pos in enumerate(order):
            trick_so_far = [{"position": k, "card": card_to_code(v)}
                            for k, v in trick.items()]
            if first_trick and pos == me:
                card = lead_card           # forced, already removed
            else:
                card = ai_select_card(hands[pos], lead_suit, operator,
                                      trick_so_far=trick_so_far)
                _remove_card(hands[pos], card)
            if i == 0:
                lead_suit = card.suit
            trick[pos] = card
        first_trick = False
        winner = determine_trick_winner(trick, order[0], operator, folger)
        pts = trick_points(trick, operator)
        if (winner in SN_PLAYERS) == my_is_sn:
            my_points += pts
        last_winner = winner
        leader = winner

    # Last-trick bonus (+5, scaled by mode multiplier) goes to the final winner.
    if (last_winner in SN_PLAYERS) == my_is_sn:
        my_points += 5 * _mode_multiplier(operator)
    return my_points
