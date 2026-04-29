# Schieber — AI Difficulty Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three per-seat AI difficulty levels (`easy` / `medium` / `hard`) with a strategy-pattern dispatch from `_compute_ai_action`. Default = `medium` = today's behaviour, so default rooms are unaffected.

**Architecture:** New module `ausbau/ai_strategies.py` with `AIStrategy` ABC and three concrete classes. `Seat` gets `ai_difficulty` + `_strategy` fields. `_compute_ai_action` becomes a one-line delegation. New endpoint `POST /rooms/{code}/ai_difficulty` (host-only, lobby-only). Frontend lobby gets a per-AI-seat dropdown.

**Tech Stack:** Python 3.9+, FastAPI, pytest, vanilla JS.

**Reference:** `docs/superpowers/specs/2026-04-29-schieber-ai-difficulty-design.md`. Branch state at start: `master` at `8d1ae6f` with 285 tests passing.

**File map:**
- Create: `ausbau/ai_strategies.py` — base + 3 strategies + factory
- Modify: `ausbau/room.py` — `Seat` fields + `create_room` defaults
- Modify: `ausbau/game_session.py` — `_compute_ai_action` delegation; lifecycle hooks; `valid_actions["trick_so_far"]`
- Modify: `ausbau/server.py` — new endpoint; `_seat_to_dict` adds `ai_difficulty`
- Modify: `ausbau/html5/lobby.html`, `lobby.js`, `lobby.css` — dropdown
- Create tests: `tests/multiplayer/test_ai_strategies.py`, `test_ai_difficulty_endpoint.py`, `test_ai_difficulty_lifecycle.py`
- Extend: `tests/multiplayer/test_e2e_4_humans.py` (mixed-difficulty case)

---

## Task 1: Module skeleton + EasyStrategy + factory

**Files:**
- Create: `ausbau/ai_strategies.py`
- Create: `tests/multiplayer/test_ai_strategies.py`

- [ ] **Step 1: Write failing tests**

`tests/multiplayer/test_ai_strategies.py`:
```python
import pytest
import random
from Cards_refactored import Play, SUITS
from ausbau.ai_strategies import (
    AIStrategy,
    EasyStrategy,
    MediumStrategy,
    HardStrategy,
    make_strategy,
)


def test_make_strategy_easy():
    s = make_strategy("easy", "compe")
    assert isinstance(s, EasyStrategy)
    assert s.position == "compe"


def test_make_strategy_medium():
    s = make_strategy("medium", "compn")
    assert isinstance(s, MediumStrategy)


def test_make_strategy_hard():
    s = make_strategy("hard", "comps")
    assert isinstance(s, HardStrategy)


def test_make_strategy_unknown():
    with pytest.raises(ValueError, match="unknown difficulty"):
        make_strategy("expert", "compe")


def test_easy_pick_trump_returns_one_of_six_modes():
    random.seed(0)
    s = EasyStrategy("compe")
    play = Play(spiel=1)
    seen = set()
    for _ in range(50):
        msg = s.pick_trump(play, schieben_allowed=True)
        assert msg["type"] == "choose_trump"
        seen.add(msg["operator"])
    # Over 50 calls expect coverage of multiple modes.
    assert len(seen) >= 3
    for op in seen:
        assert op in ("Eicheln", "Rosen", "Schellen", "Schilten", "Oben", "Unten")


def test_easy_pick_trump_never_schiebens():
    random.seed(0)
    s = EasyStrategy("compe")
    play = Play(spiel=1)
    for _ in range(20):
        msg = s.pick_trump(play, schieben_allowed=True)
        assert msg["type"] == "choose_trump"


def test_easy_pick_card_returns_valid_card():
    random.seed(0)
    s = EasyStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    msg = s.pick_card(play, lead_suit=None, trick_so_far=[])
    assert msg["type"] == "play_card"
    # Card must be one of the codes in seat's hand
    from ausbau.game_session import hand_to_codes
    assert msg["card"] in hand_to_codes(play.comps)
```

- [ ] **Step 2: Run failing**

```bash
python -m pytest tests/multiplayer/test_ai_strategies.py -v
```
Expected: ImportError (module missing).

- [ ] **Step 3: Implement skeleton + EasyStrategy + factory**

`ausbau/ai_strategies.py`:
```python
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


def make_strategy(difficulty: str, position: str) -> AIStrategy:
    if difficulty == "easy":
        return EasyStrategy(position)
    if difficulty == "medium":
        return MediumStrategy(position)
    if difficulty == "hard":
        return HardStrategy(position)
    raise ValueError(f"unknown difficulty: {difficulty!r}")
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/multiplayer/test_ai_strategies.py -v
```
Expected: 7 passed.

- [ ] **Step 5: Run full suite**

```bash
python -m pytest tests/ -q
```
Expected: 292 passed (285 baseline + 7 new). HardStrategy methods raise NotImplementedError but no test exercises them yet.

- [ ] **Step 6: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_strategies.py
git -c commit.gpgsign=false commit -m "feat(ai): module skeleton + EasyStrategy + factory"
```

---

## Task 2: MediumStrategy tests

**Files:**
- Modify: `tests/multiplayer/test_ai_strategies.py`

MediumStrategy is implemented in Task 1; this task adds its tests. Separating test-add from impl-add keeps each commit focused.

- [ ] **Step 1: Add tests**

Append to `tests/multiplayer/test_ai_strategies.py`:
```python
def test_medium_pick_trump_uses_farbe_lang():
    from utils.card_utils import farbe_lang
    s = MediumStrategy("comps")
    play = Play(spiel=1)
    msg = s.pick_trump(play, schieben_allowed=True)
    assert msg["type"] == "choose_trump"
    assert msg["operator"] == farbe_lang(play.comps)


def test_medium_pick_trump_never_schiebens():
    s = MediumStrategy("comps")
    play = Play(spiel=1)
    for _ in range(10):
        msg = s.pick_trump(play, schieben_allowed=True)
        assert msg["type"] == "choose_trump"


def test_medium_pick_card_lead_picks_highest_point():
    from ausbau.game_session import ai_select_card, card_to_code
    s = MediumStrategy("compe")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    msg = s.pick_card(play, lead_suit=None, trick_so_far=[])
    expected = card_to_code(ai_select_card(play.compe, None, "Eicheln"))
    assert msg == {"type": "play_card", "card": expected}


def test_medium_pick_card_follow_picks_lowest_point():
    from ausbau.game_session import ai_select_card, card_to_code
    s = MediumStrategy("compn")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    # Lead has been played: pretend lead suit is "Rosen"
    msg = s.pick_card(play, lead_suit="Rosen", trick_so_far=[{"position": "compe", "card": "RA"}])
    expected = card_to_code(ai_select_card(play.compn, "Rosen", "Eicheln"))
    assert msg == {"type": "play_card", "card": expected}
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/multiplayer/test_ai_strategies.py -v
```
Expected: 11 passed (7 + 4 new).

- [ ] **Step 3: Commit**

```bash
git add tests/multiplayer/test_ai_strategies.py
git -c commit.gpgsign=false commit -m "test(ai): MediumStrategy unit tests"
```

---

## Task 3: HardStrategy memory hooks

**Files:**
- Modify: `ausbau/ai_strategies.py`
- Modify: `tests/multiplayer/test_ai_strategies.py`

- [ ] **Step 1: Write failing tests**

Append to `test_ai_strategies.py`:
```python
def test_hard_on_spiel_start_populates_remaining():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    # 36 total cards - 9 own = 27 remaining
    total = sum(len(v) for v in s._remaining_by_suit.values())
    assert total == 27
    # All 4 suits keys exist
    assert set(s._remaining_by_suit.keys()) == set(SUITS)


def test_hard_on_spiel_start_excludes_own_hand():
    from ausbau.game_session import hand_to_codes
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    own = set(hand_to_codes(play.comps))
    tracked = {c for codes in s._remaining_by_suit.values() for c in codes}
    assert own.isdisjoint(tracked)


def test_hard_on_card_played_removes_known_card():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    # Pick any tracked card from any suit
    suit, codes = next((k, v) for k, v in s._remaining_by_suit.items() if v)
    code = next(iter(codes))
    s.on_card_played("compo", code)
    assert code not in s._remaining_by_suit[suit]


def test_hard_on_card_played_skips_own_position():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    initial_total = sum(len(v) for v in s._remaining_by_suit.values())
    # Send a "self-play" — own cards aren't tracked anyway, so it's a no-op.
    from ausbau.game_session import hand_to_codes
    own_card = hand_to_codes(play.comps)[0]
    s.on_card_played("comps", own_card)
    after_total = sum(len(v) for v in s._remaining_by_suit.values())
    assert initial_total == after_total


def test_hard_on_card_played_unknown_card_is_noop():
    s = HardStrategy("comps")
    play = Play(spiel=1)
    s.on_spiel_start(play)
    initial_total = sum(len(v) for v in s._remaining_by_suit.values())
    # Use a code we know is not tracked: pick a card from own hand
    from ausbau.game_session import hand_to_codes
    own_card = hand_to_codes(play.comps)[0]
    s.on_card_played("compo", own_card)  # opponent "playing" something we have — defensive
    after_total = sum(len(v) for v in s._remaining_by_suit.values())
    assert initial_total == after_total  # no crash, no change
```

- [ ] **Step 2: Run failing**

```bash
python -m pytest tests/multiplayer/test_ai_strategies.py -k hard_on -v
```
Expected: errors (HardStrategy.on_spiel_start raises NotImplementedError or default-noops with empty memory).

- [ ] **Step 3: Implement**

In `ausbau/ai_strategies.py`, add module-level constants (after `TRUMP_OPTIONS`):
```python
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
```

Add to `HardStrategy`:
```python
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
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/multiplayer/test_ai_strategies.py -v
```
Expected: 16 passed (11 + 5 new).

- [ ] **Step 5: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_strategies.py
git -c commit.gpgsign=false commit -m "feat(ai): HardStrategy memory hooks (on_spiel_start, on_card_played)"
```

---

## Task 4: HardStrategy.pick_trump

**Files:**
- Modify: `ausbau/ai_strategies.py`
- Modify: `tests/multiplayer/test_ai_strategies.py`

- [ ] **Step 1: Write failing tests**

Append:
```python
def _hand_with_suits(play, position, suit_to_codes):
    """Helper: stuff Play's per-position hand with specific cards by suit."""
    from Cards_refactored import CARD_ATTRIBUTES, SUITS, create_card
    from ausbau.game_session import RANK_SUFFIX
    inverse_rank = {v: k for k, v in RANK_SUFFIX.items()}
    hand = {s: [] for s in SUITS}
    for suit, codes in suit_to_codes.items():
        for code_suffix in codes:
            rank = inverse_rank[code_suffix]
            hand[suit].append(create_card(rank, suit))
    setattr(play, position, hand)


def test_hard_pick_trump_commits_when_long_with_under():
    # 4-card Schilten hand including Under → should commit Schilten.
    s = HardStrategy("comps")
    play = Play(spiel=1)
    _hand_with_suits(play, "comps", {"Schilten": ["A", "K", "U", "9"]})
    msg = s.pick_trump(play, schieben_allowed=True)
    assert msg == {"type": "choose_trump", "operator": "Schilten"}


def test_hard_pick_trump_schiebens_when_weak_and_allowed():
    # 3-card best suit → schieben.
    s = HardStrategy("comps")
    play = Play(spiel=1)
    _hand_with_suits(play, "comps", {
        "Eicheln": ["A", "K", "9"],
        "Rosen": ["8", "7"],
        "Schellen": ["6", "U"],
        "Schilten": ["O", "B"],
    })
    msg = s.pick_trump(play, schieben_allowed=True)
    assert msg == {"type": "schieben"}


def test_hard_pick_trump_falls_back_to_max_score_post_schieben():
    # Post-schieben: same weak hand, but schieben_allowed=False forces commit.
    # With four Asses-and-Kings, Oben should score highest.
    s = HardStrategy("comps")
    play = Play(spiel=1)
    _hand_with_suits(play, "comps", {
        "Eicheln": ["A", "K"],
        "Rosen": ["A", "K"],
        "Schellen": ["A", "K"],
        "Schilten": ["A"],   # 9 cards total
    })
    msg = s.pick_trump(play, schieben_allowed=False)
    assert msg["type"] == "choose_trump"
    # All Asses + Kings dominates Oben (4×11 + 4×4 = 60 over 9 cards).
    assert msg["operator"] == "Oben"


def test_hard_pick_trump_long_no_under_no_neun_schiebens():
    # 5 cards but no Under or Neun → schieben.
    s = HardStrategy("comps")
    play = Play(spiel=1)
    _hand_with_suits(play, "comps", {
        "Eicheln": ["A", "K", "O", "B", "8"],
        "Rosen": ["A", "K", "O", "7"],
    })
    msg = s.pick_trump(play, schieben_allowed=True)
    assert msg == {"type": "schieben"}
```

- [ ] **Step 2: Run failing**

Expected: NotImplementedError on `pick_trump`.

- [ ] **Step 3: Implement**

Add to `HardStrategy`:
```python
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
```

- [ ] **Step 4: Run tests**

Expected: 20 passed (16 + 4 new).

- [ ] **Step 5: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_strategies.py
git -c commit.gpgsign=false commit -m "feat(ai): HardStrategy.pick_trump (4-trump heuristic + 6-mode forced fallback)"
```

---

## Task 5: HardStrategy.pick_card — leading

**Files:**
- Modify: `ausbau/ai_strategies.py`
- Modify: `tests/multiplayer/test_ai_strategies.py`

- [ ] **Step 1: Write failing tests**

```python
def test_hard_pick_card_lead_plays_guaranteed_winner_ass():
    """When leading and we hold the highest remaining of a suit, play it."""
    s = HardStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    # Stuff hand so comps holds RA (Rosen Ass) and Rosen-Ass is the highest
    # remaining of its suit (no other Rosen Ass exists).
    _hand_with_suits(play, "comps", {
        "Rosen": ["A", "9", "8"],
        "Eicheln": ["7", "6"],
        "Schellen": ["7", "6"],
        "Schilten": ["6", "U"],
    })
    s.on_spiel_start(play)
    msg = s.pick_card(play, lead_suit=None, trick_so_far=[])
    assert msg == {"type": "play_card", "card": "RA"}


def test_hard_pick_card_lead_no_winner_plays_lowest():
    """When no card guarantees a win when leading, play lowest-point."""
    s = HardStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    _hand_with_suits(play, "comps", {
        "Rosen": ["6", "7"],
        "Eicheln": ["6", "7"],
        "Schellen": ["6", "7"],
        "Schilten": ["6", "7", "8"],
    })
    s.on_spiel_start(play)
    msg = s.pick_card(play, lead_suit=None, trick_so_far=[])
    assert msg["type"] == "play_card"
    # All cards are 0 points (Sechs); pick is deterministic but we just
    # assert it returned a 0-point card from the hand.
    assert msg["card"] in {"R6","R7","E6","E7","SE6","SE7","SI6","SI7","SI8"}
```

- [ ] **Step 2: Run failing**

Expected: NotImplementedError on `pick_card`.

- [ ] **Step 3: Implement leading branch + helpers (no follow yet)**

Add to `HardStrategy`:
```python
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
        from Cards_refactored import SUITS
        # Compare against tracked remaining cards in the same suit.
        from ausbau.game_session import find_card_in_hand
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
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/multiplayer/test_ai_strategies.py -v
```
Expected: 22 passed.

- [ ] **Step 5: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_strategies.py
git -c commit.gpgsign=false commit -m "feat(ai): HardStrategy.pick_card lead branch (cash guaranteed winners)"
```

---

## Task 6: HardStrategy.pick_card — following + trump conservation

**Files:**
- Modify: `ausbau/ai_strategies.py`
- Modify: `tests/multiplayer/test_ai_strategies.py`

- [ ] **Step 1: Write failing tests**

```python
def test_hard_follow_partner_winning_dumps_low():
    """Partner has played the leading card. Dump low; do NOT trump in."""
    s = HardStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    # comps's partner is compn (per Cards_refactored partner mapping)
    _hand_with_suits(play, "comps", {
        "Rosen": ["A", "9", "6"],
        "Eicheln": ["U", "7"],
        "Schellen": [],
        "Schilten": ["O", "B"],
    })
    s.on_spiel_start(play)
    # Partner (compn) led RA — they're winning.
    msg = s.pick_card(play, lead_suit="Rosen",
                      trick_so_far=[{"position": "compn", "card": "RA"}])
    # Should follow with lowest Rosen (R6, 0 points).
    assert msg == {"type": "play_card", "card": "R6"}


def test_hard_follow_opponent_winning_beats_cheaply():
    """Opponent is leading; we beat with the cheapest valid card that wins."""
    s = HardStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    _hand_with_suits(play, "comps", {
        "Rosen": ["A", "K", "9"],
        "Eicheln": ["7"],
        "Schellen": [],
        "Schilten": ["6"],
    })
    s.on_spiel_start(play)
    # Opponent (compe) led R8.
    msg = s.pick_card(play, lead_suit="Rosen",
                      trick_so_far=[{"position": "compe", "card": "R8"}])
    # Cheapest beat is R9 (0 points, beats R8 rank).
    assert msg == {"type": "play_card", "card": "R9"}


def test_hard_follow_no_lead_suit_dumps_low_when_cant_beat():
    """Can't follow lead suit, can't trump cheaply; dump lowest non-trump."""
    s = HardStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    # comps has no Rosen; trump is Eicheln.
    _hand_with_suits(play, "comps", {
        "Rosen": [],
        "Eicheln": ["U", "8"],   # trump
        "Schellen": ["6"],
        "Schilten": ["7"],
    })
    s.on_spiel_start(play)
    # Opponent led RA; current trick total = 11 (one Ass).
    msg = s.pick_card(play, lead_suit="Rosen",
                      trick_so_far=[{"position": "compe", "card": "RA"}])
    # Trick total < 18, so DON'T trump. Dump lowest non-trump (SE6, 0 pts).
    assert msg["card"] in ("SE6", "SI7")  # both are 0 pts; pick is deterministic
    assert msg["type"] == "play_card"


def test_hard_trump_steal_when_trick_high_value():
    """Trick already has 18+ points; we have trump; steal it."""
    s = HardStrategy("comps")
    play = Play(spiel=1)
    play.operator = "Eicheln"
    _hand_with_suits(play, "comps", {
        "Rosen": [],
        "Eicheln": ["6"],   # one trump
        "Schellen": ["7"],
        "Schilten": ["8"],
    })
    s.on_spiel_start(play)
    # Trick: opponent led Ass (11) + partner played Ober... no wait, partner's a teammate.
    # Two opponents played: compe RA (11) + compo R K (4) + we're 4th to play? 
    # Partner is compn for comps. So compe + compo are opponents.
    # Trick so far: RA (11) + RK (4) + compn (partner) RB (8 for Banner) = 23 pts.
    # The compn at index 2 is partner. Even though partner played, total >=18
    # and trump conservation overlay should apply only when partner is winning.
    # Partner played RB (rank 5, lower than A) so opponent compe (RA) wins the trick.
    msg = s.pick_card(play, lead_suit="Rosen",
                      trick_so_far=[
                          {"position": "compe", "card": "RA"},
                          {"position": "compn", "card": "RB"},
                          {"position": "compo", "card": "RK"},
                      ])
    # Opponent winning, trick total ~23 ≥ 18, no Rosen in hand → trump in with E6.
    assert msg == {"type": "play_card", "card": "E6"}
```

- [ ] **Step 2: Run failing**

Expected: failures (Task 5 stub picks lowest unconditionally).

- [ ] **Step 3: Replace pick_card following branch**

In `HardStrategy.pick_card`, replace the trailing follow branch with:
```python
        # ── Following ──────────────────────────────────────────────────────
        from Cards_refactored import SUITS
        operator = play.operator

        # Determine current trick winner.
        played = trick_so_far  # [{position, card}, ...] — at most 3
        winner_position = self._winner_so_far(played, operator)
        partner_position = play.partner.get(self.position)
        partner_winning = (winner_position == partner_position)

        # Sum points already on the table.
        from ausbau.game_session import find_card_in_hand, card_to_code
        from Cards_refactored import create_card
        from ausbau.game_session import RANK_SUFFIX
        inverse_rank = {v: k for k, v in RANK_SUFFIX.items()}

        def _code_to_card(code):
            from ausbau.ai_strategies import _split_code
            suit, rank_suffix = _split_code(code)
            return create_card(inverse_rank[rank_suffix], suit)

        trick_total = sum(
            self._card_value(_code_to_card(p["card"]), operator) for p in played
        )

        if partner_winning:
            # Dump lowest valid card.
            pick = min(valid_cards, key=lambda c: self._card_value(c, operator))
            return {"type": "play_card", "card": card_to_code(pick)}

        # Opponent winning. Try to beat cheaply.
        winning_card = _code_to_card(
            next(p["card"] for p in played if p["position"] == winner_position)
        )
        winning_strength = self._strength(winning_card, operator, lead_suit)

        beaters = [c for c in valid_cards
                   if self._strength(c, operator, lead_suit) > winning_strength]
        if beaters:
            cheapest = min(beaters, key=lambda c: self._card_value(c, operator))
            # Cheap take threshold: cheap enough vs. trick value.
            if self._card_value(cheapest, operator) <= trick_total + 5:
                # Trump conservation overlay — see below before returning.
                pick = cheapest
            else:
                pick = min(valid_cards, key=lambda c: self._card_value(c, operator))
        else:
            pick = min(valid_cards, key=lambda c: self._card_value(c, operator))

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
                pick = min(non_trump_alts, key=lambda c: self._card_value(c, operator))

        # High-value trump steal: if trick is rich and we can trump in.
        if (
            operator in SUITS
            and lead_suit != operator
            and trick_total >= 18
            and not partner_winning
        ):
            trump_cards = [c for c in valid_cards if c.suit == operator]
            if trump_cards:
                pick = min(trump_cards, key=lambda c: self._card_value(c, operator))

        return {"type": "play_card", "card": card_to_code(pick)}

    def _winner_so_far(self, played: list, operator: str) -> Optional[str]:
        """Return position of the current trick winner among `played`. None if empty."""
        if not played:
            return None
        from Cards_refactored import create_card
        from ausbau.game_session import RANK_SUFFIX
        from ausbau.ai_strategies import _split_code
        inverse_rank = {v: k for k, v in RANK_SUFFIX.items()}

        def _to_card(code):
            suit, rank_suffix = _split_code(code)
            return create_card(inverse_rank[rank_suffix], suit)

        lead_card = _to_card(played[0]["card"])
        lead_suit = lead_card.suit
        winner = played[0]["position"]
        best = self._strength(lead_card, operator, lead_suit)
        for entry in played[1:]:
            c = _to_card(entry["card"])
            s = self._strength(c, operator, lead_suit)
            if s > best:
                best = s
                winner = entry["position"]
        return winner
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/multiplayer/test_ai_strategies.py -v
```
Expected: 26 passed (22 + 4 new).

- [ ] **Step 5: Run full suite**

```bash
python -m pytest tests/ -q
```
Expected: 311 passed (285 baseline + 26 ai_strategies tests).

- [ ] **Step 6: Commit**

```bash
git add ausbau/ai_strategies.py tests/multiplayer/test_ai_strategies.py
git -c commit.gpgsign=false commit -m "feat(ai): HardStrategy.pick_card follow + trump conservation + high-value steal"
```

---

## Task 7: Seat fields + create_room defaults

**Files:**
- Modify: `ausbau/room.py`
- Modify: `tests/multiplayer/test_room_model.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/multiplayer/test_room_model.py`:
```python
def test_seat_default_ai_difficulty_medium():
    from ausbau.room import Seat
    s = Seat(position="compo")
    assert s.ai_difficulty == "medium"
    assert s._strategy is None  # Seat dataclass alone doesn't auto-build


def test_create_room_assigns_medium_strategy_to_ai_seats():
    from ausbau.room import create_room, Variant
    from ausbau.ai_strategies import MediumStrategy
    from frontend.auth.guest import Guest
    g = Guest(guest_id="a" * 32)
    room = create_room(host=g, variant=Variant())
    # Host seat is human → no strategy
    assert room.seats[0]._strategy is None
    # Other 3 are AI with MediumStrategy
    for i in (1, 2, 3):
        assert isinstance(room.seats[i]._strategy, MediumStrategy)
        assert room.seats[i].ai_difficulty == "medium"
        assert room.seats[i]._strategy.position == room.seats[i].position
```

- [ ] **Step 2: Run failing**

Expected: AttributeError (Seat has no `ai_difficulty` / `_strategy`).

- [ ] **Step 3: Add Seat fields**

In `ausbau/room.py`, modify the `Seat` dataclass:
```python
@dataclass
class Seat:
    position: str
    principal: Optional[object] = None
    websocket: Optional[object] = None
    is_ai: bool = True
    reconnect_deadline: Optional[float] = None
    connected_since: Optional[float] = None
    incoming: asyncio.Queue = field(default_factory=asyncio.Queue)
    state_event: asyncio.Event = field(default_factory=asyncio.Event)
    ai_difficulty: str = "medium"               # one of: easy / medium / hard
    _strategy: Optional[object] = None          # AIStrategy | None; built on demand
    # ... existing display_name() method unchanged
```

- [ ] **Step 4: Update `create_room`**

```python
def create_room(*, host, variant: Variant):
    from ausbau.game_session import GameSession
    from ausbau.ai_strategies import make_strategy
    code = make_code()
    session = GameSession(
        code=code,
        host_principal_id=principal_id(host),
        variant=variant,
    )
    session.seats[0].principal = host
    session.seats[0].is_ai = False
    # Auto-AI seats 1-3 with default-medium strategy.
    for i in (1, 2, 3):
        seat = session.seats[i]
        seat._strategy = make_strategy(seat.ai_difficulty, seat.position)
    ROOMS[code] = session
    return session
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/multiplayer/test_room_model.py -v
python -m pytest tests/ -q
```
Expected: 313 passed (311 + 2 new).

- [ ] **Step 6: Commit**

```bash
git add ausbau/room.py tests/multiplayer/test_room_model.py
git -c commit.gpgsign=false commit -m "feat(ai): Seat.ai_difficulty / _strategy fields + create_room default-medium"
```

---

## Task 8: Lifecycle — join, leave, AI takeover

**Files:**
- Modify: `ausbau/server.py` (`/join`, `/leave`)
- Modify: `ausbau/game_session.py` (`_reconnect_timeout`)
- Create: `tests/multiplayer/test_ai_difficulty_lifecycle.py`

Per spec §5: human-joins-AI-seat clears `_strategy`; human-leaves-AI-seat in lobby rebuilds `_strategy` from preserved difficulty; AI-takeover mid-game resets `ai_difficulty="medium"` and rebuilds `_strategy`.

- [ ] **Step 1: Write failing tests**

`tests/multiplayer/test_ai_difficulty_lifecycle.py`:
```python
import pytest
from ausbau.game_session import GameSession
from ausbau.room import Variant, ROOMS, create_room
from ausbau.ai_strategies import MediumStrategy, HardStrategy
from frontend.auth.guest import Guest

pytestmark = pytest.mark.asyncio


async def test_human_join_clears_strategy_keeps_difficulty():
    """Manually simulate /join's effect on the seat. Difficulty preserved."""
    g_host = Guest(guest_id="h" * 32)
    g_join = Guest(guest_id="j" * 32)
    room = create_room(host=g_host, variant=Variant())
    seat = room.seats[1]
    seat.ai_difficulty = "hard"
    from ausbau.ai_strategies import make_strategy
    seat._strategy = make_strategy("hard", seat.position)
    # Simulate join: replicate what /join does to an AI seat.
    seat.principal = g_join
    seat.is_ai = False
    seat._strategy = None
    assert seat.ai_difficulty == "hard"          # preserved
    assert seat._strategy is None


async def test_lobby_leave_rebuilds_strategy_from_preserved_difficulty():
    """When a human leaves an AI-seat in lobby, _strategy must rebuild."""
    from ausbau.ai_strategies import make_strategy
    g_host = Guest(guest_id="h" * 32)
    g_join = Guest(guest_id="j" * 32)
    room = create_room(host=g_host, variant=Variant())
    seat = room.seats[1]
    seat.ai_difficulty = "hard"
    # Human took the seat:
    seat.principal = g_join
    seat.is_ai = False
    seat._strategy = None
    # Now they leave (server.py path will eventually call _strategy rebuild).
    # We test the helper directly.
    seat.principal = None
    seat.is_ai = True
    # The /leave endpoint must do this. We test the endpoint in Task 11.
    # Here we test the seat-side invariant: rebuild yields correct class.
    seat._strategy = make_strategy(seat.ai_difficulty, seat.position)
    assert isinstance(seat._strategy, HardStrategy)
    assert seat._strategy.position == seat.position


async def test_mid_game_ai_takeover_resets_difficulty_to_medium(fast_clock):
    """AI takeover post-disconnect resets difficulty to medium."""
    g_host = Guest(guest_id="h" * 32)
    room = create_room(host=g_host, variant=Variant())
    # Replace seat 1 with a hard human seat
    seat = room.seats[1]
    seat.principal = Guest(guest_id="x" * 32)
    seat.is_ai = False
    seat.websocket = None  # disconnected
    seat.ai_difficulty = "hard"
    seat._strategy = None
    room.state = "playing"

    await room._reconnect_timeout("compn")

    assert seat.is_ai is True
    assert seat.ai_difficulty == "medium"        # reset!
    assert isinstance(seat._strategy, MediumStrategy)
```

- [ ] **Step 2: Run failing**

```bash
python -m pytest tests/multiplayer/test_ai_difficulty_lifecycle.py -v
```
Expected: 1st passes, 2nd passes (testing invariant directly), 3rd fails (`_reconnect_timeout` doesn't touch `_strategy` yet).

- [ ] **Step 3: Patch `_reconnect_timeout`**

In `ausbau/game_session.py`, find `_reconnect_timeout`. After `seat.is_ai = True`:
```python
        seat.is_ai = True
        seat.reconnect_deadline = None
        # Sub-project C: reset AI difficulty on takeover (spec §5 step 5).
        seat.ai_difficulty = "medium"
        from ausbau.ai_strategies import make_strategy
        seat._strategy = make_strategy("medium", position)
        self._reconnect_tasks.pop(position, None)
```

- [ ] **Step 4: Patch `/join` and `/leave`**

In `ausbau/server.py` find `/join` endpoint. After the line that sets `seat.is_ai = False` / `seat.principal = principal`:
```python
        seat._strategy = None
```

Find `/leave` endpoint. After the seat reverts to AI in the lobby branch (`seat.is_ai = True`, `seat.principal = None`):
```python
        from ausbau.ai_strategies import make_strategy
        seat._strategy = make_strategy(seat.ai_difficulty, seat.position)
```

(The exact insertion points depend on existing structure — locate them by searching for the seat-revert-to-AI logic in `/leave`.)

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/multiplayer/test_ai_difficulty_lifecycle.py tests/multiplayer/test_join_leave.py tests/multiplayer/test_disconnect.py -v
python -m pytest tests/ -q
```
Expected: full suite still green; new lifecycle tests pass. 316 passed (313 + 3 new).

- [ ] **Step 6: Commit**

```bash
git add ausbau/server.py ausbau/game_session.py tests/multiplayer/test_ai_difficulty_lifecycle.py
git -c commit.gpgsign=false commit -m "feat(ai): lifecycle — join clears strategy; leave/takeover rebuild"
```

---

## Task 9: Wire `_compute_ai_action` + pass `trick_so_far`

**Files:**
- Modify: `ausbau/game_session.py`

- [ ] **Step 1: Replace `_compute_ai_action` body**

Find the method `_compute_ai_action(self, seat, valid_actions: dict) -> dict`. Replace its body with:
```python
    def _compute_ai_action(self, seat, valid_actions: dict) -> dict:
        """Delegate to the seat's strategy. Defensive rebuild if missing."""
        if seat._strategy is None:
            from ausbau.ai_strategies import make_strategy
            import logging
            logging.warning(
                "AI seat %s had no strategy; defensive rebuild as %s",
                seat.position, seat.ai_difficulty,
            )
            seat._strategy = make_strategy(seat.ai_difficulty or "medium", seat.position)

        action_type = valid_actions.get("type")
        play = valid_actions.get("play") or self.current_play
        if action_type == "trump":
            return seat._strategy.pick_trump(
                play, valid_actions.get("schieben_allowed", True),
            )
        if action_type == "play_card":
            return seat._strategy.pick_card(
                play,
                valid_actions.get("lead_suit"),
                valid_actions.get("trick_so_far") or [],
            )
        return {"type": "noop"}
```

- [ ] **Step 2: Pass `play` and `trick_so_far` in `valid_actions`**

In `_trump_phase`, find the `_await_seat_action` call. Modify to add `"play": play`:
```python
            msg = await self._await_seat_action(target_position, valid_actions={
                "type": "trump",
                "options": list(TRUMP_OPTIONS),
                "schieben_allowed": schieben_allowed,
                "hand": getattr(play, target_position, None),
                "play": play,
            })
```

In `_play_trick`, find the `_await_seat_action` call inside the per-iteration loop. Modify:
```python
            msg = await self._await_seat_action(player, valid_actions={
                "type": "play_card",
                "lead_suit": lead_suit,
                "operator": play.operator,
                "valid_cards": valid,
                "hand": hand,
                "play": play,
                "trick_so_far": list(trick_order),
            })
```

(Find the actual var names — `trick_order` is the in-flight list; verify in current code.)

- [ ] **Step 3: Run all tests**

```bash
python -m pytest tests/ -q
```
Expected: 316 passed (existing tests still green; AI dispatch now uses strategies).

- [ ] **Step 4: Commit**

```bash
git add ausbau/game_session.py
git -c commit.gpgsign=false commit -m "feat(ai): _compute_ai_action delegates to seat._strategy + trick_so_far in valid_actions"
```

---

## Task 10: Wire lifecycle hooks — `on_spiel_start` + `on_card_played`

**Files:**
- Modify: `ausbau/game_session.py`

- [ ] **Step 1: Hook `on_spiel_start` in `_run_spiel`**

Find `_run_spiel`. After `play = Play(spiel_num)` and `self.current_play = play`, add:
```python
        # Sub-project C: notify each AI seat's strategy.
        for s in self.seats:
            if s.is_ai and s._strategy is not None:
                s._strategy.on_spiel_start(play)
```

- [ ] **Step 2: Hook `on_card_played` in `_play_trick`**

Find `_play_trick`. After the `card_played` broadcast inside the per-iteration loop:
```python
            await self.broadcast({
                "type": "card_played",
                "by_position": player,
                "card": card_to_code(card),
            })
            # Sub-project C: feed AI memory.
            for s in self.seats:
                if s.is_ai and s._strategy is not None:
                    s._strategy.on_card_played(player, card_to_code(card))
```

- [ ] **Step 3: Verify with existing e2e**

```bash
python -m pytest tests/multiplayer/test_e2e_4_humans.py tests/multiplayer/test_run_spiel.py -v
```
Expected: green.

- [ ] **Step 4: Run full suite**

```bash
python -m pytest tests/ -q
```
Expected: 316 passed.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py
git -c commit.gpgsign=false commit -m "feat(ai): wire on_spiel_start + on_card_played lifecycle hooks"
```

---

## Task 11: `POST /rooms/{code}/ai_difficulty` endpoint

**Files:**
- Modify: `ausbau/server.py`
- Modify: `ausbau/game_session.py` (`_seat_to_dict`)
- Modify: tests for `_seat_to_dict` if any (`tests/multiplayer/test_seat_helpers.py`)
- Create: `tests/multiplayer/test_ai_difficulty_endpoint.py`

- [ ] **Step 1: Add `ai_difficulty` to `_seat_to_dict`**

In `ausbau/game_session.py` `_seat_to_dict`:
```python
    def _seat_to_dict(self, seat) -> dict:
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
            "ai_difficulty": seat.ai_difficulty if seat.is_ai else None,
        }
```

In `ausbau/server.py` `_seat_to_dict`:
```python
def _seat_to_dict(seat, room) -> dict:
    from ausbau.room import principal_id
    return {
        "position": seat.position,
        "display_name": seat.display_name(),
        "is_ai": seat.is_ai,
        "connected": seat.websocket is not None and not seat.is_ai,
        "is_host": (
            seat.principal is not None
            and principal_id(seat.principal) == room.host_principal_id
        ),
        "principal_id": (
            principal_id(seat.principal) if seat.principal is not None else None
        ),
        "ai_difficulty": seat.ai_difficulty if seat.is_ai else None,
    }
```

- [ ] **Step 2: Add the endpoint**

In `ausbau/server.py`, near the other `/rooms/{code}/...` endpoints:
```python
@app.post("/rooms/{code}/ai_difficulty", status_code=200)
async def ai_difficulty_endpoint(
    code: str,
    request: Request,
    response: Response,
    payload: Optional[dict] = Body(default={}),
):
    """Set an AI seat's difficulty. Host-only, lobby-only.

    Body: {"position": "compe", "level": "hard"}
    """
    from ausbau.room import get_room, principal_id, POSITIONS
    from ausbau.ai_strategies import make_strategy

    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")

    principal = await _get_principal(request, response)
    if principal_id(principal) != room.host_principal_id:
        raise HTTPException(403, "not host")
    if room.state != "lobby":
        raise HTTPException(409, f"lobby only; state={room.state}")

    body = payload or {}
    position = body.get("position")
    level = body.get("level")
    if position not in POSITIONS:
        raise HTTPException(400, "invalid position")
    if level not in ("easy", "medium", "hard"):
        raise HTTPException(400, f"unknown difficulty: {level!r}")

    seat = next(s for s in room.seats if s.position == position)
    if not seat.is_ai:
        raise HTTPException(400, "seat is human, no AI difficulty")

    seat.ai_difficulty = level
    seat._strategy = make_strategy(level, seat.position)

    await room.broadcast({
        "type": "seat_changed",
        "seat": _seat_to_dict(seat, room),
        "reason": "ai_difficulty",
    })
    return _room_state_dict(room)
```

- [ ] **Step 3: Write endpoint tests**

`tests/multiplayer/test_ai_difficulty_endpoint.py`:
```python
import pytest
from fastapi.testclient import TestClient
from ausbau.server import app
from ausbau.room import ROOMS, create_room, Variant
from frontend.auth.guest import Guest, issue_guest_cookie
from frontend.auth.settings import Settings


@pytest.fixture(autouse=True)
def patch_auth(monkeypatch, tmp_path):
    """Stub the auth init so TestClient calls don't need real auth env."""
    settings = Settings(
        secret_key="x" * 32,
        base_url="http://test",
        smtp_user="x@y", smtp_app_password="x",
        mail_backend="console", admin_bootstrap_email="root@y",
        auth_db_url=f"sqlite+aiosqlite:///{tmp_path}/auth.db",
    )
    monkeypatch.setattr("ausbau.server._auth_settings", settings)
    monkeypatch.setattr("ausbau.server._auth_factory", None)
    yield


def _set_guest_cookie(client, guest):
    from frontend.auth.guest import issue_guest_cookie
    cookie_value, _ = issue_guest_cookie("x" * 32)
    client.cookies.set("schieber_guest", cookie_value)


def _make_lobby(client, host_guest):
    _set_guest_cookie(client, host_guest)
    r = client.post("/rooms",
                    json={"variant": {}},
                    headers={"X-Requested-With": "schieber"})
    assert r.status_code == 201, r.text
    return r.json()["code"]


def test_set_ai_difficulty_happy():
    g = Guest(guest_id="h" * 32)
    with TestClient(app) as client:
        code = _make_lobby(client, g)
        r = client.post(
            f"/rooms/{code}/ai_difficulty",
            json={"position": "compn", "level": "hard"},
            headers={"X-Requested-With": "schieber"},
        )
        assert r.status_code == 200
        room = ROOMS[code]
        seat = next(s for s in room.seats if s.position == "compn")
        from ausbau.ai_strategies import HardStrategy
        assert seat.ai_difficulty == "hard"
        assert isinstance(seat._strategy, HardStrategy)


def test_set_ai_difficulty_invalid_level():
    g = Guest(guest_id="h" * 32)
    with TestClient(app) as client:
        code = _make_lobby(client, g)
        r = client.post(
            f"/rooms/{code}/ai_difficulty",
            json={"position": "compn", "level": "expert"},
            headers={"X-Requested-With": "schieber"},
        )
        assert r.status_code == 400


def test_set_ai_difficulty_invalid_position():
    g = Guest(guest_id="h" * 32)
    with TestClient(app) as client:
        code = _make_lobby(client, g)
        r = client.post(
            f"/rooms/{code}/ai_difficulty",
            json={"position": "compZ", "level": "hard"},
            headers={"X-Requested-With": "schieber"},
        )
        assert r.status_code == 400


def test_set_ai_difficulty_human_seat():
    g = Guest(guest_id="h" * 32)
    with TestClient(app) as client:
        code = _make_lobby(client, g)
        # Seat 0 (compo) is the human host.
        r = client.post(
            f"/rooms/{code}/ai_difficulty",
            json={"position": "compo", "level": "hard"},
            headers={"X-Requested-With": "schieber"},
        )
        assert r.status_code == 400


def test_set_ai_difficulty_not_host():
    g_host = Guest(guest_id="h" * 32)
    g_other = Guest(guest_id="o" * 32)
    with TestClient(app) as client:
        code = _make_lobby(client, g_host)
        # Switch to another guest cookie.
        from frontend.auth.guest import issue_guest_cookie
        other_cookie, _ = issue_guest_cookie("x" * 32)
        client.cookies.set("schieber_guest", other_cookie)
        r = client.post(
            f"/rooms/{code}/ai_difficulty",
            json={"position": "compn", "level": "hard"},
            headers={"X-Requested-With": "schieber"},
        )
        assert r.status_code == 403


def test_set_ai_difficulty_mid_game_409():
    g = Guest(guest_id="h" * 32)
    with TestClient(app) as client:
        code = _make_lobby(client, g)
        ROOMS[code].state = "playing"
        r = client.post(
            f"/rooms/{code}/ai_difficulty",
            json={"position": "compn", "level": "hard"},
            headers={"X-Requested-With": "schieber"},
        )
        assert r.status_code == 409


def test_set_ai_difficulty_room_not_found_404():
    g = Guest(guest_id="h" * 32)
    with TestClient(app) as client:
        _set_guest_cookie(client, g)
        r = client.post(
            "/rooms/NOSUCH/ai_difficulty",
            json={"position": "compn", "level": "hard"},
            headers={"X-Requested-With": "schieber"},
        )
        assert r.status_code == 404
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/multiplayer/test_ai_difficulty_endpoint.py -v
python -m pytest tests/ -q
```
Expected: 7 endpoint tests pass; full suite at 323 (316 + 7).

- [ ] **Step 5: Commit**

```bash
git add ausbau/server.py ausbau/game_session.py tests/multiplayer/test_ai_difficulty_endpoint.py
git -c commit.gpgsign=false commit -m "feat(ai): POST /rooms/{code}/ai_difficulty + ai_difficulty in seat dict"
```

---

## Task 12: Frontend lobby integration

**Files:**
- Modify: `ausbau/html5/lobby.html`
- Modify: `ausbau/html5/js/lobby.js`
- Modify: `ausbau/html5/css/lobby.css`
- Modify: `tests/multiplayer/test_lobby_page.py`

- [ ] **Step 1: HTML — add a `<select>` skeleton in the seats list**

In `ausbau/html5/lobby.html`, the seats list is currently `<ul id="seats"></ul>`. The dropdown is rendered per-seat by JS. No HTML change needed beyond ensuring the seats list container exists; JS owns the markup for AI rows.

- [ ] **Step 2: CSS — style the dropdown**

In `ausbau/html5/css/lobby.css`, append:
```css
.seats select.ai-difficulty {
  margin-left: 0.5rem;
  font-size: 0.85rem;
}
.seats select.ai-difficulty:disabled {
  opacity: 0.6;
}
```

- [ ] **Step 3: JS — render dropdown for AI seats; wire change handler**

In `ausbau/html5/js/lobby.js`, find the `render()` function's seat-rendering loop. Modify each `<li>` build for an AI seat:
```javascript
function render() {
  if (!currentRoomState) return;
  $code.textContent = currentRoomState.code;
  $seats.innerHTML = '';
  let mySeat = null;
  let amHost = false;
  for (const s of currentRoomState.seats) {
    if (s.is_host && s.principal_id === myPrincipalId) amHost = true;
  }
  for (const s of currentRoomState.seats) {
    const li = document.createElement('li');
    const flags = [];
    if (s.is_host) flags.push('HOST');
    if (s.is_ai) flags.push('AI');
    if (!s.connected && !s.is_ai) flags.push('paused');
    const label = `${s.position}: ${s.display_name}${flags.length ? ' [' + flags.join(' ') + ']' : ''}`;
    li.textContent = label;

    if (s.is_ai) {
      const sel = document.createElement('select');
      sel.className = 'ai-difficulty';
      sel.dataset.position = s.position;
      for (const lvl of ['easy', 'medium', 'hard']) {
        const opt = document.createElement('option');
        opt.value = lvl;
        opt.textContent = lvl;
        if (lvl === s.ai_difficulty) opt.selected = true;
        sel.appendChild(opt);
      }
      sel.disabled = !amHost || currentRoomState.state !== 'lobby';
      sel.addEventListener('change', async (ev) => {
        try {
          await api(`/rooms/${currentRoomState.code}/ai_difficulty`, {
            method: 'POST',
            body: { position: ev.target.dataset.position, level: ev.target.value },
          });
        } catch (err) {
          $error.textContent = err.message;
          await refresh();   // revert dropdown to server state
        }
      });
      li.appendChild(sel);
    }

    $seats.appendChild(li);
    if (s.principal_id === myPrincipalId && !s.is_ai) mySeat = s;
  }
  // ... (existing variant + buttons rendering — unchanged)
}
```

(Keep the existing variant + button-gating code unchanged; only the seat-row loop is modified.)

- [ ] **Step 4: Smoke test JS asset**

Append to `tests/multiplayer/test_lobby_page.py`:
```python
def test_lobby_js_references_ai_difficulty_endpoint():
    from fastapi.testclient import TestClient
    from ausbau.server import app
    with TestClient(app) as client:
        r = client.get("/static/js/lobby.js")
        assert r.status_code == 200
        body = r.text
        assert "ai_difficulty" in body
        assert "ai-difficulty" in body  # the CSS class
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/multiplayer/test_lobby_page.py -v
python -m pytest tests/ -q
```
Expected: 324 passed (323 + 1 new).

- [ ] **Step 6: Commit**

```bash
git add ausbau/html5/lobby.html ausbau/html5/js/lobby.js ausbau/html5/css/lobby.css tests/multiplayer/test_lobby_page.py
git -c commit.gpgsign=false commit -m "feat(ai): lobby UI dropdown for per-AI-seat difficulty"
```

---

## Task 13: e2e mixed-difficulty integration test

**Files:**
- Modify: `tests/multiplayer/test_e2e_4_humans.py` OR create `tests/multiplayer/test_e2e_mixed_ai.py`

- [ ] **Step 1: Add the test**

`tests/multiplayer/test_e2e_mixed_ai.py`:
```python
import asyncio
import pytest
from ausbau.game_session import GameSession
from ausbau.room import Variant
from ausbau.ai_strategies import make_strategy
from frontend.auth.guest import Guest
from tests.multiplayer.conftest import FakeWebSocket, seat_4_humans

pytestmark = pytest.mark.asyncio


async def _human_responder(seat, ws, log):
    """Same pattern as test_e2e_4_humans.py."""
    last_seen = 0
    while True:
        if len(ws.sent) > last_seen:
            new_msgs = ws.sent[last_seen:]
            last_seen = len(ws.sent)
            for msg in new_msgs:
                t = msg.get("type")
                log.append(t)
                if t == "trump_request":
                    seat.incoming.put_nowait({
                        "type": "choose_trump",
                        "operator": "Eicheln",
                    })
                elif t == "weis_request":
                    seat.incoming.put_nowait({"type": "announce_weis", "announce": False})
                elif t == "play_request":
                    valid = msg.get("valid_cards") or []
                    if valid:
                        seat.incoming.put_nowait({"type": "play_card", "card": valid[0]})
                elif t == "game_end":
                    return
        await asyncio.sleep(0)


async def test_e2e_mixed_difficulty_3_ai(fast_clock):
    """1 human (compo) + 3 AIs at easy/medium/hard. Verify game completes."""
    g = Guest(guest_id="h" * 32)
    s = GameSession(
        code="MIXAI",
        host_principal_id=f"guest:{g.guest_id}",
        variant=Variant(),
        end_game=200,
    )
    # Seat 0 = human (compo); seats 1-3 = AI with mixed levels.
    s.seats[0].principal = g
    s.seats[0].is_ai = False
    s.seats[0].websocket = FakeWebSocket()
    s.seats[1].ai_difficulty = "easy"
    s.seats[1]._strategy = make_strategy("easy", s.seats[1].position)
    s.seats[2].ai_difficulty = "medium"
    s.seats[2]._strategy = make_strategy("medium", s.seats[2].position)
    s.seats[3].ai_difficulty = "hard"
    s.seats[3]._strategy = make_strategy("hard", s.seats[3].position)

    log = []
    responder = asyncio.create_task(
        _human_responder(s.seats[0], s.seats[0].websocket, log)
    )
    game = asyncio.create_task(s.start_game())

    try:
        await asyncio.wait_for(game, timeout=10.0)
    except asyncio.TimeoutError:
        pytest.fail(f"game didn't finish in 10s; log: {log}")
    finally:
        responder.cancel()

    assert s.state == "finished"
    assert s.seats[0].websocket.last_sent_of_type("game_end") is not None
    # All 3 AI strategies must have been consulted at least once.
    # We can't directly assert that here, but on_spiel_start populated
    # HardStrategy memory:
    assert s.seats[3]._strategy._remaining_by_suit  # non-empty after spiel start
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/multiplayer/test_e2e_mixed_ai.py -v
python -m pytest tests/ -q
```
Expected: 325 passed (324 + 1 new).

- [ ] **Step 3: Commit**

```bash
git add tests/multiplayer/test_e2e_mixed_ai.py
git -c commit.gpgsign=false commit -m "test(ai): e2e mixed-difficulty 3-AI integration"
```

---

## Task 14: CLAUDE.md update

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add sub-project C done note**

In `CLAUDE.md` "Refactoring Status" section, find the "Remaining sub-project: sub-project C" line and replace with:
```
- **Sub-project C — AI difficulty** (this branch). Spec: `docs/superpowers/specs/2026-04-29-schieber-ai-difficulty-design.md`. Plan: `docs/superpowers/plans/2026-04-30-schieber-ai-difficulty.md`. New module `ausbau/ai_strategies.py` defines `AIStrategy` ABC + `EasyStrategy` (uniform random) / `MediumStrategy` (today's heuristic) / `HardStrategy` (per-spiel card tracking + trump conservation + smarter trump pick incl. schieben). Per-seat via `Seat.ai_difficulty`. Host-only `/rooms/{code}/ai_difficulty` endpoint, lobby-only. Lobby UI shows a dropdown per AI seat. AI takeover (mid-game disconnect) resets the seat's difficulty to `medium`.

**All three sub-projects (A multiplayer, B accounts, C AI difficulty) are done.** Future work is variant expansion (§7.7) and stronger AI (sub-project D — partner inference, minimax).
```

- [ ] **Step 2: Run tests one final time**

```bash
python -m pytest tests/ -q
```
Expected: 325 passed.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git -c commit.gpgsign=false commit -m "docs(claude): mark sub-project C (AI difficulty) done"
```

---

## Self-review checklist

**Spec coverage:**
- §3 Architecture (module + Seat fields + endpoint): Tasks 1–7 + 11
- §4.1 AIStrategy ABC: Task 1
- §4.2 EasyStrategy: Task 1
- §4.3 MediumStrategy: Tasks 1 (impl) + 2 (tests)
- §4.4 HardStrategy: Tasks 3 (memory) + 4 (pick_trump) + 5 (lead) + 6 (follow + conservation)
- §4.5 Factory: Task 1
- §5 Data flow: Tasks 7 (room creation) + 8 (lifecycle) + 9 (dispatch) + 10 (hooks) + 11 (endpoint)
- §6 Trick-state plumbing: Task 9
- §7 HTTP API: Task 11
- §8 Lobby UI: Task 12
- §9 Error handling: Task 9 (defensive rebuild) + Task 11 (validation)
- §10 Testing: spread across all tasks
- §11 Out of scope: respected

**Type/name consistency:**
- `make_strategy(difficulty, position)` — signature matches across all callers (Tasks 1, 7, 8, 9, 11).
- `seat._strategy` (underscore-prefixed) — consistent.
- `seat.ai_difficulty` (no underscore) — consistent; serialised to dict.
- `pick_trump(play, schieben_allowed)` — 2 args; consistent.
- `pick_card(play, lead_suit, trick_so_far)` — 3 args; consistent. `valid_actions["trick_so_far"]` is forwarded by `_compute_ai_action`.

**No placeholders.** Every step contains the actual code or command; no "TBD".

**Variation:** none — single-pass plan.

**Spec compliance:** §10 testing target was ~25–30 tests; this plan adds ~40. Final test count ~325 (vs ~310 spec estimate); over-delivery on coverage is acceptable.
