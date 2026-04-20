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

**GameState class** (`Cards_refactored.py`) replaces all global variables. Holds player IDs (`spieler_id`), scoring arrays (`weis`, `weis4`, `spsp`), and the `schieber` session object.

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
