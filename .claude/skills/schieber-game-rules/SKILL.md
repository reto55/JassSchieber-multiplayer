---
name: schieber-game-rules
description: Authoritative Schieber (Swiss Jass) game rules reference — card point values per mode, trick-winning logic, Weis combinations, scoring, `Schieben` mechanic, team assignments. Read before implementing, modifying, or reviewing any game-logic code (`max_game`, `check_game_end`, `wiis`, `determine_trumpf`, scoring arrays). Consult whenever card point totals or trick winners are in question. Applies to backend, QA, and reviewer agents.
---

# Schieber Game Rules

Swiss 4-player Jass variant. Reference for implementation correctness.

## Players & Teams

| Position | Key | Team |
|----------|-----|------|
| Süd (human) | `comps` | SN (North-South) |
| Nord | `compn` | SN |
| Ost | `compo` | OW (East-West) |
| West | `compe` | OW |

Scoring arrays: `point_sn`, `point_ow`. Target score: **1000** points.

## Deck

36 cards, 4 suits × 9 ranks.

| Suit (German) |
|---------------|
| Eicheln (acorns) |
| Rosen (roses) |
| Schellen (bells) |
| Schilten (shields) |

| Rank | Short |
|------|-------|
| Ass | A |
| König | K |
| Ober (Dame) | O |
| Under (Bube) | U |
| Banner (10) | B |
| Neun | 9 |
| Acht | 8 |
| Sieben | 7 |
| Sechs | 6 |

## Game Modes (`operator`)

Chosen by starter (or opposite after `Schieben`):

| Mode | Meaning |
|------|---------|
| `Eicheln`, `Rosen`, `Schellen`, `Schilten` | Trumpf game — that suit is trump |
| `Oben` | No-trump, high cards score (Ass high) |
| `Unten` | No-trump, low cards score (Sechs high) |

## Card Point Values

### Trumpf mode (the chosen suit)

In trump suit:
| Rank | Points |
|------|--------|
| Under (Bube) | 20 |
| Neun | 14 |
| Ass | 11 |
| König | 4 |
| Ober | 3 |
| Banner | 10 |
| Acht, Sieben, Sechs | 0 |

In non-trump suits during a trump game:
| Rank | Points |
|------|--------|
| Ass | 11 |
| König | 4 |
| Ober | 3 |
| Under | 2 |
| Banner | 10 |
| Neun, Acht, Sieben, Sechs | 0 |

### `Oben` mode (top-down, no trump)

| Rank | Points |
|------|--------|
| Ass | 11 |
| König | 4 |
| Ober | 3 |
| Under | 2 |
| Banner | 10 |
| Neun, Acht, Sieben | 0 |
| Sechs | 0 |

Ass beats König beats Ober beats Under beats Banner beats Neun... No trump.

### `Unten` mode (bottom-up, no trump)

| Rank | Points |
|------|--------|
| Sechs | 11 |
| Sieben | 0 |
| Acht | 8 |
| Neun | 0 |
| Banner | 10 |
| Under | 2 |
| Ober | 3 |
| König | 4 |
| Ass | 0 |

Sechs is highest, Ass lowest. Scoring inverts vs Oben roughly.

### Last trick bonus
The team winning the **9th (last) trick** scores extra **5** points.

### Match ("Matsch")
If one team wins **all 9 tricks** the round total gets a bonus (typically 100, consult `utils/game_utils.py`).

## Trick-Winning Logic (`max_game`)

Four cards per trick, one per player. Determine winner:

1. **Lead suit** = suit of the first card played in the trick.
2. **Trump game (`operator ∈ SUITS`):**
   - Any trump card beats any non-trump card.
   - Among trumps: highest trump rank wins (Under=20 > Neun=14 > Ass=11 > König=4 > Ober=3 > Banner=10... with trump rank order: **U > 9 > A > K > O > B > 8 > 7 > 6**).
   - Among non-trumps: only lead-suit cards compete; highest follows the non-trump rank order (A > K > O > U > B > 9 > 8 > 7 > 6).
3. **`Oben`:** highest card of lead suit wins. Order: A > K > O > U > B > 9 > 8 > 7 > 6.
4. **`Unten`:** highest card of lead suit by inverted order. Order: 6 > 7 > 8 > 9 > B > U > O > K > A.

## Following Suit

- If you have a card in the lead suit you must play one.
- **Trump-Under exception:** in a trump game, the trump Under (Bube) may always be played, even if you could follow the lead suit.
- If you cannot follow, you may play any card (including a trump — called "stechen").

## Schieben

Starter of the round may pass the trump choice to the partner across the table (`comps` ↔ `compn`, `compo` ↔ `compe`):

- Only **once per round**.
- Partner must then choose a real trump (cannot schieben back).
- Round starter (for lead purposes) remains the original player — only the trump-chooser changes.

## Weis (Meld)

Declared after trump is known, before the first trick. Server detects; player may announce or withhold.

### Patterns

- **Dreier (3 of a suit in sequence)** — 20 points
- **Vierer (4 of a suit in sequence)** — 50 points
- **Fünfer (5 of a suit in sequence)** — 100 points
- **Sechser/… higher sequences** — scale upward
- **Vier Gleiche (4 of a rank)** — values vary by rank; trump-Under quadruple is highest (200)

Sequences: consecutive by normal rank order (A-K-O-U-B-9-8-7-6 as "face cards down"), **not** by trump-rank order.

### Resolution

Only the **team with the strongest Weis** scores. Their entire declared Weis-list then counts. Compare:
1. Highest sequence length; tiebreak by highest card in sequence.
2. `Vier Gleiche` is compared by rank value; trump-Under quadruple trumps everything.
3. If the two teams have equal-strength top Weis, no one scores (tradition varies; consult `wiis_gleiche` in `Cards_refactored.py`).

## Scoring Flow Per Round

1. Each trick: winner's team gets the trick point total.
2. Last trick: +5 bonus to winner's team.
3. Weis: winning-Weis team adds their declared Weis points.
4. Match: if applicable, bonus to the winning team.
5. `point_sn` / `point_ow` accumulators updated.
6. If either team ≥ 1000, game ends. Otherwise deal next round.

## Key Code Locations

| Concept | File | Function |
|---------|------|----------|
| Point value attributes on cards | `Cards_refactored.py` | `Card` subclass definitions |
| Trump determination | `Cards_refactored.py` | `determine_trumpf`, `trumpfs` |
| Weis detection | `Cards_refactored.py` | `wiis`, `wiis_gleiche` |
| Trick winner | `utils/game_utils.py` | `max_game` |
| Game end check | `utils/game_utils.py` | `check_game_end`, `get_winner` |
| Valid cards | `ausbau/game_session.py` | `get_valid_cards` |
| AI card selection | `ausbau/game_session.py` | `ai_select_card` |

## Common Pitfalls

- **Trump-rank vs normal-rank confusion.** Under = 20 points *in trump suit*, 2 points otherwise. Weis sequences use normal rank order, not trump order.
- **Banner (10) value.** 10 points across all modes except `Unten` where it is still 10 — verify against card attribute arrays.
- **Oben/Unten Sechs.** In `Unten`, Sechs is both highest-ranked and scores 11. Not 0.
- **Last-trick bonus** is 5, not 10. Matsch is separate.
- **Team on Schieben** — the starter's *team* is fixed by seat, but the trump-chooser changed; lead remains with the original starter.
