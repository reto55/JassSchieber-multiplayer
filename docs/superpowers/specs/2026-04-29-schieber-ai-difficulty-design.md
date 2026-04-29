# Schieber — AI Difficulty (Sub-project C)

**Status:** Design / spec.
**Author:** Reto + Claude (Opus 4.7).
**Date:** 2026-04-29.
**Predecessors:** Sub-project A (multiplayer, done) and B (user accounts, done). This spec extends `Seat` and the AI dispatch path; no other multiplayer code changes.
**Linkage:** Spec §12.6 of `2026-04-28-schieber-multiplayer-design.md` reserved this work as a strategy slot on `Seat`.

---

## 1. Goal

Replace the single hard-coded AI heuristic (`ai_select_card` lead-high / follow-low + `farbe_lang` trump pick) with a per-seat configurable difficulty: **easy**, **medium**, **hard**. Each AI seat can be set independently. The current behaviour is preserved as `medium` so default rooms play identically to today.

## 2. Decisions (from brainstorm)

| ID | Decision |
|----|----------|
| Q1 | Three tiers: `easy` / `medium` / `hard`. |
| Q2 | `hard` adds: per-spiel card tracking + trump conservation + smarter trump pick (incl. schieben). |
| Q3 | Per-seat (not per-room). Field on `Seat`. |
| Q4 | Default for fresh AI seat: `medium`. |
| Q5 | Only the host can change AI difficulty in the lobby. |
| Q6 | Lobby-only change. Frozen once `state == "playing"`. |
| Q7 | `easy` = pure uniform random (cards AND trump pick). |
| Q8 | `hard` schieben heuristic: hybrid — schieben iff best-suit-length < 4 OR best suit has neither Under nor Nell, AND `schieben_allowed`. |
| Q9 | `hard` memory: per-spiel only (rebuild at spiel start, update on each `card_played`). No partner inference. |
| Q10 | Lobby preservation: `seat.ai_difficulty` survives human join+leave on that seat. AI-takeover (mid-game disconnect) resets to `medium`. |

## 3. Architecture

A new module `ausbau/ai_strategies.py` defines an abstract base class and three concrete strategies. `Seat` gets two new fields: `ai_difficulty: str` and `_strategy: AIStrategy | None`. `GameSession._compute_ai_action` becomes a one-line delegation to `seat._strategy`. A new HTTP endpoint `POST /rooms/{code}/ai_difficulty {position, level}` lets the host change a seat's difficulty in the lobby. `Variant` is unchanged — difficulty is strictly per-seat, not part of the room-level variant block.

The `_strategy` lifecycle invariant: **`seat.is_ai is True` ⇔ `seat._strategy is not None`**. All transitions (room creation, join, leave, AI-takeover, difficulty change) maintain this.

```
ausbau/
  ai_strategies.py        ← AIStrategy abstract + Easy/Medium/Hard concrete + factory
  room.py                 ← Seat gets ai_difficulty + _strategy fields
  game_session.py         ← _compute_ai_action delegates to seat._strategy
  server.py               ← POST /rooms/{code}/ai_difficulty
tests/multiplayer/
  test_ai_strategies.py            ← per-strategy unit tests
  test_ai_difficulty_endpoint.py   ← endpoint contract
  test_ai_difficulty_lifecycle.py  ← Seat._strategy lifecycle
```

## 4. Components

### 4.1 `AIStrategy` (abstract base)

```python
class AIStrategy:
    def pick_trump(self, play, schieben_allowed: bool) -> dict:
        """Return {'type': 'choose_trump', 'operator': <suit>} or {'type': 'schieben'}."""
        raise NotImplementedError

    def pick_card(self, play, lead_suit: str | None, trick_so_far: list[dict]) -> dict:
        """Return {'type': 'play_card', 'card': <code>}.

        trick_so_far: list of {'position': ..., 'card': <code>} dicts for cards
        already played in the current trick (in play order). Empty when leading.
        """
        raise NotImplementedError

    def on_spiel_start(self, play) -> None:
        """Lifecycle hook fired by _run_spiel before trump phase. Default no-op."""

    def on_card_played(self, player_position: str, card_code: str) -> None:
        """Lifecycle hook fired after each card_played broadcast. Default no-op."""
```

Each strategy is constructed with the position string it serves (`EasyStrategy(position="compe")`) so it can look up its own hand via `getattr(play, self.position)`. Strategies do not hold a reference to the `Seat` itself — they receive the live `play` object on each call.

### 4.2 `EasyStrategy`

- `pick_trump`: `random.choice(("Eicheln","Rosen","Schellen","Schilten","Oben","Unten"))`. Never schiebens.
- `pick_card`: `random.choice(get_valid_cards(hand, lead_suit, play.operator))`. Ignores `trick_so_far`.
- No state. No lifecycle work.

### 4.3 `MediumStrategy`

- `pick_trump`: `farbe_lang(hand)` — today's behaviour. Never schiebens. Returns one of the four suits (never Oben/Unten).
- `pick_card`: today's `ai_select_card(hand, lead_suit, play.operator)`. Lead = highest point value; follow = lowest. Ignores `trick_so_far`.
- No state. Default behaviour, identical to today's hard-coded AI.

### 4.4 `HardStrategy`

#### State
- `_remaining_by_suit: dict[str, set[str]]` — set of card codes still in play, keyed by suit name. Built in `on_spiel_start`, decremented in `on_card_played`.

#### `pick_trump(play, schieben_allowed)`
1. Group own hand cards by suit; for each suit, count its cards as would-be trumps and inspect ranks.
2. Find longest-by-length suit (tie-break: Schilten > Schellen > Eicheln > Rosen, matching `farbe_lang`).
3. **If** `len(best_suit) >= 4 AND ('Under' in ranks OR 'Neun' in ranks)`: return `{"type":"choose_trump","operator":<best_suit>}`.
4. **Elif** `schieben_allowed`: return `{"type":"schieben"}`.
5. **Else (post-schieben, MUST commit)**: score all 6 modes — for each trump suit, sum `w_trumpf` over the cards in that suit; for `Oben`, sum `w_oben` over the whole hand; for `Unten`, sum `w_unten` over the whole hand. Return the operator with the maximum score (tie-break: trump suits in `farbe_lang` order, then `Oben`, then `Unten`).

#### `pick_card(play, lead_suit)`
Compute valid cards via `get_valid_cards(hand, lead_suit, play.operator)`. Then:

1. **Leading (lead_suit is None):**
   - For each valid card, check if it is the highest remaining of its suit (using `_remaining_by_suit` and the rank-strength functions appropriate to `play.operator`).
   - If any guaranteed-winner exists, play the highest-point one (cash in winners early).
   - Else, play the lowest-point valid card.

2. **Following:**
   - Determine if partner is currently winning the trick (use `play.partner` mapping).
   - **If partner wins**: play the lowest-point valid card (dump).
   - **If opponent wins:**
     - Compute the cheapest valid card that beats the current best.
     - If its point value ≤ current trick total + 5 (cheap take), play it.
     - Else if `play.operator in SUITS` AND own cards include trump AND lead_suit ≠ trump AND current trick total ≥ 18, play the lowest trump (high-value steal).
     - Else play the lowest-point valid card.
   - **If no opponent or partner has played yet (i.e., 2nd to play):** treat as opponent-currently-winning.

3. **Trump-conservation overlay:** if `play.operator in SUITS` AND the chosen valid card is a trump AND lead_suit ≠ trump AND current trick total < 18 AND a non-trump card is in `valid`, downgrade the choice to the lowest-point non-trump valid card.

The "current trick total" is computed from `trick_so_far` using `trick_points` semantics for the active operator. Helper: a small private function on `HardStrategy` that sums `_card_value(card, play.operator)` over the codes in `trick_so_far` (see §6).

#### `on_spiel_start(play)`
Rebuild `_remaining_by_suit`:

```python
self._remaining_by_suit = {suit: set() for suit in SUITS}
own_codes = set(hand_to_codes(getattr(play, self.position)))
for code in ALL_36_CARD_CODES:
    if code in own_codes:
        continue
    suit_letter = code[:-1]   # 'E', 'R', 'SE', 'SI'
    suit_name = INVERSE_SUIT_PREFIX[suit_letter]
    self._remaining_by_suit[suit_name].add(code)
```

`ALL_36_CARD_CODES` is computed once at module load: cartesian product of `SUIT_PREFIX` × `RANK_SUFFIX`.

#### `on_card_played(player_position, card_code)`
- Don't track own plays (we've already removed those by virtue of starting with `_remaining_by_suit` excluding own hand). Skip if `player_position == self.position`.
- Else `discard` the code from the matching suit set. If the code is not in the set, log a warning at INFO level (no crash — defensive against missed lifecycle hooks).

### 4.5 Factory

```python
def make_strategy(difficulty: str, position: str) -> AIStrategy:
    if difficulty == "easy":
        return EasyStrategy(position)
    if difficulty == "medium":
        return MediumStrategy(position)
    if difficulty == "hard":
        return HardStrategy(position)
    raise ValueError(f"unknown difficulty: {difficulty!r}")
```

`make_strategy` is the only constructor used by `room.py` and `game_session.py`. Direct class instantiation is reserved for tests.

## 5. Data Flow

1. **Room creation (`create_room`):** for each of seats 1–3 (the auto-AI seats), set `ai_difficulty="medium"` and `_strategy=make_strategy("medium", position)`.
2. **Lobby — change difficulty:** host POSTs `/rooms/{code}/ai_difficulty {position, level}`. Server validates (host, lobby, AI seat, level valid). On success: `seat.ai_difficulty = level`; `seat._strategy = make_strategy(level, position)`; broadcasts `seat_changed` with `reason="ai_difficulty"`.
3. **Human joins AI seat (`/join`):** `seat._strategy = None`. `seat.ai_difficulty` is preserved on the seat (so leaving restores it). `seat.is_ai = False` and `seat.principal = <human>` (existing behavior).
4. **Human leaves AI seat in lobby (`/leave`):** existing flow flips `is_ai=True`. Add `seat._strategy = make_strategy(seat.ai_difficulty, position)`.
5. **AI takeover mid-game (`_reconnect_timeout`):** seat goes to AI. `seat.ai_difficulty = "medium"` (reset per Q10b — defeats ragequit-for-easy-AI exploit). `seat._strategy = make_strategy("medium", position)`.
6. **Spiel start (`_run_spiel`):** for each AI seat, `seat._strategy.on_spiel_start(play)`.
7. **Trump phase (`_compute_ai_action`):** if `valid_actions["type"] == "trump"`, dispatch to `seat._strategy.pick_trump(play, valid_actions["schieben_allowed"])`.
8. **Play phase (`_compute_ai_action`):** if `valid_actions["type"] == "play_card"`, dispatch to `seat._strategy.pick_card(play, valid_actions.get("lead_suit"))`.
9. **After each `card_played` broadcast in `_play_trick`:** for every AI seat, call `seat._strategy.on_card_played(player_position, card_code)`. Includes when the played card is the AI's own — those calls are filtered inside `HardStrategy.on_card_played` by `position` check. EasyStrategy and MediumStrategy default to no-op.

## 6. Trick-state plumbing

`HardStrategy.pick_card` needs the current trick total in points. The multi-seat `_play_trick` already maintains `trick_order` (a list of `{position, card}` dicts) representing the in-flight trick. Pass it to AI strategies via `valid_actions["trick_so_far"]` — Task 12's path already passes `lead_suit`, `operator`, and `valid_cards`. `_compute_ai_action` reads `valid_actions["trick_so_far"]` and forwards it as the third positional arg to `seat._strategy.pick_card(play, lead_suit, trick_so_far)`.

This is a self-contained change in `_play_trick` (one extra key in the kwarg dict) and has zero protocol implications — `valid_actions` is internal to the AI dispatch.

## 7. HTTP API

```
POST /rooms/{code}/ai_difficulty
Body: {"position": "compe", "level": "hard"}
Headers: X-Requested-With: schieber

→ 200 {room_state}
→ 400 "unknown difficulty: {level}"      (level not in {easy,medium,hard})
→ 400 "seat is human, no AI difficulty"   (target seat has a human principal)
→ 400 "invalid position"                  (position not in POSITIONS)
→ 403 "not host"
→ 404 "room not found"
→ 409 "lobby only; state={state}"
```

On success, server broadcasts:
```json
{"type": "seat_changed", "seat": <_seat_to_dict>, "reason": "ai_difficulty"}
```

The `_seat_to_dict` helper (in `server.py` and `game_session.py`) is extended to include `ai_difficulty: str | None` (`None` for human seats).

## 8. Lobby UI

`ausbau/html5/lobby.html` and `lobby.js`:
- Each AI seat row gets a `<select>` next to the seat name with options `easy / medium / hard`. Disabled (read-only) for non-host viewers.
- Change handler POSTs `/rooms/{code}/ai_difficulty`. On success, the lobby re-renders from the broadcast `seat_changed`.
- Difficulty also surfaces in the seat-list rendering of `lobby.html` for read-only viewers (so spectators in the lobby see the AI configuration).

## 9. Error handling

- Endpoint validation per §7.
- HardStrategy `on_card_played` for an unknown card → log INFO, no-op (defensive).
- HardStrategy `pick_card` returns no candidate → raise `RuntimeError("HardStrategy: no valid card")`. Never silently swallow — surfaces upstream bugs.
- Invariant violation `seat.is_ai is True AND seat._strategy is None` → defensive rebuild via `make_strategy(seat.ai_difficulty or "medium", position)` with a logged warning. Never crash mid-trick.
- `make_strategy` rejects unknown difficulty with `ValueError`. The endpoint catches this and returns 400.

## 10. Testing

### 10.1 Per-strategy unit tests (`test_ai_strategies.py`)
- **EasyStrategy** (3): pick_trump returns one of 6 ops; pick_card returns a valid card; never schiebens.
- **MediumStrategy** (4): pick_trump returns farbe_lang result; pick_card lead = highest by point; pick_card follow = lowest; pick_trump never schiebens.
- **HardStrategy pick_trump** (5): commits when len≥4 ∧ Under-or-Nell; schiebens when allowed and weak; commits to highest-scored mode when forced post-schieben; tie-break order; weak-but-no-schieben fallback uses 6-mode score.
- **HardStrategy pick_card** (6): leading with a guaranteed-winner Ass plays it; leading with no winner plays lowest; following partner-wins dumps low; following opponent-wins beats cheaply; trump conservation downgrades trump play when trick is cheap; high-value trump steal when trick ≥18 points.
- **HardStrategy memory** (3): on_spiel_start populates the set; on_card_played removes a known card; on_card_played missing card no-ops with log.

### 10.2 Endpoint test (`test_ai_difficulty_endpoint.py`)
6 cases: 200 happy path + broadcast verification, 400 invalid level, 400 human seat, 400 invalid position, 403 not host, 409 mid-game, 404 no room.

### 10.3 Lifecycle test (`test_ai_difficulty_lifecycle.py`)
4 cases: `_strategy` rebuilt on lobby `/leave` of an AI seat; `_strategy` set to None on `/join`; mid-game AI takeover resets `ai_difficulty="medium"` AND rebuilds `_strategy`; `seat.ai_difficulty` is preserved across human-join-then-leave in lobby.

### 10.4 Integration extension (`test_e2e_4_humans.py` or sibling)
Add `test_e2e_mixed_difficulty_3_ai`: 1 human + 3 AIs, one each easy/medium/hard. Run a full game; assert it reaches `game_end`, no exceptions, all 3 AI seats had `_strategy` consulted at least once. Doesn't assert outcome (too stochastic).

### 10.5 Estimated total
~25 unit/integration tests added. Final test count: 285 → ~310.

## 11. Out of Scope

- Sub-project D (partner-aware AI, opponent-hand inference) — explicitly deferred per Q9.
- Minimax / Monte Carlo search.
- Tournament-style AI tuning, ELO, training data.
- Cross-spiel memory (memory clears at each `_run_spiel` start).
- Difficulty changes mid-game — locked at room state `playing`.
- Per-room default override (host could set "all AIs default to hard at room creation"). Q4 fixed default at `medium` regardless.
- Difficulty visible in spectator/game-end summaries — not surfaced.

## 12. Migration / compatibility

- Existing rooms have `Seat.ai_difficulty="medium"` and behave identically (MediumStrategy = today's heuristic). Zero behaviour change for anyone who doesn't touch the new endpoint.
- No DB schema changes (game data stays anonymous; room state is in-memory).
- No protocol breaking changes — only an additive `ai_difficulty` field on `_seat_to_dict`'s output.

## 13. Decomposition

Single sub-project, single spec, single plan. Estimate: 8–12 implementation tasks. Plan to follow.
