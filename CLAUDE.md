# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python implementation of **Schieber**, a classic Swiss four-player card game. The repo is mid-refactoring: original monolithic code is being split into modular utilities with proper OOP structure and tests.

## Commands

```bash
# Run the game
python play.py

# Run all tests
python run_tests.py

# Run a single test file
python -m unittest tests/test_card_utils.py
python -m unittest tests/test_game_utils.py
python -m unittest tests/test_db_utils.py
python -m unittest tests/test_integration.py
```

No external dependencies — uses only Python stdlib (`sqlite3`, `datetime`, `enum`, `collections`, `random`, `json`, `time`).

## Architecture

The codebase has two parallel tracks: **legacy** (original code) and **refactored** (in-progress):

```
play.py                          ← CLI entry point
deal_cards_refactored.py         ← GameController (game loop, round management)
Cards_refactored.py              ← Core data structures (Card, Deck, Hand, Players, GameState)
utils/
  card_utils.py                  ← Card sorting and hand manipulation
  game_utils.py                  ← Scoring, winner logic, game duration
  db_utils.py                    ← SQLite CRUD operations
ausbau/
  database_manager.py            ← OOP DatabaseManager with context manager
  db_adapter.py                  ← Compatibility shim for legacy code
  db_migration.py                ← Data migration tool
tests/                           ← Unit and integration tests
```

Legacy files (`Cards.py`, `deal_cards.py`, `imports.py`, `ausbau/schieber*.py`) are kept for reference. The `ausbau/` dir contains in-progress database improvements.

## Key Design Decisions

**Static card table** (`Cards_refactored.py` `CARD_ATTRIBUTES`): 1-based dict mapping rank → `[name, rank, oben, unten, trumpf, w_oben, w_unten, w_trumpf, w_farbe]`. The `Play` class populates its per-suit `farben` grid from it. (Historical note: this table used to live on a `GameState` singleton along with per-session scoring arrays; those arrays were never actually read, so the singleton was removed — the table stands alone as a module constant.)

**Card hierarchy**: `Card` base class with rank subclasses (`Ass`, `Koenig`, `Ober`, `Under`, `Banner`, `Neun`, `Acht`, `Sieben`, `Sechs`). Each subclass defines point values for the four game modes: `oben` (trick value normal), `unten` (trick value reversed), `trumpf` (trump value), and special attributes.

**Game modes**: `operator` field in each round is one of `'Eicheln'`, `'Rosen'`, `'Schellen'`, `'Schilten'` (trump suit) or `'Oben'`/`'Unten'` (no-trump modes).

**Teams**: North-South (`pointSN`) vs East-West (`pointOW`). Players are `compo` (O/West), `compn` (N/North), `compe` (E/East), `comps` (S/South).

**`farbe_lang()`** in `card_utils.py` determines a player's longest suit with priority order: Schilten > Schellen > Eicheln > Rosen.

**`max_game()`** in `game_utils.py` contains the core trick-winning logic — which card beats which based on the current trump/mode. This is the most complex function in the codebase.

## Database Schema

SQLite database (`schieber.db`) with tables: `schieber` (sessions), `game`, `play` (individual turns), `spieler` (players), `stich` (tricks), `wys`/`wwys` (special scoring).

## Refactoring Status

**Done:**
- `Cards_refactored.py` with `GameState`, proper Card subclasses, `Hand`, `Players`
- `utils/` package with `card_utils`, `game_utils`, `db_utils`
- `GameController` in `deal_cards_refactored.py`
- `ausbau/database_manager.py` with OOP database layer
- Test suite in `tests/`

**Still needed** (per original plan):
- Eliminate remaining global variables
- Standardize German/English naming
- Add error handling
- Improve `max_game()` readability

## Harness: Schieber

**Goal:** Build, verify, and finish the Schieber HTML5 game (plan in `docs/superpowers/plans/2026-04-13-schieber-html5-frontend.md`) via a coordinated agent team.

**Trigger:** For any Schieber implementation / testing / fixing / refactoring work, invoke the `schieber-build` skill. The skill orchestrates `schieber-backend`, `schieber-frontend`, `schieber-qa`, `schieber-reviewer`. Pure lookup questions (game rules, WebSocket field meaning) can be answered directly by reading the `schieber-game-rules` / `schieber-protocol` skill.

**Variable conventions added by harness:**
- Shared intermediate artifacts live in `_workspace/` (gitignored via patterns like `_workspace/`).
- Protocol changes go to `.claude/skills/schieber-protocol/SKILL.md` BEFORE code changes.
- Game-rule questions resolve to `.claude/skills/schieber-game-rules/SKILL.md`.

**Variation ledger:**
| Date | Change | Target | Reason |
|------|--------|--------|--------|
| 2026-04-20 | Initial harness (backend, frontend, qa, reviewer agents; schieber-build orchestrator; schieber-protocol and schieber-game-rules skills) | whole harness | Finish 15-task HTML5 plan with coordinated roles and cross-boundary QA |
| 2026-04-20 | Phase 0 now compares commit log with plan checkboxes | schieber-build | Plan boxes drifted — code committed for Tasks 1–14 without ticking; orchestrator was misled into treating completed work as unstarted |
| 2026-04-20 | Parallel subagents declared valid default for Phase 2 | schieber-build | TeamCreate/SendMessage added overhead with no benefit when the protocol skill is authoritative |
| 2026-04-20 | Reviewer phase skipped for skill-only, tooling-only, and orchestrator-inflight batches | schieber-build | Batch B and D did not benefit from reviewer; running it would have added cycle time with no findings |
| 2026-04-20 | Orchestrator may fix trivial QA gaps in-place | schieber-build | D8 leftover (game_end winner_team normalization) was a two-line fix; re-dispatch for that would have been pure overhead |
| 2026-04-20 | Audit-first mode added to Phase 0 | schieber-build | Tasks 1–14 already committed; QA should run before any new build to establish baseline |
| 2026-04-20 | Defensive staging rule in Phase 5 | schieber-build | Pre-staged user work (schieber.txt) got swept into harness commit; needed soft reset to split |
| 2026-04-20 | QA agent distinguishes DRIFT vs SKILL_GAP explicitly | schieber-qa | Initial skill was aspirational from the plan, not factual from code; Batch 1 found 4 gaps that needed skill updates, not code fixes |
| 2026-04-20 | Protocol-skill sanity check added to Phase 0 | schieber-build | Orchestrator must verify the skill against actual `send_json`/`receive_json` sites before trusting it as ground truth |
