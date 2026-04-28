# Schieber — Mobile / Responsive Layout Design

**Date:** 2026-04-28
**Author:** brainstorming session (user: Reto Müller)
**Status:** approved (design phase) — pending implementation plan
**Scope:** primarily frontend (CSS / HTML / JS). One small backend touch: `GameSession` gains an optional RNG seed via env var, used only by the new Playwright suite. No protocol changes. No DB changes.

## 1. Goal

Make the existing single-player Schieber HTML5 game (browser ↔ FastAPI `/ws` ↔ `GameSession`) usable on phones and tablets in both orientations, without regressing the desktop experience. Add Playwright responsive snapshot tests to prevent layout regressions.

This is one of four planned extension sub-projects (mobile, AI difficulty, accounts, networked multiplayer). It is intentionally tackled first because it has zero dependencies on the others.

## 2. Non-goals

- Networked multiplayer (separate sub-project, will be designed later).
- User accounts / persistent login (separate sub-project).
- AI difficulty settings (separate sub-project).
- Asset re-export to higher-DPI sprite sheets (`Jasskarten@2x.png`).
- PWA, install-to-homescreen, or offline support.
- Keyboard accessibility / screen-reader support (noted as future work, not blocking).
- Drag-to-play gesture (decided against in favor of tap-to-lift / tap-to-confirm).
- Animations beyond the existing `transition: transform .15s`.

## 3. Approach

**Approach 1 — Minimal patch.** Append `@media` blocks to existing `frontend/css/game.css`, restructure topology via CSS `grid-template-areas`, add a small new `frontend/js/touch.js` module for the tap-to-lift state machine, and add a Playwright responsive test suite.

Rejected alternatives:
- *Layered files* (split CSS by breakpoint): triples file count for ~200 lines of media queries. YAGNI.
- *Container-query first*: game is `100vh` fullscreen, viewport == container, so `@container` adds cognitive load with no benefit until the game is embedded somewhere — not on the roadmap.

## 4. Breakpoints + topology

Five viewport classes. Boundaries chosen at common device widths.

| Class | Width × Height | Topology | Hand | Log |
|-------|---------------|----------|------|-----|
| **phone-portrait** | `(max-width: 480px) and (orientation: portrait)` | top-bar (W,N,O), trick-cross center, hand bottom | overlap fan, scale 0.55 | hidden |
| **phone-landscape** | `(max-height: 500px) and (orientation: landscape)` | top-bar (W,N,O), trick-cross, hand bottom | overlap fan, scale 0.65 | hidden |
| **tablet-portrait** | `(min-width: 481px) and (max-width: 820px) and (min-height: 501px)` | compass: N top, W left strip, O right strip, hand bottom | wrap, scale 0.85 | shrunk 140×100 |
| **tablet-wide** | `(min-width: 821px) and (max-width: 1199px) and (min-height: 501px)` | compass | wrap, scale 0.9 | 180×140 |
| **desktop** | `(min-width: 1200px) and (min-height: 501px)` | compass (current layout, unchanged) | wrap, scale 1.0 | 200×160 (current) |

The five `@media` blocks are layered in cascade order from broadest (desktop, default) to most specific (phone-landscape, last). Conditions may overlap in principle; the **last matching block wins** by CSS source-order, which is the normal `@media` pattern. The intended cascade is:

```
1. desktop          (default base styles, no @media wrapper)
2. tablet-wide      @media (max-width: 1199px) and (min-height: 501px)
3. tablet-portrait  @media (max-width: 820px)  and (min-height: 501px)
4. phone-portrait   @media (max-width: 480px)  and (orientation: portrait)
5. phone-landscape  @media (max-height: 500px) and (orientation: landscape)
```

Notable consequences of this ordering:
- A 1300×400 foldable ends at `phone-landscape` (last match), keeping hand usable on a short viewport.
- A 480×800 phone lands in `phone-portrait` (overrides tablet-portrait via cascade).
- A 481×500 device (portrait, just over phone width but exactly at short-height threshold) lands in `tablet-portrait` only (height clause fails phone-portrait orientation rule and phone-landscape orientation rule).
- An 850×900 tablet held portrait lands in `tablet-wide` (width >820 fails tablet-portrait). The "wide" label refers to topology bucket, not orientation.

Notes:
- *Compass* topology means: Nord row at top, West/Ost as ~60-80px vertical strips flanking the table, trick-cross in the middle. Matches the trick-area cross labelling.
- *Top-bar* topology is the current layout (W, N, O abreast in a top strip). Kept for phones because vertical strips on a 360px-wide screen would steal too much horizontal real estate from the trick area.
- `phone-landscape` is distinguished by `(max-height: 500px) and (orientation: landscape)` so square tablets don't fall into it.
- All breakpoints honor `prefers-reduced-motion: reduce` (skip card transition animations).

## 5. Component changes

HTML structure stays largely intact. Compass topology is achieved via CSS `grid-template-areas`, not by moving DOM nodes.

### 5.1 AI bar (`#ai-bar`)

- **Phone (both orientations):** avatar shrinks 34→24px; per-opponent card-back stack hidden, replaced by a single "🂠 ×N" count badge; score panel collapses to a compact `SN 0 · OW 0` row.
- **Tablet+:** `#ai-bar` becomes a CSS grid with template areas placing `#player-compn` (Nord) at top, `#player-compe` (West) on left strip, `#player-compo` (Ost) on right strip. Score panel moves to a fixed corner (top-right) via `grid-area: score`.

### 5.2 Table (`#table`)

- **Phone:** `#trick-area` slots shrink 56→40px wide. `#trump-badge` and `#round-info` move from absolute corners to an inline pill row above the trick area (avoids collision when the table is short).
- **Tablet+:** trick-cross dimensions unchanged; trump-badge / round-info stay absolute corners.

### 5.3 Hand (`#hand-area`)

- **Phone:** `#hand-cards` switches from `flex; gap:6px; flex-wrap:wrap` to overlap fan: `display:flex; gap:0`. Each `.card` gets `margin-left: -50px`; the first child overrides to `0`. Width fills viewport. Cards on touch get `.lifted` class (translate-y -16px, z-index bump). Neighbors of a lifted card spread to `margin-left: -35px` via `:has(.lifted) + .card` and the equivalent reverse selector.
- **Tablet+:** keep current wrap + flex.

### 5.4 Game log (`#game-log`)

- **Phone (both):** `display: none`. (Decision Q4 — most events are visible from trick-area + score anyway.)
- **Tablet portrait:** shrink to 140×100, font 9px.
- **Tablet landscape / desktop:** current 200×160.

### 5.5 Modals (`#trump-modal`, `#weis-modal`)

- **Phone:** `min-width` removed; `max-width: 92vw`; padding 14px; font +2px (touch readability); suit-grid stays 2-col; buttons get `min-height: 44px` (Apple HIG touch target).
- **Tablet+:** current.

### 5.6 Hand-card states (touch)

- Drop the `.valid:hover` lift on touch devices via `@media (hover: none)`.
- Add `.lifted` class (translate-y -16px, yellow border emphasized, z-index bump, subtle 1s pulse).
- Add `.dimmed` class for non-lifted cards while one is lifted (opacity 0.7).

## 6. Touch interaction state machine

New module `frontend/js/touch.js`. Single source of truth for "which card is lifted".

### 6.1 States

```
IDLE              — no card lifted
LIFTED(cardId)    — one card lifted, awaiting confirm or cancel
```

### 6.2 Transitions

| From | Event | Action | To |
|------|-------|--------|----|
| IDLE | tap valid card C | add `.lifted` to C, `.dimmed` to others | LIFTED(C) |
| IDLE | tap invalid card | flash red 200ms | IDLE |
| LIFTED(C) | tap C again | send `{type:"play_card", code:C}`, clear classes | IDLE |
| LIFTED(C) | tap valid card C2 (≠C) | move `.lifted` to C2 | LIFTED(C2) |
| LIFTED(C) | tap invalid card | flash red, keep C lifted | LIFTED(C) |
| LIFTED(C) | tap outside `#hand-cards` | clear classes | IDLE |
| LIFTED(C) | server `your_turn` for next round | clear classes | IDLE |
| LIFTED(C) | server `error` | clear classes | IDLE |

### 6.3 Activation

- State machine is active only when `(hover: none)` matches (covers all touch-primary devices).
- At script load: `document.body.classList.toggle('touch-mode', matchMedia('(hover: none)').matches)`.
- Touch handlers attach only when `body.touch-mode` is set.
- Desktop keeps existing single-click semantics (one click = play).

### 6.4 Integration with existing `schieber.js`

- The existing `playCard(code)` function is called on the confirm transition.
- Existing card-click handler is split: if `body.classList.contains('touch-mode')`, route through state machine; else play immediately.
- No protocol changes. Server is stateless about lift / confirm — it only sees the final `play_card` message identical to today's flow.

### 6.5 Cancellation UX

- "Tap outside" zone = anywhere not inside `#hand-cards`. Trick area, AI bar, log, modals — all cancel a lifted card.
- Lifted card has a subtle 1s pulse loop signaling "tap again to play".

## 7. Sprite scaling

Per decision Q6: CSS `transform: scale(<factor>)` on `.card` wrappers at smaller breakpoints. Slight blur is acceptable for phone-sized cards. `image-rendering: crisp-edges` applied to `.face.back` to harden edges.

No new sprite assets needed.

## 8. Testing

### 8.1 Playwright suite

- New deps in `requirements-html5.txt`: `pytest-playwright`.
- New `tests/e2e/conftest.py`: spawns `uvicorn frontend.server:app --port 8766` in subprocess, waits for `/` to return 200, yields `base_url`, kills on teardown.
- New `tests/e2e/test_responsive.py`: tests parametrized over viewport sizes.

### 8.2 Viewports

| Name | Size | Class |
|------|------|-------|
| `iphone-se` | 375×667 | phone-portrait |
| `iphone-landscape` | 667×375 | phone-landscape |
| `ipad-portrait` | 768×1024 | tablet-portrait |
| `ipad-landscape` | 1024×768 | tablet-landscape |
| `desktop` | 1280×800 | desktop |

### 8.3 Test cases (per viewport)

1. **Layout snapshot** — full-page screenshot compared to baseline `tests/e2e/snapshots/<viewport>.png`, tolerance 1%.
2. **No horizontal overflow** — `document.documentElement.scrollWidth === clientWidth`.
3. **Hand fits viewport** — `#hand-cards` bounding box `right - left ≤ viewport.width`.
4. **Trick area not occluded** — `#trick-area` `getBoundingClientRect` does not intersect `#game-log` or trump/round badges.
5. **Tap-to-play flow (phone viewports only)** — `page.tap` valid card → assert `.lifted` present; tap again → assert WebSocket `play_card` was sent.
6. **Modal usable on phone (phone viewports only)** — open trump modal, assert all 6 suit buttons visible without scroll.

### 8.4 Snapshots

- Baselines committed under `tests/e2e/snapshots/`.
- Update via custom `pytest --update-snapshots` flag.
- Backend serves a deterministic game state. Note: no such fixture exists today — `GameSession` shuffles via `random.shuffle` with no seed parameter. Implementation will need a small extension: an optional environment variable (e.g. `SCHIEBER_DECK_SEED`) read by `GameSession.__init__` to seed the RNG. Setting it from `conftest.py` before launching `uvicorn` gives reproducible deals for snapshot baselines. This RNG-seed plumbing is part of the implementation plan, not a backend redesign.

### 8.5 CI integration

- `run_tests.py` extended with an optional `--e2e` flag that runs the Playwright suite. Default unchanged (unit tests only). Keeps the default test runs fast.

### 8.6 Manual checklist (executed at end of implementation)

- Real iPhone Safari, real Android Chrome, desktop Firefox / Chrome / Safari at all 5 viewport sizes.
- Golden-path: deal → choose trump → announce weis → play 9 tricks → next round.
- Edge cases: tap-outside cancels lift; rotate device mid-game; modal on smallest viewport.

## 9. File changes

### 9.1 Modified

- `frontend/css/game.css` — append ~200 lines of `@media` blocks; add `grid-template-areas` for compass topology; add `.lifted` / `.dimmed` / `.touch-mode` rules.
- `frontend/game.html` — add `<script src="/static/js/touch.js">` before `schieber.js`. (Compass topology is achieved via CSS grid alone — no DOM restructure required.)
- `frontend/js/schieber.js` — split card-click handler: route to touch state machine when `body.touch-mode`, else play immediately. ~10-line change.

### 9.2 Added

- `frontend/js/touch.js` — touch state machine (~80 lines).
- `tests/e2e/conftest.py` — Playwright fixtures (~40 lines).
- `tests/e2e/test_responsive.py` — responsive test cases (~150 lines).
- `tests/e2e/snapshots/*.png` — 5 baseline screenshots (one per viewport).
- `requirements-html5.txt` — add `pytest-playwright`.

### 9.3 Minimal backend touch (testability only)

- `frontend/game_session.py` — accept an optional `SCHIEBER_DECK_SEED` env var (read at `GameSession.__init__`); when set, seed the RNG used to shuffle. Production deployments leave it unset and behavior is unchanged.
- This is the only backend change. **No protocol changes. No DB changes.** All other backend files (`frontend/server.py`, `Cards.py`, `utils/`, `frontend/database_manager.py`) and all existing `tests/test_*.py` remain untouched.

## 10. Risks + mitigations

| Risk | Mitigation |
|------|------------|
| Sprite blur at scale 0.55 on phone | Acceptable per design decision; `image-rendering: crisp-edges` on `.face.back` to harden edges |
| Compass `grid-template-areas` regression on desktop | Baseline screenshot for `desktop` viewport catches any pixel diff |
| Tap-target collision in overlap fan (lifting the wrong card) | `.lifted` raises z-index; `:has(.lifted) + .card` spreads neighbors by 15px; Playwright tap test verifies the correct card lifts |
| `(hover: none)` false-positive on hybrid devices (Surface, iPad+keyboard) | User can still tap; first tap lifts, second plays — no worse than the touch flow. Desktop hover still works for primary mouse input. |
| Playwright snapshot flakiness from font rendering / GPU diffs | Tolerance 1%; CI uses fixed Linux Chromium; baseline regenerated per platform if needed |

## 11. Success criteria

- All five Playwright viewport snapshot tests pass green on a fresh checkout.
- Manual checklist completed without blocking issues on at least one real iOS and one real Android device.
- Existing `python run_tests.py` (unit tests, no `--e2e` flag) is unchanged and still green — no regressions in backend or protocol behavior.
- Desktop screenshot at 1280×800 is pixel-equivalent to the pre-change baseline (within 1% tolerance) — the desktop layout must not shift.
