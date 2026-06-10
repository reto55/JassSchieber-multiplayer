---
name: schieber-game-rules
description: Authoritative Schieber (Swiss Jass) game rules reference — card point values per mode, trick-winning logic, Weis combinations, scoring, `Schieben` mechanic, team assignments, variant bonuses (trumpf_bock / match_bonus / stoeck). Read before implementing, modifying, or reviewing any game-logic code (`determine_trick_winner`, `trick_points`, `check_game_end`, `wiis`, `wiis_gleiche`, `describe_weis`, `_apply_match_bonus`, `_apply_stoeck`, `determine_trumpf`). Consult whenever card point totals or trick winners are in question. Reflects the implementation, not standard Schieber rulebook — code-vs-rulebook divergences are flagged inline. Applies to backend, QA, and reviewer agents.
---

# Schieber Game Rules

Swiss 4-player Jass variant. **This document reflects the implementation in this repo, not the standard rulebook.** Where the two differ, the code-as-ground-truth value is given and the divergence is noted (`⚠ rulebook-divergence`).

**Authority rule:** divergences are *intentional house rules* unless a marker explicitly says "future convergence work". Never change game-scoring behavior toward the standard rulebook without a user-approved plan document. When game-rule semantics change, update this skill **before** the code change lands (same skill-first discipline as `schieber-protocol`).

## Players & Teams

| Position | Key | Team |
|----------|-----|------|
| Süd | `comps` | SN (North-South) |
| Nord | `compn` | SN |
| Ost  | `compo` | OW (East-West) |
| West | `compe` | OW |

`folger` (next-to-act order, counterclockwise): `comps → compo → compn → compe → comps`.
`partner` (across the table): `comps↔compn`, `compo↔compe`.

Score accumulators: `point_sn`, `point_ow`. Default target: **1000** points (`end_game`).

## Deck

36 cards = 4 suits × 9 ranks.

| Suit (German) |
|---------------|
| Eicheln (acorns) |
| Rosen (roses) |
| Schellen (bells) |
| Schilten (shields) |

| Rank | `rank` index | Class |
|------|--------------|-------|
| Sechs (6)   | 1 | `Sechs` |
| Sieben (7)  | 2 | `Sieben` |
| Acht (8)    | 3 | `Acht` |
| Neun (9)    | 4 | `Neun` |
| Banner (10) | 5 | `Banner` |
| Under (Bube)| 6 | `Under` |
| Ober (Dame) | 7 | `Ober` |
| König       | 8 | `Koenig` |
| Ass         | 9 | `Ass` |

## Game Modes (`operator`)

Chosen by the round starter (or partner after `Schieben`):

| Mode | Meaning |
|------|---------|
| `Eicheln`, `Rosen`, `Schellen`, `Schilten` | Trumpf game — that suit is trump |
| `Oben` | No-trump, top-down (Ass high) |
| `Unten` | No-trump, bottom-up (Sechs high) |

## Card Attributes (per `Card` subclass in `Cards_refactored.py`)

Each card carries two independent things: **trick-rank attributes** (`oben`, `unten`, `trumpf`) used by `determine_trick_winner` to decide who wins, and **point-value attributes** (`woben`, `wunten`, `wtrumpf`, `wfarbe`) summed by `trick_points`.

### Trick-rank attributes (higher beats lower)

| Rank | `oben` | `unten` | `trumpf` |
|------|--------|---------|----------|
| Ass    | 9 | 1 | 16 |
| König  | 8 | 2 | 15 |
| Ober   | 7 | 3 | 14 |
| Under  | 6 | 4 | **18** |
| Banner | 5 | 5 | 13 |
| Neun   | 4 | 6 | **17** |
| Acht   | 3 | 7 | 12 |
| Sieben | 2 | 8 | 11 |
| Sechs  | 1 | 9 | 10 |

Trump-rank order (highest first): **Under > Neun > Ass > König > Ober > Banner > Acht > Sieben > Sechs**.

For non-trump cards inside a trump game, lead-suit comparison uses `card.rank` (1..9, Sechs=1, Ass=9), giving **Ass > König > Ober > Under > Banner > Neun > Acht > Sieben > Sechs**.

### Point-value attributes

| Rank | `wtrumpf` (trump suit, trump game) | `wfarbe` (non-trump suit, trump game) | `woben` (Oben) | `wunten` (Unten) |
|------|------|------|------|------|
| Ass    | 11 | 11 | 11 | 0 |
| König  | 4  | 4  | 4  | 4 |
| Ober   | 3  | 3  | 3  | 3 |
| Under  | **20** | 2 | 2 | 2 |
| Banner | 10 | 10 | 10 | 10 |
| Neun   | **14** | 0 | 0 | 0 |
| Acht   | 0  | 0  | **8** | 8 |
| Sieben | 0  | 0  | 0  | 0 |
| Sechs  | 0  | 0  | 0  | **11** |

> ⚠ **rulebook-divergence — Acht in Oben.** Standard Schieber gives Acht=0 in Obenabe (per-suit total 30, deck 120). This code has `woben=8` for Acht (per-suit 38, deck 152), making Oben totals match Unten. Reflects implementation in `Cards_refactored.py::Acht`. If you change this, update `trick_points` test fixtures.

### Per-deck totals (sanity)

| Mode | Per-suit | Whole deck |
|------|----------|------------|
| Trump game | 62 (trump suit) + 30×3 (off-suits) | 152 |
| Oben  | 38 (because of code's Acht=8) | 152 |
| Unten | 38 | 152 |

## Trick-Winning Logic — `ausbau/game_session.py::determine_trick_winner`

`strength(card)` per mode:

| Mode | Trump card | Lead-suit card | Other |
|------|-----------|----------------|-------|
| Trump (`operator ∈ SUITS`) | `(2, card.trumpf)` | `(1, card.rank)` | `(0, 0)` |
| `Oben` | n/a | `(1, card.oben)`   | `(0, 0)` |
| `Unten`| n/a | `(1, card.unten)`  | `(0, 0)` |

Highest tuple wins. Tuple ordering means trumps always beat off-suit (group 2 vs 1). **Lead suit** = suit of the card the leader played.

## Following Suit — `ausbau/game_session.py::get_valid_cards`

Signature: `get_valid_cards(hand, lead_suit, operator, trick_so_far=None)`.
`trick_so_far` is the list of cards already played this trick — accepted as
CODE strings, `Card`s, or the engine's `{"position","card"}` dicts (`card` =
code). It is consulted only in trump modes, to enforce no-undertrumping.

### Trump modes (`operator ∈ {Eicheln, Rosen, Schellen, Schilten}`)

- **Leading** (`lead_suit is None`): any card.
- **Trump led** (`lead_suit == operator`):
  - No trump in hand → any card (can't follow).
  - **Under-holdback (house rule, implemented):** if your *only* trump is the
    trump *Under* (Bauer/Jack), you may play **any** card — the Under is never
    forced. If you hold a non-Under trump too, you must follow with a trump
    (Under stays optional among them).
  - Otherwise → must follow with a trump.
- **Non-trump led** (`lead_suit != operator`):
  1. **Trump always playable (house rule, implemented):** you may always trump
     in, even when you could follow the led suit — subject to no-undertrumping.
  2. **No undertrumping (house rule, implemented):** once a trump sits in the
     trick, any further trump you play must be **strictly higher** (by
     `card.trumpf`) than the highest trump already played. *Exception:* if your
     entire hand is trumps (no non-trump card to discard), you may undertrump
     (you are forced to play a trump). With any non-trump card in hand you may
     not undertrump — discard a non-trump or overtrump instead.
  3. If you have no lead-suit card, you may also discard any non-trump card.

The valid set is `follow ∪ allowed_trumps` (`+ non_trump discards` when you
can't follow). `allowed_trumps` = trumps strictly above the highest played
trump, or all your trumps if no trump played yet / your whole hand is trumps.

### No-trump modes (`operator ∈ {Oben, Unten}`)

Plain follow-suit: if you hold a lead-suit card you must play one; otherwise
any card. The three trump house rules above do **not** apply.

## Schieben — `_trump_phase`

Round starter (`play.first`) may pass trump choice to the across-the-table partner:

- Once per round only (`schieben_used` flag, `schieben_allowed=False` after pass).
- Partner may not schieben back; must pick a real `operator` ∈ `TRUMP_OPTIONS`.
- `play.first` (lead seat) is **not** changed — only the trump-chooser shifts.
- Partner pairing: `compo↔compe`, `compn↔comps` (see `_partner_of`).

## Weis (Meld) — `wiis`, `wiis_gleiche`, `describe_weis`, `_weis_phase`

Server detects eligible Weis from each hand after trump is known. Each seat is asked privately whether to announce.

### Patterns and points (per `describe_weis` SCORE_MAP)

| Combination | Detected by | Points |
|-------------|-------------|--------|
| **Dreier** — 3 in same suit, consecutive by `oben`-rank (6-7-8-9-B-U-O-K-A) | `wiis` | 20 |
| **Vierter** — 4 in same suit, consecutive | `wiis` | 50 |
| **`{n}er`** — 5+ consecutive in same suit | `wiis` | **100 (flat)** |
| **Viererle** — same `trumpf` value across all 4 suits (i.e. four-of-a-kind by rank) | `wiis_gleiche` | **100 (flat, regardless of which rank)** |

> ⚠ **rulebook-divergence — Weis values.** Standard Schieber scales sequences (6er=150, 7er=200, …) and gives Vier-Under=200, Vier-Neun=150, Vier-A/K/O=100. This code flattens all 5+ sequences and all four-of-a-kind to 100. Lives in `describe_weis::SCORE_MAP`.

### Sequence detection details

`wiis` sorts `card.oben` ascending per suit, walks once accumulating consecutive run, recurses on tail if first run too short. Only one sequence per suit may be reported. Sequences are by **face-card ranking** (`oben`), **never** trump-rank order — even in a trump game.

### Resolution — `_weis_phase` lines ~988–1001

Per-team **sum** of declared Weis points. Higher sum wins; that team adds its sum to the running score. Equal sums (including 0–0) → no team scores.

> ⚠ **rulebook-divergence — Strongest-Weis tiebreak.** Standard Schieber compares only the strongest single Weis between teams (length, then top card; Vier-Under absolute trump). This code uses sum-of-points, with no length / top-card tiebreak. Code comment in `_weis_phase` explicitly notes this is a Task 11 simplification.

Broadcast: `weis_resolution { winning_team: 'sn' | 'ow' | 'tie', weis_by_position: {...} }`. AI seats auto-announce all eligible Weis.

## Stöck — `detect_stock`, `_apply_stoeck` (variant-gated)

Holding **König + Ober of the trump suit** in your starting hand: +20 to your team. Variant `stoeck` must be enabled. No-trump rounds (`Oben`/`Unten`) never award Stöck. Multiple seats can each award their own +20 (rare with one deck, but the code supports it). Applied **before** Weis phase, in `_run_spiel` step 3. The base value is then multiplied by the mode multiplier (see Multiplikator below).

> ⚠ **rulebook-divergence — Stöck auto-award (intentional house rule).** Standard Schieber requires the holder to *announce* Stöck when playing the second of the two cards — silence forfeits it, and the announcement timing matters for reaching the target mid-round. This code auto-detects Stöck from the starting hand and credits it before any card is played; there is no announcement and no forfeiture.

## Multiplikator — `_mode_multiplier(operator, *, trumpf_bock=False)`

Single source of truth for the per-mode score multiplier. Every score-bearing site routes through this helper.

| Operator | Multiplier | + `trumpf_bock` |
|----------|-----------|-----------------|
| `Eicheln`, `Rosen` | ×1 | ×5 |
| `Schellen`, `Schilten` | ×2 | ×10 |
| `Oben`, `Unten` | ×3 | ×3 (bock has no effect in no-trump) |

Applied at:
- `trick_points` — every trick total (uses `trumpf_bock`)
- `describe_weis` — Weis points (Dreier 20, Vierter 50, Viererle 100; ignores `trumpf_bock`)
- `_apply_stoeck` — Stöck +20 (ignores `trumpf_bock`)
- `_run_spiel` — last-trick +5 bonus (ignores `trumpf_bock`)

`_apply_match_bonus` is **not** multiplied — the +100 match bonus is a flat value.

## Variants — `ausbau/room.py::Variant`

| Flag | Effect | Where applied |
|------|--------|---------------|
| `trumpf_bock` | Stacks ×5 on top of base mode multiplier in trump-mode rounds (so Eicheln/Rosen → ×5, Schellen/Schilten → ×10). Does **not** affect Weis, Stöck, or last-trick bonus. No effect in Oben/Unten. | `_mode_multiplier`, applied in `trick_points` |
| `match_bonus` | If one team wins all 9 tricks of a spiel: **+100** to that team (flat, not multiplied). Mixed winners or fewer than 9 tricks recorded → 0. | `_apply_match_bonus` |
| `stoeck` | König + Ober of trump in a hand → +20 (×mode multiplier) to that team. Trump-mode rounds only. | `_apply_stoeck` |

## Per-Spiel Scoring Flow — `_run_spiel`

In order:

1. `game_start` broadcast (per-seat redacted).
2. Trump phase (with optional `Schieben`).
3. **Stöck** (variant-gated, trump rounds only) — adds to `point_sn` / `point_ow`.
4. **Weis phase** — winning team's sum added.
5. **9 tricks** via `_play_trick` loop:
   - Winner of each trick leads the next; `play.first` updated.
   - Trick points = `trick_points(trick, operator, trumpf_bock=variant.trumpf_bock)`, added to winner's team total. Already multiplied by mode multiplier (and ×5 if `trumpf_bock` in trump mode).
   - **Last trick (#9): +5 × mode multiplier to winner's team** (always; not variant-gated). Bock does NOT apply.
6. **Match bonus** (variant-gated, flat): +100 if all 9 went to one team. Not multiplied.
7. `spiel_end` broadcast with deltas.

After every spiel, `start_game` checks `check_game_end(point_sn, point_ow, end_game)`. On true, computes winner inline (`sn` / `ow` / `tie`) and broadcasts `game_end`.

> ⚠ **rulebook-divergence — game-end timing (FUTURE CONVERGENCE WORK, not a house rule).** Standard Schieber ends the *instant* a team reaches the target; this code checks only between spiels, so the full spiel always plays out and a `'tie'` outcome is possible (both teams crossing the target in the same spiel) — standard play cannot tie. Agreed target behavior (2026-06-10): check after **every scoring event** in order (Stöck award → Weis resolution → each trick); first team to cross wins immediately, spiel aborts mid-play, `'tie'` disappears. Requires its own plan document before implementation — do not converge ad hoc.

## Trump Determination (AI / starter heuristic) — `determine_trumpf`

Used by `Play._setup_round` to seed the round's `operator` field for AI starters. Returns `'Schieben'`, a suit name, `'Oben'`, or `'Unten'` based on longest sequence length and sum of `card.oben` values in that suit. Pure heuristic; not authoritative game rules. AI strategies (sub-project C) override this via `ausbau/ai_strategies.py`.

`determine_trumpf_after_schieben` exists as a separate code path for the partner case but is mostly a copy of `determine_trumpf` with the `Schieben` return replaced by `longest_suit`.

## Key Code Locations

| Concept | File | Function |
|---------|------|----------|
| Card subclasses with point/rank attributes | `Cards_refactored.py` | `Ass`, `Koenig`, `Ober`, `Under`, `Banner`, `Neun`, `Acht`, `Sieben`, `Sechs` |
| Trump-pick heuristic | `Cards_refactored.py` | `determine_trumpf`, `determine_trumpf_after_schieben` |
| Weis sequence detection | `Cards_refactored.py` | `wiis`, `calculate_wiis` |
| Weis four-of-a-kind detection | `Cards_refactored.py` | `wiis_gleiche` |
| Weis description / point map | `ausbau/game_session.py` | `describe_weis` |
| Trick-winner | `ausbau/game_session.py` | `determine_trick_winner` |
| Trick-points sum (incl. `trumpf_bock` ×5) | `ausbau/game_session.py` | `trick_points` |
| Valid-cards (follow-suit + Under-holdback + no-undertrump house rules) | `ausbau/game_session.py` | `get_valid_cards` |
| Naive AI card pick | `ausbau/game_session.py` | `ai_select_card` |
| Stöck detect / apply | `ausbau/game_session.py` | `detect_stock`, `_apply_stoeck` |
| Match bonus apply | `ausbau/game_session.py` | `_apply_match_bonus` |
| Trump phase + Schieben | `ausbau/game_session.py` | `_trump_phase`, `_partner_of` |
| Weis phase | `ausbau/game_session.py` | `_weis_phase` |
| Per-spiel orchestration (Stöck → Weis → 9 tricks → match) | `ausbau/game_session.py` | `_run_spiel` |
| Game-end check | `utils/game_utils.py` | `check_game_end` |
| Game loop / winner broadcast | `ausbau/game_session.py` | `start_game` |

> Legacy/dead code: `utils/game_utils.py::calculate_points`, `get_winner`, `get_next_player` — referenced nowhere in the live HTML5 path; references `card.trumpf_value` etc. that no longer exist on `Card`. Do not call.

## Common Pitfalls

- **`oben` / `unten` / `trumpf` are trick-rank ordinals, not points.** Under has `trumpf=18` (highest trump rank) and `wtrumpf=20` (point value). Distinct attributes; do not conflate.
- **Any trump may break follow-suit** in this code (house rule, intentional). Off-suit lead → trumping in is always legal, subject to no-undertrumping.
- **No-undertrumping enforced (house rule).** On a non-trump lead, once a trump is in the trick a further trump must be *strictly higher* by `card.trumpf` than the highest played. Exception: an all-trump hand (no non-trump to discard) may undertrump (forced). `get_valid_cards` reads `trick_so_far` to apply this.
- **Under-holdback enforced (house rule).** Trump led + your only trump is the trump Under → any card is legal; the Under is never forced.
- **Weis uses `oben`-order for sequences**, even when the round is a trump game. So in a Schellen-trump round, U-9-A-K-O (trump-order) is **not** a valid Weis sequence; B-U-O-K-A (oben-order) is.
- **Weis four-of-a-kind = flat 100.** Trump-Under quad is not 200 in this code.
- **Acht in Oben = 8 points** (code), not 0 (rulebook). Tests assume 8.
- **Last-trick bonus = +5**, always, not variant-gated. Match bonus = +100 separately, variant-gated.
- **`Schieben` only changes the trump-chooser, not `play.first`.** The lead seat is fixed by spiel number.
- **Stöck applies *before* Weis** in `_run_spiel`; if you reorder steps, broadcast deltas (`spiel_end.weis_added`) will mis-attribute.
- **Game end is checked between spiels only** — `'tie'` exists solely because of this. Mid-round termination is scheduled future work (see ⚠ in Per-Spiel Scoring Flow), not something to "fix" in passing.
