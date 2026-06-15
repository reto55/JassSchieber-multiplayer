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
