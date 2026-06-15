# Hard-AI PIMC Trump-Draw Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Hard AI's heuristic *leading* decision in trump modes with a Perfect-Information Monte Carlo (PIMC) engine that leads the card with the best expected team score, sampled over feasible deals and rolled out to spiel end.

**Architecture:** A standalone, stateless engine module `ausbau/ai_pimc.py` (deal sampler + rollout evaluator + EV driver) consumes a plain `EngineState` struct. `HardStrategy` grows generalized per-spiel tracking (per-player hand sizes, all-suit voids, trump Under-holdback), builds the struct, and calls the engine when leading in a trump mode — falling back to today's heuristic (which keeps the Tier-1 sound rule) when the engine is disabled or times out.

**Tech Stack:** Python 3.9+, stdlib only (`dataclasses`, `random`, `time`). Tests in `pytest`. Reuses `ausbau/game_session.py` helpers (`get_valid_cards`, `ai_select_card`, `determine_trick_winner`, `trick_points`, `card_to_code`, `code_to_card`) and `Cards_refactored` (`SUITS`, `Under`, `create_card`).

**Spec:** `docs/superpowers/specs/2026-06-15-schieber-ai-pimc-design.md`

---

## File Structure

- **Create `ausbau/ai_pimc.py`** — `EngineState` dataclass, `SamplingError`, `DealSampler`, `rollout`, `pimc_choose_lead`, and tuning constants. One responsibility: choose a lead by PIMC given an `EngineState`. No knowledge of `HardStrategy`.
- **Create `tests/multiplayer/test_ai_pimc.py`** — unit tests for the engine in isolation (seeded, deterministic).
- **Modify `ausbau/ai_strategies.py`** — generalize `HardStrategy` tracking, add `_rng` / `_pimc_enabled`, `_build_engine_state`, and refactor `_lead` (rename body to `_lead_heuristic`, add PIMC branch).
- **Modify `tests/multiplayer/test_ai_hard_trump_draw.py`** — disable PIMC in the `_make` fixture so the existing tests target the retained heuristic fallback.
- **Modify `CLAUDE.md`** — HardStrategy bullet: PIMC supersedes the heuristic lead in trump modes; Tier-1 retained as fallback. (Not a game-rules change; `schieber-game-rules` untouched.)

Position constants already exist in `ausbau/game_session.py`: `PLAYERS = ['comps', 'compo', 'compn', 'compe']`, `SN_PLAYERS = {'comps', 'compn'}`, `OW_PLAYERS = {'compo', 'compe'}`.

---

## Task 1: Engine module skeleton + `EngineState`

**Files:**
- Create: `ausbau/ai_pimc.py`
- Test: `tests/multiplayer/test_ai_pimc.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/multiplayer/test_ai_pimc.py
"""PIMC engine (ausbau/ai_pimc.py) unit tests — seeded and deterministic."""
import random
import pytest

from Cards_refactored import SUITS, create_card, Under
from ausbau.game_session import RANK_SUFFIX, card_to_code, PLAYERS
from ausbau import ai_pimc

_INVERSE_RANK = {v: k for k, v in RANK_SUFFIX.items()}


def _hand(suit_to_suffixes):
    """Build a {suit: [Card,...]} hand dict from {suit: 'AKO...'} suffixes."""
    h = {s: [] for s in SUITS}
    for suit, suffixes in suit_to_suffixes.items():
        for suf in suffixes:
            h[suit].append(create_card(_INVERSE_RANK[suf], suit))
    return h


def test_engine_state_holds_fields():
    state = ai_pimc.EngineState(
        me="comps",
        operator="Schellen",
        partner={"comps": "compn", "compn": "comps", "compo": "compe", "compe": "compo"},
        folger={"comps": "compo", "compo": "compn", "compn": "compe", "compe": "comps"},
        my_hand=_hand({"Schellen": "AK"}),
        others=["compo", "compn", "compe"],
        hand_sizes={"compo": 1, "compn": 1, "compe": 1},
        voids={"compo": set(), "compn": set(), "compe": set()},
        no_trump_except_under=set(),
        unseen=[create_card(_INVERSE_RANK["O"], "Schellen")],
    )
    assert state.me == "comps"
    assert state.operator == "Schellen"
    assert state.others == ["compo", "compn", "compe"]
    assert len(state.unseen) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py::test_engine_state_holds_fields -v`
Expected: FAIL with `ModuleNotFoundError` / `AttributeError: module 'ausbau.ai_pimc' has no attribute 'EngineState'`.

- [ ] **Step 3: Write minimal implementation**

```python
# ausbau/ai_pimc.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py::test_engine_state_holds_fields -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ausbau/ai_pimc.py tests/multiplayer/test_ai_pimc.py
git commit -m "feat(pimc): add EngineState and engine module skeleton

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: `DealSampler` — constrained deal sampling

Samples the 3 hidden hands honoring per-suit voids, hand-size capacities, and the trump Under-holdback (a player who discarded on a trump lead may hold the lone trump Under but no other trump). Most-constrained-card-first ordering plus restart keeps it fast and dead-end-free.

**Files:**
- Modify: `ausbau/ai_pimc.py`
- Test: `tests/multiplayer/test_ai_pimc.py`

- [ ] **Step 1: Write the failing tests**

```python
def _basic_state(my_hand, others, hand_sizes, voids=None,
                 no_trump_except_under=None, unseen=None,
                 operator="Schellen", me="comps"):
    partner = {"comps": "compn", "compn": "comps", "compo": "compe", "compe": "compo"}
    folger = {"comps": "compo", "compo": "compn", "compn": "compe", "compe": "comps"}
    return ai_pimc.EngineState(
        me=me, operator=operator, partner=partner, folger=folger,
        my_hand=my_hand, others=others, hand_sizes=hand_sizes,
        voids=voids or {p: set() for p in others},
        no_trump_except_under=no_trump_except_under or set(),
        unseen=unseen or [],
    )


def test_sampler_respects_capacities_and_partitions_unseen():
    # 2 unseen Schellen cards, two others each needing exactly 1 card.
    unseen = [create_card(_INVERSE_RANK["O"], "Schellen"),
              create_card(_INVERSE_RANK["U"], "Schellen")]
    state = _basic_state(
        my_hand=_hand({"Schellen": "AK"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        unseen=unseen,
    )
    sampler = ai_pimc.DealSampler(state)
    rng = random.Random(0)
    deal = sampler.sample(rng)
    # Each other gets exactly its capacity; all unseen placed exactly once.
    assert sum(len(cs) for h in deal.values() for cs in h.values()) == 2
    assert sum(len(cs) for cs in deal["compo"].values()) == 1
    assert sum(len(cs) for cs in deal["compe"].values()) == 1
    placed = {card_to_code(c) for h in deal.values() for cs in h.values() for c in cs}
    assert placed == {"SEO", "SEU"}


def test_sampler_respects_voids():
    unseen = [create_card(_INVERSE_RANK["6"], "Rosen"),
              create_card(_INVERSE_RANK["7"], "Rosen")]
    state = _basic_state(
        my_hand=_hand({"Schellen": "A"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        voids={"compo": {"Rosen"}, "compe": set()},
        unseen=unseen,
        operator="Schellen",
    )
    sampler = ai_pimc.DealSampler(state)
    # compo is void in Rosen, but capacity forces 1 Rosen each -> infeasible.
    with pytest.raises(ai_pimc.SamplingError):
        for _ in range(50):
            sampler.sample(random.Random(_))  # try several seeds


def test_sampler_under_holdback_only_under_to_voided_player():
    # compo discarded on a trump lead -> may hold ONLY the trump Under.
    under = create_card(_INVERSE_RANK["U"], "Schellen")   # SEU, the Under
    nine = create_card(_INVERSE_RANK["9"], "Schellen")    # SE9, not an Under
    state = _basic_state(
        my_hand=_hand({"Eicheln": "A"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        no_trump_except_under={"compo"},
        unseen=[under, nine],
        operator="Schellen",
    )
    sampler = ai_pimc.DealSampler(state)
    seen_under_with_compo = False
    for s in range(40):
        deal = sampler.sample(random.Random(s))
        compo_codes = {card_to_code(c) for cs in deal["compo"].values() for c in cs}
        # compo must never hold SE9 (a non-Under trump).
        assert "SE9" not in compo_codes
        if "SEU" in compo_codes:
            seen_under_with_compo = True
    assert seen_under_with_compo  # the Under CAN land with compo


def test_sampler_is_deterministic_under_seed():
    unseen = [create_card(_INVERSE_RANK["O"], "Schellen"),
              create_card(_INVERSE_RANK["U"], "Schellen")]
    state = _basic_state(
        my_hand=_hand({"Schellen": "AK"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        unseen=unseen,
    )
    sampler = ai_pimc.DealSampler(state)
    d1 = sampler.sample(random.Random(123))
    d2 = sampler.sample(random.Random(123))
    norm = lambda d: {p: sorted(card_to_code(c) for cs in h.values() for c in cs)
                      for p, h in d.items()}
    assert norm(d1) == norm(d2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k sampler -v`
Expected: FAIL with `AttributeError: module 'ausbau.ai_pimc' has no attribute 'DealSampler'`.

- [ ] **Step 3: Write minimal implementation**

Add to `ausbau/ai_pimc.py`:

```python
from Cards_refactored import SUITS, Under


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k sampler -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add ausbau/ai_pimc.py tests/multiplayer/test_ai_pimc.py
git commit -m "feat(pimc): add DealSampler with void/capacity/Under-holdback constraints

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: `rollout` — simulate the spiel to the end

Plays a sampled full deal to completion from the current position with a forced AI lead, using `ai_select_card` as the playout policy for every seat. Returns the AI team's points (trick points + last-trick bonus) for the remainder. Reuses the real trick-resolution helpers so it can't diverge from game rules.

**Files:**
- Modify: `ausbau/ai_pimc.py`
- Test: `tests/multiplayer/test_ai_pimc.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_rollout_is_deterministic():
    # 2-card endgame: I lead, everyone has 2 cards. Schellen trump.
    my_hand = _hand({"Schellen": "A", "Eicheln": "6"})  # SEA (boss), E6
    others = ["compo", "compn", "compe"]
    deal = {
        "compo": _hand({"Schellen": "9", "Rosen": "6"}),
        "compn": _hand({"Eicheln": "A", "Rosen": "7"}),   # partner
        "compe": _hand({"Schellen": "U", "Eicheln": "7"}),
    }
    state = _basic_state(
        my_hand=my_hand, others=others,
        hand_sizes={p: 2 for p in others},
        unseen=[c for h in deal.values() for cs in h.values() for c in cs],
        operator="Schellen", me="comps",
    )
    lead = create_card(_INVERSE_RANK["A"], "Schellen")    # lead SEA
    s1 = ai_pimc.rollout(state, deal, lead)
    s2 = ai_pimc.rollout(state, deal, lead)
    assert s1 == s2
    assert isinstance(s1, int)


def test_rollout_points_are_bounded_and_nonnegative():
    my_hand = _hand({"Schellen": "A", "Eicheln": "6"})
    others = ["compo", "compn", "compe"]
    deal = {
        "compo": _hand({"Schellen": "9", "Rosen": "6"}),
        "compn": _hand({"Eicheln": "A", "Rosen": "7"}),
        "compe": _hand({"Schellen": "U", "Eicheln": "7"}),
    }
    state = _basic_state(
        my_hand=my_hand, others=others,
        hand_sizes={p: 2 for p in others},
        unseen=[c for h in deal.values() for cs in h.values() for c in cs],
        operator="Schellen", me="comps",
    )
    lead = create_card(_INVERSE_RANK["A"], "Schellen")
    pts = ai_pimc.rollout(state, deal, lead)
    assert 0 <= pts <= 300   # sanity: never negative, never absurd
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k rollout -v`
Expected: FAIL with `AttributeError: module 'ausbau.ai_pimc' has no attribute 'rollout'`.

- [ ] **Step 3: Write minimal implementation**

Add to `ausbau/ai_pimc.py`:

```python
from ausbau.game_session import (
    SN_PLAYERS, ai_select_card, determine_trick_winner, trick_points,
    card_to_code, _mode_multiplier,
)


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k rollout -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add ausbau/ai_pimc.py tests/multiplayer/test_ai_pimc.py
git commit -m "feat(pimc): add rollout playout to spiel end

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: `pimc_choose_lead` — EV driver with time-box + fallback

Averages rollout scores per candidate lead across sampled deals, time-boxed; returns the max-EV card, or `None` when fewer than `min_samples` complete (signalling the caller to use the heuristic).

**Files:**
- Modify: `ausbau/ai_pimc.py`
- Test: `tests/multiplayer/test_ai_pimc.py`

- [ ] **Step 1: Write the failing tests**

```python
def _endgame_state():
    """I hold the boss trump (SEA) and a losing side card (E6). One trump
    (SE9) is outstanding with an OPPONENT (compo), who is void in Eicheln so
    they would ruff an Eicheln lead. Leading the boss trump should score
    better in EV than leading E6 into the ruff."""
    my_hand = _hand({"Schellen": "A", "Eicheln": "6"})   # SEA boss, E6
    others = ["compo", "compn", "compe"]
    state = _basic_state(
        my_hand=my_hand, others=others,
        hand_sizes={"compo": 2, "compn": 2, "compe": 2},
        voids={"compo": {"Eicheln"}, "compn": set(), "compe": set()},
        unseen=[
            create_card(_INVERSE_RANK["9"], "Schellen"),   # SE9 (opp trump)
            create_card(_INVERSE_RANK["6"], "Rosen"),
            create_card(_INVERSE_RANK["A"], "Eicheln"),
            create_card(_INVERSE_RANK["7"], "Rosen"),
            create_card(_INVERSE_RANK["K"], "Eicheln"),
            create_card(_INVERSE_RANK["7"], "Eicheln"),
        ],
        operator="Schellen", me="comps",
    )
    return state


def test_pimc_prefers_boss_trump_over_ruffable_side_lead():
    state = _endgame_state()
    leads = state.my_hand["Schellen"] + state.my_hand["Eicheln"]  # [SEA, E6]
    rng = random.Random(7)
    pick = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=5.0, rng=rng, min_samples=5, n=60)
    assert pick is not None
    assert card_to_code(pick) == "SEA"   # lead the boss trump, not E6


def test_pimc_returns_none_when_below_min_samples():
    state = _endgame_state()
    leads = state.my_hand["Schellen"] + state.my_hand["Eicheln"]
    # deadline_s=0 -> no samples complete -> fallback signal.
    pick = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=0.0, rng=random.Random(1), min_samples=5, n=60)
    assert pick is None


def test_pimc_is_deterministic_under_seed():
    state = _endgame_state()
    leads = state.my_hand["Schellen"] + state.my_hand["Eicheln"]
    p1 = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=5.0, rng=random.Random(42), min_samples=5, n=40)
    p2 = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=5.0, rng=random.Random(42), min_samples=5, n=40)
    assert card_to_code(p1) == card_to_code(p2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k pimc -v`
Expected: FAIL with `AttributeError: module 'ausbau.ai_pimc' has no attribute 'pimc_choose_lead'`.

- [ ] **Step 3: Write minimal implementation**

Add to `ausbau/ai_pimc.py`:

```python
import time


def pimc_choose_lead(state: EngineState, candidate_leads, *,
                     deadline_s: float = PIMC_DEADLINE_S,
                     rng=None,
                     min_samples: int = PIMC_MIN_SAMPLES,
                     n: int = PIMC_N) -> Optional[object]:
    """Return the max-EV lead Card from `candidate_leads`, or None when fewer
    than `min_samples` deals complete within the time-box (caller should then
    fall back to the heuristic lead)."""
    import random as _random
    if rng is None:
        rng = _random.Random()
    if not candidate_leads:
        return None

    sampler = DealSampler(state)
    totals = {card_to_code(c): 0.0 for c in candidate_leads}
    completed = 0
    start = time.monotonic()

    for _ in range(n):
        if time.monotonic() - start > deadline_s:
            break
        try:
            deal = sampler.sample(rng)
        except SamplingError:
            continue
        for c in candidate_leads:
            totals[card_to_code(c)] += rollout(state, deal, c)
        completed += 1

    if completed < min_samples:
        return None

    best_code = max(totals, key=lambda code: totals[code] / completed)
    for c in candidate_leads:
        if card_to_code(c) == best_code:
            return c
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k pimc -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Run the whole engine test file**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -v`
Expected: PASS (all engine tests)

- [ ] **Step 6: Commit**

```bash
git add ausbau/ai_pimc.py tests/multiplayer/test_ai_pimc.py
git commit -m "feat(pimc): add expected-value driver with time-box and fallback

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Generalize `HardStrategy` tracking

Add per-player hand sizes, all-suit void flags, and the trump Under-holdback marker, tracked for all three non-self positions (partner included). The existing trump-only `_opp_void_trump` / `_opp_shown_suits` stay (the heuristic fallback still uses them).

**Files:**
- Modify: `ausbau/ai_strategies.py` (`HardStrategy.__init__`, `on_spiel_start`, `on_card_played`)
- Test: `tests/multiplayer/test_ai_pimc.py`

Reference: current `on_spiel_start` is at `ausbau/ai_strategies.py:106-126`; `on_card_played` at `:128-181`; `__init__` at `:83-98`.

- [ ] **Step 1: Write the failing tests**

```python
# Append to tests/multiplayer/test_ai_pimc.py
from Cards_refactored import Play
from ausbau.ai_strategies import HardStrategy


def _make_strat(position, operator, my_suit_to_suffixes):
    play = Play(spiel=1)
    play.operator = operator
    hand = {s: [] for s in SUITS}
    for suit, sufs in my_suit_to_suffixes.items():
        for suf in sufs:
            hand[suit].append(create_card(_INVERSE_RANK[suf], suit))
    setattr(play, position, hand)
    strat = HardStrategy(position)
    strat.on_spiel_start(play)
    return play, strat


def test_tracking_initializes_sizes_and_voids():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "AK"})
    for p in ("compo", "compn", "compe"):
        assert strat._hand_sizes[p] == 9
        assert strat._voids_all[p] == set()
    assert strat._no_trump_except_under == set()


def test_tracking_decrements_sizes_for_all_others():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "AK"})
    strat.on_card_played("compo", "R6")
    strat.on_card_played("compn", "R7")
    assert strat._hand_sizes["compo"] == 8
    assert strat._hand_sizes["compn"] == 8
    assert strat._hand_sizes["compe"] == 9   # untouched


def test_tracking_marks_hard_void_on_nontrump_lead_discard():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "A"})
    # Rosen led; compe discards Eicheln -> compe void in Rosen.
    strat.on_card_played("compn", "R6")   # lead Rosen (partner)
    strat.on_card_played("compe", "E6")   # discard -> void in Rosen
    assert "Rosen" in strat._voids_all["compe"]
    assert "compe" not in strat._no_trump_except_under


def test_tracking_marks_under_holdback_on_trump_lead_discard():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "A"})
    # Schellen (trump) led; compo discards Rosen -> "no trump except Under".
    strat.on_card_played("comps", "SEA")  # trump led by us
    strat.on_card_played("compo", "R6")   # discard on trump lead
    assert "compo" in strat._no_trump_except_under
    # NOT recorded as a hard trump void (they may still hold the Under):
    assert "Schellen" not in strat._voids_all["compo"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k tracking -v`
Expected: FAIL with `AttributeError: 'HardStrategy' object has no attribute '_hand_sizes'`.

- [ ] **Step 3: Write the implementation**

In `ausbau/ai_strategies.py`, `HardStrategy.__init__` — add after the existing `_running_trick` init:

```python
        # ── PIMC tracking (sub-project D) ────────────────────────────────
        # Remaining hand size for each of the 3 non-self positions.
        self._hand_sizes: dict[str, int] = {}
        # Hard voids per non-self position, ALL suits (set on follow failure).
        self._voids_all: dict[str, set] = {}
        # Positions that discarded on a trump lead: "no trump except Under".
        self._no_trump_except_under: set = set()
        import random as _random
        self._rng = _random.Random()
        self._pimc_enabled = True
```

In `on_spiel_start`, after the existing `self._running_trick = []` line, add:

```python
        others = [p for p in ("comps", "compo", "compn", "compe")
                  if p != self.position]
        self._hand_sizes = {p: 9 for p in others}
        self._voids_all = {p: set() for p in others}
        self._no_trump_except_under = set()
```

In `on_card_played`, inside the `if player_position != self.position:` block (alongside the existing remaining/shown/void-trump updates), add the new tracking. Place it right after the existing `self._opp_shown_suits.setdefault(...)` line:

```python
            # PIMC tracking: decrement hand size for this non-self player.
            if player_position in self._hand_sizes:
                self._hand_sizes[player_position] -= 1
            # All-suit void + Under-holdback (house rule).
            if not is_lead and lead_suit_name is not None and suit != lead_suit_name:
                if lead_suit_name == self._operator:
                    # Discard on a trump lead: no trump EXCEPT possibly the Under.
                    self._no_trump_except_under.add(player_position)
                else:
                    # Discard on a non-trump lead: hard void in the led suit.
                    self._voids_all.setdefault(player_position, set()).add(lead_suit_name)
```

(The existing `is_lead` / `lead_suit_name` locals are computed earlier in the method — reuse them; do not recompute.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k tracking -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Run the full strategy suite (no regressions)**

Run: `python -m pytest tests/multiplayer/test_ai_strategies.py tests/multiplayer/test_ai_hard_trump_draw.py -q`
Expected: PASS (existing behavior unchanged — new state is additive)

- [ ] **Step 6: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_pimc.py
git commit -m "feat(pimc): generalize HardStrategy tracking (hand sizes, all-suit voids, Under-holdback)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: `HardStrategy._build_engine_state`

Adapts the strategy's tracking into an `EngineState`. Asserts the consistency invariant: total unseen cards == sum of the 3 others' hand sizes.

**Files:**
- Modify: `ausbau/ai_strategies.py` (new method on `HardStrategy`)
- Test: `tests/multiplayer/test_ai_pimc.py`

- [ ] **Step 1: Write the failing test**

```python
def test_build_engine_state_is_consistent():
    play, strat = _make_strat("comps", "Schellen", {"Schellen": "AK9", "Eicheln": "A"})
    # Simulate one trump-led trick so some tracking is populated.
    strat.on_card_played("comps", "SEA")
    strat.on_card_played("compo", "R6")   # discard on trump lead -> holdback
    strat.on_card_played("compn", "SEK")  # partner follows trump
    strat.on_card_played("compe", "E6")   # discard on trump lead -> holdback
    # Note: comps's SEA/SEK above are not in our real hand for this test; the
    # consistency check below uses remaining tracking vs hand sizes only.
    state = strat._build_engine_state(play)
    assert state.me == "comps"
    assert state.operator == "Schellen"
    assert set(state.others) == {"compo", "compn", "compe"}
    # Invariant: unseen card count equals sum of the 3 hidden hand sizes.
    assert len(state.unseen) == sum(state.hand_sizes[p] for p in state.others)
    assert "compo" in state.no_trump_except_under
    assert "compe" in state.no_trump_except_under
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k build_engine_state -v`
Expected: FAIL with `AttributeError: 'HardStrategy' object has no attribute '_build_engine_state'`.

- [ ] **Step 3: Write the implementation**

Add this method to `HardStrategy` in `ausbau/ai_strategies.py` (place it just above `_lead`):

```python
    def _build_engine_state(self, play):
        """Adapt current tracking into an ai_pimc.EngineState."""
        from ausbau.ai_pimc import EngineState
        from ausbau.game_session import code_to_card
        from Cards_refactored import SUITS

        me = self.position
        others = [p for p in ("comps", "compo", "compn", "compe") if p != me]
        unseen = [code_to_card(code)
                  for suit in SUITS
                  for code in self._remaining_by_suit.get(suit, set())]
        return EngineState(
            me=me,
            operator=play.operator,
            partner=play.partner,
            folger=play.folger,
            my_hand=getattr(play, me),
            others=others,
            hand_sizes={p: self._hand_sizes[p] for p in others},
            voids={p: set(self._voids_all.get(p, set())) for p in others},
            no_trump_except_under=set(self._no_trump_except_under),
            unseen=unseen,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k build_engine_state -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_pimc.py
git commit -m "feat(pimc): add HardStrategy._build_engine_state adapter

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7: Wire PIMC into `HardStrategy._lead`

Rename the current rule A/B body to `_lead_heuristic` and add the PIMC branch in `_lead` (trump modes only, leading). Any engine error or a `None` return falls back to the heuristic — which keeps the Tier-1 sound rule.

**Files:**
- Modify: `ausbau/ai_strategies.py` (`_lead`)
- Test: `tests/multiplayer/test_ai_pimc.py`

Reference: current `_lead` spans `ausbau/ai_strategies.py:261-379`. The non-trump early-return (`if operator not in SUITS: return self._lead_legacy(...)`) must stay at the top of the NEW `_lead`, NOT inside `_lead_heuristic`.

- [ ] **Step 1: Write the failing tests**

```python
def test_lead_uses_pimc_when_enabled(monkeypatch):
    play, strat = _make_strat("comps", "Schellen", {"Schellen": "A", "Eicheln": "6"})
    strat._pimc_enabled = True
    sentinel = create_card(_INVERSE_RANK["A"], "Schellen")  # SEA

    called = {}
    def fake_choose(state, leads, **kw):
        called["yes"] = True
        return sentinel
    monkeypatch.setattr("ausbau.ai_pimc.pimc_choose_lead", fake_choose)

    valid = play.comps["Schellen"] + play.comps["Eicheln"]
    result = strat._lead(play, valid)
    assert called.get("yes") is True
    assert result == {"type": "play_card", "card": "SEA"}


def test_lead_falls_back_to_heuristic_when_pimc_disabled():
    play, strat = _make_strat("comps", "Schellen", {"Schellen": "AK9"})
    strat._pimc_enabled = False
    valid = play.comps["Schellen"]
    result = strat._lead(play, valid)
    # Heuristic rule A draws the highest trump (SEA) with trumps outstanding.
    assert result["type"] == "play_card"
    assert result["card"] == "SEA"


def test_lead_falls_back_when_pimc_returns_none(monkeypatch):
    play, strat = _make_strat("comps", "Schellen", {"Schellen": "AK9"})
    strat._pimc_enabled = True
    monkeypatch.setattr("ausbau.ai_pimc.pimc_choose_lead",
                        lambda state, leads, **kw: None)
    valid = play.comps["Schellen"]
    result = strat._lead(play, valid)
    assert result["card"] == "SEA"   # heuristic fallback fired
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k "lead_uses_pimc or lead_falls_back" -v`
Expected: FAIL (`_lead` still runs the heuristic directly; `_pimc_enabled` not consulted / `pimc_choose_lead` not called).

- [ ] **Step 3: Write the implementation**

In `ausbau/ai_strategies.py`, rename the existing method `def _lead(self, play, valid_cards) -> dict:` to `def _lead_heuristic(self, play, valid_cards) -> dict:`, and **remove** its leading non-trump early-return block

```python
        # Non-trump modes: today's behaviour unchanged.
        if operator not in SUITS:
            return self._lead_legacy(play, valid_cards)
```

from `_lead_heuristic` (that check moves to the new `_lead`). Keep the rest of the body (rule A / rule B, including the Tier-1 lone-trump lack-boss clause) unchanged. Then add the new dispatcher immediately above `_lead_heuristic`:

```python
    def _lead(self, play, valid_cards) -> dict:
        """Leading dispatcher. Trump modes: try PIMC (sub-project D), fall back
        to the heuristic (which retains the Tier-1 sound stop). No-trump modes
        keep the legacy behaviour."""
        from Cards_refactored import SUITS
        from ausbau.game_session import card_to_code

        operator = play.operator
        if operator not in SUITS:
            return self._lead_legacy(play, valid_cards)

        if self._pimc_enabled and valid_cards:
            try:
                import ausbau.ai_pimc as ai_pimc
                state = self._build_engine_state(play)
                pick = ai_pimc.pimc_choose_lead(
                    state, valid_cards, rng=self._rng)
            except Exception:
                pick = None
            if pick is not None:
                return {"type": "play_card", "card": card_to_code(pick)}

        return self._lead_heuristic(play, valid_cards)
```

(Importing `ai_pimc` as a module inside the method, and patching `ausbau.ai_pimc.pimc_choose_lead`, lets the monkeypatch tests above intercept the call.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -k "lead_uses_pimc or lead_falls_back" -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Run the full engine + strategy suites**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py -v`
Expected: PASS (all)

- [ ] **Step 6: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_pimc.py
git commit -m "feat(pimc): wire PIMC into HardStrategy._lead with heuristic fallback

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 8: Keep existing trump-draw tests on the heuristic path + docs

The existing `test_ai_hard_trump_draw.py` tests assert heuristic rule A/B behavior. With PIMC default-on, they would now exercise the engine and become non-deterministic. Pin them to the retained heuristic by disabling PIMC in their fixture.

**Files:**
- Modify: `tests/multiplayer/test_ai_hard_trump_draw.py` (`_make` helper)
- Modify: `CLAUDE.md` (HardStrategy bullet)

- [ ] **Step 1: Disable PIMC in the existing fixture**

In `tests/multiplayer/test_ai_hard_trump_draw.py`, in `_make`, set the flag right after constructing the strategy (current `_make` is at lines 41-47):

```python
def _make(position, operator, suit_to_suffixes):
    play = Play(spiel=1)
    play.operator = operator
    _set_hand(play, position, suit_to_suffixes)
    strat = HardStrategy(position)
    strat._pimc_enabled = False   # these tests target the heuristic fallback
    strat.on_spiel_start(play)
    return play, strat
```

- [ ] **Step 2: Run the existing trump-draw suite to confirm it stays green**

Run: `python -m pytest tests/multiplayer/test_ai_hard_trump_draw.py -q`
Expected: PASS (all 22 — heuristic behavior unchanged because PIMC is off)

- [ ] **Step 3: Update the module docstring note**

In `tests/multiplayer/test_ai_hard_trump_draw.py`, append to the module docstring (after the existing "Following-suit behaviour..." paragraph):

```
These tests pin ``HardStrategy._pimc_enabled = False`` (via ``_make``) so they
exercise the retained heuristic leading path. The PIMC engine (sub-project D)
is covered separately in ``tests/multiplayer/test_ai_pimc.py``.
```

- [ ] **Step 4: Update CLAUDE.md**

In `CLAUDE.md`, in the **Sub-project C — AI difficulty** bullet's HardStrategy description, append a sentence at the end of that bullet:

```
**Sub-project D (PIMC):** in trump modes the Hard AI now chooses its LEAD via
a Perfect-Information Monte Carlo engine (`ausbau/ai_pimc.py`): it samples
deals consistent with tracked hand sizes / all-suit voids / trump
Under-holdback, rolls each out to spiel end with the `ai_select_card` heuristic
policy, and leads the highest expected-value card. Synchronous and time-boxed
(`PIMC_DEADLINE_S`); on timeout/too-few-samples it falls back to the heuristic
`_lead_heuristic`, which retains the Tier-1 lone-trump lack-boss stop. Gated by
`HardStrategy._pimc_enabled` (default on). Tests in
`tests/multiplayer/test_ai_pimc.py`. Not a game-rules change.
```

- [ ] **Step 5: Run the full test suite**

Run: `python run_tests.py`
Expected: PASS (all; engine suite added, existing suites unchanged)

- [ ] **Step 6: Commit**

```bash
git add tests/multiplayer/test_ai_hard_trump_draw.py CLAUDE.md
git commit -m "test/docs(pimc): pin trump-draw tests to heuristic path; document sub-project D

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 9: End-to-end smoke — PIMC active in a real leading decision

Confirms the full path works against a real `Play` and `pick_card` (not monkeypatched), with PIMC on, and produces a legal lead within the time budget.

**Files:**
- Test: `tests/multiplayer/test_ai_pimc.py`

- [ ] **Step 1: Write the test**

```python
def test_pick_card_leading_with_pimc_returns_legal_card():
    play, strat = _make_strat(
        "comps", "Schellen",
        {"Schellen": "AK", "Eicheln": "A6", "Rosen": "6"})
    strat._pimc_enabled = True
    strat._rng = random.Random(0)
    # Leading (lead_suit=None), empty trick.
    result = strat.pick_card(play, None, [])
    assert result["type"] == "play_card"
    legal = set(card_to_code(c) for s in SUITS for c in play.comps[s])
    assert result["card"] in legal
```

- [ ] **Step 2: Run the test**

Run: `python -m pytest tests/multiplayer/test_ai_pimc.py::test_pick_card_leading_with_pimc_returns_legal_card -v`
Expected: PASS (a legal lead is returned via the live PIMC path)

- [ ] **Step 3: Run the full multiplayer + AI suites once more**

Run: `python -m pytest tests/multiplayer/ -q`
Expected: PASS (all)

- [ ] **Step 4: Commit**

```bash
git add tests/multiplayer/test_ai_pimc.py
git commit -m "test(pimc): end-to-end smoke for live PIMC leading path

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review notes (carried out while writing)

- **Spec coverage:** §3 module layout → Tasks 1–4; §4.1 generalized tracking → Task 5; §4.1 EngineState assembly → Task 6; §5 integration + Tier-1 fallback → Tasks 7–8; §6 time-box constants → Task 1/4; §7 testing (sampler, rollout, decisions, fallback, regression) → Tasks 2,3,4,7,8,9. §8 limitations are accepted, not implemented. All covered.
- **Type consistency:** `EngineState` field names are identical across Tasks 1, 6 (`me`, `operator`, `partner`, `folger`, `my_hand`, `others`, `hand_sizes`, `voids`, `no_trump_except_under`, `unseen`). `pimc_choose_lead` keyword args (`deadline_s`, `rng`, `min_samples`, `n`) match between Task 4 definition and Task 7 call (Task 7 passes only `rng`, relying on the constant defaults). `_pimc_enabled` / `_rng` / `_hand_sizes` / `_voids_all` / `_no_trump_except_under` / `_build_engine_state` / `_lead_heuristic` names are consistent across Tasks 5–9.
- **No placeholders:** every code step has complete code; every run step has the exact command and expected result.
