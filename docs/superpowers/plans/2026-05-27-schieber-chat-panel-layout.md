# Chat-Panel Layout Refactor & Diagnostics Cleanup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Verify and land the in-progress chat-panel layout refactor and remove the temporary WebSocket/chat debug prints, producing a clean, browser-verified commit.

**Architecture:** The in-game chat moves from a flex sidebar inside a `#game-main` wrapper to a `position: fixed` right-hand panel that is a sibling of the (now 800×600, centered, flex-column) `#game` board. The duplicate row-flex `#game` rule and the `#game-main` wrapper are deleted, `html,body` background is unified to the table green, and the game-log moves from the left edge to `right: 14px`. The `server.py` change is pure cleanup: the `[ws] connect`, `[ws] reader loop start`, and `[chat]` stderr diagnostics added in commit `9c07448` are removed.

**Tech Stack:** Vanilla JS + HTML + CSS frontend; FastAPI WebSocket backend (`ausbau/server.py`); Playwright (via `webapp-testing` skill) for browser verification; `python run_tests.py` for the suite.

> **Note on TDD:** This work is already implemented in the working tree and is layout/cleanup only — there is no new behavior to drive with a red-green unit test. The plan therefore verifies via static checks, the existing test suite, and in-browser observation rather than writing new failing unit tests first. This is a deliberate, scoped deviation from greenfield TDD.

**Files in scope (all currently uncommitted):**
- Modify: `ausbau/html5/css/game.css` — chat panel → fixed; remove `#game-main` + duplicate `#game`; `html,body` bg green; game-log → right.
- Modify: `ausbau/html5/game.html` — remove `#game-main` wrapper and stray closing `</div>`; chat panel becomes sibling of `#game`.
- Modify: `ausbau/server.py:~779-810` — remove temporary stderr diagnostics.

---

### Task 1: Static sanity checks on the refactored markup/CSS

**Files:**
- Read: `ausbau/html5/game.html`
- Read: `ausbau/html5/css/game.css`
- Read: `ausbau/html5/js/schieber.js`

- [x] **Step 1: Confirm no code references the removed `#game-main` wrapper**

Run: `grep -rn "game-main" ausbau/html5/`
Expected: no matches (the wrapper is fully removed; nothing should target it).

- [x] **Step 2: Confirm there is exactly one `#game` rule and no orphaned `#game-main` rule in CSS**

Run: `grep -n "^#game\b\|^#game-main\b\|^#game {" ausbau/html5/css/game.css`
Expected: a single `#game {` selector (the 800×600 flex-column board). No `#game-main` selector remains. If a second `#game` block or a stray `#game-main` block is found, delete the orphan.

- [x] **Step 3: Confirm the chat-panel DOM still matches what the JS queries**

Run: `grep -rn "chat-messages\|chat-input\|chat-send\|chat-header" ausbau/html5/js/`
Expected: every chat element the JS reads (`#chat-messages`, `#chat-input`, `#chat-send`) still exists in `game.html` lines 114–121. The refactor only moved the `#chat-panel` element; its children are unchanged, so all queries should still resolve.

- [x] **Step 4: Confirm the `game.html` div nesting is balanced**

Verify by reading `ausbau/html5/game.html`: `#game` opens at line 17 and closes at line 111; `#chat-panel` (lines 114–121) is a sibling that follows the closed `#game`. There must be no unmatched `</div>`. Expected: balanced — `#game` and `#chat-panel` are siblings, both direct children of `<body>`.

---

### Task 2: Confirm the diagnostics removal is complete and behavior-neutral

**Files:**
- Modify: `ausbau/server.py`

- [x] **Step 1: Confirm no leftover debug prints remain in the WS endpoint**

Run: `grep -n "\[ws\]\|\[chat\]\|_sys\|_pid\|_who" ausbau/server.py`
Expected: no matches. The connect log, reader-loop log, and chat log added in `9c07448` are all gone, along with their now-unused `import sys as _sys` / `from ausbau.room import principal_id as _pid` helpers.

- [x] **Step 2: Confirm the chat broadcast itself is intact**

Verify by reading the WS reader loop in `ausbau/server.py` (around line 800): the `await room.broadcast({"type": "chat_message", ...})` call must still be present — only the `print(...)` lines around it were removed, not the broadcast. Expected: `chat_message` broadcast still fires; only logging was deleted.

- [x] **Step 3: Confirm the module still imports**

Run: `python -c "import ausbau.server"`
Expected: no `NameError`/`ImportError` (would catch a dangling reference to a removed `_sys`/`_pid`/`_who` name).

---

### Task 3: Run the test suite

**Files:**
- Test: whole suite via `run_tests.py`

- [x] **Step 1: Run the full suite**

Run: `python run_tests.py`
Expected: PASS. The only Python change is the removal of stderr prints, so no test behavior should change. If any multiplayer/WS test fails, investigate before proceeding — it would indicate the diff removed more than logging.

---

### Task 4: In-browser verification (golden path + layout)

**Files:**
- Uses: running server + Playwright (`webapp-testing` skill).

- [x] **Step 1: Start the server**

Run (background): `python -m uvicorn ausbau.server:app --reload --port 8765` with the env vars from `.env.example` set.
Expected: server boots, `http://localhost:8765` reachable.

- [x] **Step 2: Open the game page and capture a screenshot**

Drive a browser to a room's game page (create/join a room so `/game?...` renders the board) and screenshot the full viewport.
Expected: the 800×600 board is centered on the green (`#2d5a27`) background; the chat panel is pinned to the right edge from just below the auth strip (`top: 2.4rem`) to the bottom.

- [x] **Step 3: Verify the game-log does NOT collide with the chat panel**

Inspect the bottom-right of the board. The game-log is `position: absolute; bottom: 10px; right: 14px; width: 200px` relative to the centered `#game`; the chat panel is `position: fixed; right: 0; width: 220px`. On a typical desktop width they should not overlap, but on a narrower window the board's right edge approaches the fixed panel.
Expected: game-log entries are fully readable and not hidden behind the chat panel. If they overlap → apply Task 5. If clear → mark Task 5 N/A.

- [x] **Step 4: Exercise the chat golden path**

Type a message in `#chat-input` and send via `#chat-send` (and Enter key). Confirm the message appears in `#chat-messages`. With a second client/seat in the same room, confirm the message is received there too (validates the `chat_message` broadcast still works after the print removal).
Expected: messages send and render on both clients; no JS console errors.

- [x] **Step 5: Smoke-test core gameplay still renders**

Play through trump selection and at least one trick. Confirm the AI bar, table, trick area, hand, and modals (trump/weis) all render correctly within the now-flex-column board and are not obscured by the fixed chat panel.
Expected: no visual regression vs. the committed layout; modals appear centered and clickable.

---

### Task 5: (Conditional) Fix game-log / chat-panel overlap

> Only perform this task if Task 4 Step 3 found the game-log overlapping the fixed chat panel. Otherwise skip and mark N/A.

**Files:**
- Modify: `ausbau/html5/css/game.css` (the `#game-log` rule, ~line 311)

- [x] **Step 1: Reserve the chat-panel width so the board never sits under it**

Add a right margin/padding on `body` (or shift `#game`’s centering) so the centered 800px board is offset left of the 220px fixed panel. Concrete option — add to the `html, body` rule:

```css
/* Reserve space for the fixed 220px chat panel so the board never underlaps it */
body { padding-right: 220px; }
```

(If this over-shifts on wide screens, instead constrain only narrow widths with a media query; the body-padding approach is the simplest correct fix.)

- [x] **Step 2: Re-verify in browser**

Re-run Task 4 Steps 2–3. Expected: board + game-log clear of the chat panel at both wide and narrow widths.

---

### Task 6: Commit

- [x] **Step 1: Stage the three in-scope files**

```bash
git add ausbau/html5/css/game.css ausbau/html5/game.html ausbau/server.py
```

- [x] **Step 2: Commit**

```bash
git commit -m "$(cat <<'EOF'
Refactor in-game chat into fixed right panel; remove WS debug prints

Chat panel is now a position:fixed sibling of the board instead of a
flex sidebar in a #game-main wrapper. Removes the duplicate #game rule,
unifies the page background to the table green, and moves the game-log
to the right. Also drops the temporary [ws]/[chat] stderr diagnostics
added in 9c07448.
EOF
)"
```

- [x] **Step 3: Verify the commit landed and the tree is clean**

Run: `git status`
Expected: working tree clean (no remaining modifications to the three files).

---

## Self-Review

- **Coverage:** Every uncommitted hunk is covered — CSS/HTML chat refactor (Tasks 1, 4, 5), `#game-main` removal (Task 1), server.py diagnostics removal (Tasks 2, 3), and landing the work (Task 6).
- **Placeholders:** None — each step has a concrete command or a specific file/line to read, with expected results.
- **Consistency:** Element ids referenced (`#game`, `#game-main`, `#chat-panel`, `#chat-messages`, `#chat-input`, `#chat-send`, `#game-log`) match `game.html` lines 17–121 and the CSS selectors. The overlap fix in Task 5 targets the same `#game-log`/chat-panel geometry verified in Task 4.
