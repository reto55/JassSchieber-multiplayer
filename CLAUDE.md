# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python implementation of **Schieber**, a classic Swiss four-player card game. The repo is mid-refactoring: original monolithic code is being split into modular utilities with proper OOP structure and tests.

## Commands

```bash
# Run the HTML5 game server (set required env first; copy from .env.example)
python -m uvicorn ausbau.server:app --reload --port 8765
# open http://localhost:8765

# Run all tests
python run_tests.py

# Run a single test file
python -m pytest tests/test_card_utils.py
python -m pytest tests/test_game_utils.py
python -m pytest tests/test_db_utils.py
python -m pytest tests/test_game_session.py
python -m pytest tests/test_integration.py

# Run only the auth test suite
python -m pytest tests/auth/
```

Auth requires env vars (see `.env.example`): `SECRET_KEY`, `BASE_URL`, `SMTP_USER`, `SMTP_APP_PASSWORD`, `MAIL_BACKEND`, `ADMIN_BOOTSTRAP_EMAIL`. Tests monkeypatch these; `MAIL_BACKEND=console` sends mail to stdout.

Python 3.9+ with `fastapi` + `uvicorn` for the HTML5 server; `pytest` for tests; otherwise stdlib only (`sqlite3`, `datetime`, `enum`, `collections`, `random`, `json`, `asyncio`).

## Architecture

```
Cards_refactored.py              ← Core data (Card subclasses, Deck, Hand, Players, Play)
utils/
  card_utils.py                  ← Card sorting and hand manipulation
  game_utils.py                  ← Scoring, winner logic, game duration
  db_utils.py                    ← SQLite CRUD operations
ausbau/
  server.py                      ← FastAPI app; /ws/{code} WebSocket endpoint, /rooms/* HTTP
  room.py                        ← Room registry, Seat/Spectator/Variant data, reaper task
  game_session.py                ← GameSession (multi-seat state machine + game-loop)
  html5/                         ← game.html, lobby.html, js + css + Jasskarten.png sprite sheet
  database_manager.py            ← OOP DatabaseManager with context manager
  db_adapter.py                  ← Compatibility shim for legacy DB code
  db_migration.py                ← Data migration tool
tests/                           ← Unit and integration tests
  multiplayer/                   ← Multi-WS / room / lobby / variant / e2e tests
docs/superpowers/plans/          ← HTML5 frontend plan (done), accounts plan (done), multiplayer Part 1+2 (done)
.claude/{agents,skills}/         ← Schieber build harness (see "Harness: Schieber")
```

The live game path is HTML5: browser ↔ `ausbau/server.py /ws/{code}` ↔ `GameSession.start_game` → `_run_spiel` → `_trump_phase` / `_weis_phase` / `_play_trick` ↔ `Play` / `Cards_refactored.py`. No CLI.

## Key Design Decisions

**Static card table** (`Cards_refactored.py` `CARD_ATTRIBUTES`): 1-based dict mapping rank → `[name, rank, oben, unten, trumpf, w_oben, w_unten, w_trumpf, w_farbe]`. The `Play` class populates its per-suit `farben` grid from it. (Historical note: this table used to live on a `GameState` singleton along with per-session scoring arrays; those arrays were never actually read, so the singleton was removed — the table stands alone as a module constant.)

**Card hierarchy**: `Card` base class with rank subclasses (`Ass`, `Koenig`, `Ober`, `Under`, `Banner`, `Neun`, `Acht`, `Sieben`, `Sechs`). Each subclass defines point values for the four game modes: `oben` (trick value normal), `unten` (trick value reversed), `trumpf` (trump value), and special attributes.

**Game modes**: `operator` field in each round is one of `'Eicheln'`, `'Rosen'`, `'Schellen'`, `'Schilten'` (trump suit) or `'Oben'`/`'Unten'` (no-trump modes).

**Teams**: North-South (`point_sn`) vs East-West (`point_ow`) at the Python layer; the SQL columns remain `pointSN` / `pointOW` (schema). Players are `compo` (O/West), `compn` (N/North), `compe` (E/East), `comps` (S/South).

**`farbe_lang()`** in `card_utils.py` determines a player's longest suit with priority order: Schilten > Schellen > Eicheln > Rosen.

**Trick-winner logic** lives in `ausbau/game_session.py::determine_trick_winner` — the live HTML5 path. Rules codified in the `schieber-game-rules` skill.

**Multiplayer model**: each room is one `GameSession` keyed by 6-char code in `ausbau/room.py::ROOMS`. Per-seat state on `Seat` (principal, websocket, is_ai, reconnect_deadline, connected_since, per-seat `incoming` queue, `state_event`). Mid-game, the four phase loops (`_trump_phase`, `_weis_phase`, `_play_trick`) await per-seat input via `_await_seat_action(position, valid_actions)`. AI seats compute synchronously through `_compute_ai_action` (`farbe_lang` for trump, `ai_select_card` for play). Disconnect triggers a 60s reconnect timer; on timeout, seat flips to AI but `principal` is retained so the original human can reclaim. Replay buffer (`_completed_tricks`, capped at 3) feeds `room_resume.missed_tricks` for reconnecting clients. Per-room reaper removes finished/idle rooms after 5 min.

## Database Schema

SQLite database (`schieber.db`) with tables: `schieber` (sessions), `game`, `play` (individual turns), `spieler` (players), `stich` (tricks), `wys`/`wwys` (special scoring).

## Refactoring Status

**Done:**
- `Cards_refactored.py` with proper Card subclasses, `Hand`, `Players`, `Play`
- `utils/` package with `card_utils`, `game_utils`, `db_utils`
- `ausbau/database_manager.py` with OOP database layer
- `ausbau/game_session.py` + `ausbau/server.py` (HTML5 WebSocket game loop, plan in `docs/superpowers/plans/2026-04-13-schieber-html5-frontend.md` fully done)
- Test suite in `tests/`
- `GameState` singleton removed (E2), `max_game` readability pass (E1), naming standardisation (E3), live-path error handling (E4), legacy CLI (`play.py`, `deal_cards_refactored.py`, `GAME_FLOW_README.md`) deleted (E5).
- **Sub-project B — User accounts** (this branch). Spec: `docs/superpowers/specs/2026-04-28-schieber-accounts-design.md`. Plan: `docs/superpowers/plans/2026-04-28-schieber-accounts.md`. New package `frontend/auth/` provides email-and-password signup/login, soft email verification, password reset, change-email/password, account delete (soft, with 30-day tombstone) and export, admin tools (bootstrap-by-env, ban/unban/promote/demote/force-verify, audit log), per-IP rate limiting (slowapi), and signed guest cookies for anonymous play. WS handshake reads cookies and resolves to `User` or `Guest` principal, used for log labelling. Auth tables live in their own `auth.db` (async SQLAlchemy + aiosqlite); game tables stay raw `sqlite3`. Server entry: `python -m uvicorn ausbau.server:app --reload --port 8765` (env vars per `.env.example`).
- **Sub-project A — Networked multiplayer** (this branch). Spec: `docs/superpowers/specs/2026-04-28-schieber-multiplayer-design.md`. Plans: `docs/superpowers/plans/2026-04-28-schieber-multiplayer.md` (Part 1: Tasks 0–6) + `2026-04-28-schieber-multiplayer-part2.md` (Part 2: Tasks 7–25). New module `ausbau/room.py` adds the room registry (`ROOMS`), `Seat`, `Spectator`, `Variant`, code generation, and the reaper. `GameSession` is now multi-seat: `_trump_phase`, `_weis_phase`, `_play_trick` send per-seat redacted prompts (`trump_request`, `weis_request`, `play_request` to the active seat only) and broadcast `*_pending` / `*_chosen` / `card_played` / `trick_end` to others. Disconnect → 60s grace → AI takeover (principal retained for reclaim). Replay buffer (last 3 tricks) feeds `room_resume`. Variants `trumpf_bock` (5x trump trick), `match_bonus` (+100 for 9-of-9), `stoeck` (+20 K+O of trump). HTTP surface: `POST /rooms`, `GET /rooms/{code}`, `GET /rooms/mine`, `POST /rooms/{code}/{join,leave,spectate,leave-spectator,start,seat}`. WS at `/ws/{code}`. Lobby UI at `/lobby?code=…`. Host-only: start, kick (lobby-only). Mid-game seat swap via two-step accept, commit at trick boundary, 30s TTL.

- **Sub-project C — AI difficulty** (this branch). Spec: `docs/superpowers/specs/2026-04-29-schieber-ai-difficulty-design.md`. Plan: `docs/superpowers/plans/2026-04-30-schieber-ai-difficulty.md`. New module `ausbau/ai_strategies.py` defines `AIStrategy` ABC + `EasyStrategy` (uniform random) / `MediumStrategy` (today's heuristic) / `HardStrategy` (per-spiel card tracking + trump conservation + smarter trump pick incl. schieben + trump-drawing "Trumpf ziehen" leading logic). Per-seat via `Seat.ai_difficulty`. Host-only `POST /rooms/{code}/ai_difficulty` endpoint, lobby-only. Lobby UI shows a dropdown per AI seat. AI takeover (mid-game disconnect) resets the seat's difficulty to `medium`. **HardStrategy trump-drawing** (`_lead`): while leading in a trump mode, lead the highest trump to pull opponents' trumps; `on_card_played` reconstructs each trick (4-card reset) to flag each opponent void in trump on a trump-led non-trump discard (partner never flagged); once both opponents are void — or no trump is outstanding outside the AI's hand at all — stop opening with trump: cash the highest-point guaranteed non-trump winner (trump winners only when no trump is outstanding, since outstanding trumps can only sit in partner's hand), else lead a non-trump suit an opponent has shown (so partner trumps in), else lowest non-trump card. **Tier-1 lone-trump stop** (sub-project C, no new tracking state): rule A is also suppressed when EXACTLY ONE trump is outstanding outside the AI's hand AND the AI does not hold the boss (highest-by-`.trumpf`) trump — leading there can only lose the trick (opponent holds the lone trump) or waste partner's trump; with 2+ outstanding the AI keeps drawing into the boss to flush it, and with the boss in hand it still leads it. Uses only `_remaining_by_suit[operator]` + own hand; post-stop reuses the existing fallthrough. Known residual (deferred to **sub-project D**): the cashed non-trump winner is ruff-blind, so the lone outstanding opponent trump could still ruff it — accepted (better EV than leading trump); a ruff-aware unruffable-winner predicate + exact-hand reconstruction is sub-project D Tier-2 work. Tests in `tests/multiplayer/test_ai_hard_trump_draw.py`. **Sub-project D (PIMC):** in trump modes the Hard AI now chooses its LEAD via a Perfect-Information Monte Carlo engine (`ausbau/ai_pimc.py`): it samples deals consistent with tracked hand sizes / all-suit voids / trump Under-holdback, rolls each out to spiel end with the `ai_select_card` heuristic policy, and leads the highest expected-value card. Synchronous and time-boxed (`PIMC_DEADLINE_S`); on timeout / too-few-samples / engine error it falls back to the heuristic `_lead_heuristic`, which retains the Tier-1 lone-trump lack-boss stop. Gated by `HardStrategy._pimc_enabled` (default on). Spec `docs/superpowers/specs/2026-06-15-schieber-ai-pimc-design.md`, plan `docs/superpowers/plans/2026-06-15-schieber-ai-pimc.md`. Tests in `tests/multiplayer/test_ai_pimc.py`. Not a game-rules change.

**All three sub-projects (A multiplayer, B accounts, C AI difficulty) are done.** Sub-project D (stronger AI) is underway: Tier-1 (sound lone-trump stop) shipped; Tier-2 PIMC leading engine (`ausbau/ai_pimc.py`) implemented. Remaining future work is variant expansion (§7.7) and deeper AI (partner-inference signalling, minimax / double-dummy evaluator).

## Harness: Schieber

**Goal:** Build, verify, and finish the Schieber HTML5 game (plan in `docs/superpowers/plans/2026-04-13-schieber-html5-frontend.md`) via a coordinated agent team.

**Trigger:** For any Schieber implementation / testing / fixing / refactoring work, invoke the `schieber-build` skill. The skill orchestrates `schieber-backend`, `schieber-frontend`, `schieber-qa`, `schieber-reviewer`. Pure lookup questions (game rules, WebSocket field meaning) can be answered directly by reading the `schieber-game-rules` / `schieber-protocol` skill.

**Variable conventions added by harness:**
- Shared intermediate artifacts live in `_workspace/` (gitignored via patterns like `_workspace/`).
- Protocol changes go to `.claude/skills/schieber-protocol/SKILL.md` BEFORE code changes.
- Game-rule questions resolve to `.claude/skills/schieber-game-rules/SKILL.md`.
- Game-rule semantic changes (`get_valid_cards`, `trick_points`, `determine_trick_winner`, Weis, Stöck, multipliers, game end) go to `.claude/skills/schieber-game-rules/SKILL.md` BEFORE code changes; QA treats mismatches as DRIFT vs SKILL_GAP, same as protocol. Rulebook divergences in that skill are intentional house rules unless marked "future convergence work".

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
| 2026-06-10 | Game-rules skill gets skill-first sync discipline + authority rule (divergences = house rules; game-end timing marked future convergence work) | schieber-game-rules | /grill-me session: prevent agents from "fixing" intentional house rules toward the rulebook, and from converging game-end timing ad hoc without a plan |
| 2026-06-15 | Phase 3 cross-boundary QA may be skipped for all-backend, no-protocol batches (run reviewer instead) | schieber-build | Sub-project D PIMC build: QA's distinct value is `send_json`/`receive_json` shape agreement; on internal AI-strategy work nothing crosses the boundary and the backend already runs the full suite, so QA only re-runs tests. Reviewer is the meaningful gate there. |

<!-- okf-rs:begin -->
@AGENTS.md
<!-- okf-rs:end -->
