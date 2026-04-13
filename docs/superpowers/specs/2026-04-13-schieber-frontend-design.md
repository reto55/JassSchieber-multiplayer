# Schieber Frontend Design Spec

**Date:** 2026-04-13
**Scope:** HTML5 frontend + FastAPI WebSocket backend for a 4-player Schieber card game (1 human + 3 AI)

---

## Overview

A browser-based Schieber game served by a local FastAPI server. The human plays as South; three AI opponents (Nord/partner, West, Ost) run server-side using the existing Python game logic. Communication is over a single WebSocket connection per game session. The frontend lives in `ausbau/html5/` and reuses existing card assets and CSS sprite definitions.

---

## Files

```
ausbau/html5/
  game.html          ← single-page game (full rewrite of existing stub)
  css/game.css       ← extend existing (card sprite classes already present)
  js/schieber.js     ← new: WebSocket client + all UI logic (replaces game.js)
  images/            ← unchanged (all 36 card PNGs + Jasskarten.png present)

ausbau/
  server.py          ← new: FastAPI app — serves HTML + WebSocket endpoint
  game_session.py    ← new: thin adapter wrapping GameController for WebSocket use
```

No changes to `Cards_refactored.py`, `deal_cards_refactored.py`, or `utils/`. The existing game logic is used as-is.

---

## System Architecture

FastAPI serves `game.html` at `GET /` and handles WebSocket connections at `ws://localhost:PORT/ws`.

On connection:
1. `game_session.py` instantiates a `GameSession` which creates a `GameController` with 1 human player (South) and 3 AI players.
2. Server deals cards, sends `game_start` with the human's hand and initial state.
3. If South is not the first to choose trump, AI players resolve trump selection immediately server-side and the server sends the result.

On each AI turn, the server runs the AI move synchronously and pushes `card_played` to the client before returning control. The human is never waiting on a poll — the server drives the entire game flow via push messages.

---

## Frontend Layout

**Wide/Compact layout** — single `<div id="game">` filling the viewport:

### ① AI Bar (top strip)
Fixed-height strip across the top. Three AI players shown left-to-right (West · Nord · Ost). Each shows: avatar circle with initial, player name, face-down card count. Nord (partner) is highlighted green. Score panel on the far right shows `SN xxx / OW xxx` and the target score.

### ② Trump Badge + Round Info
Trump badge (top-left of table area): suit name + emoji. Round/trick counter and active player label (top-right).

### ③ Trick Area (center)
Four card slots at compass positions (N top, W left, O right, S bottom). Cards appear face-up as played. Empty slots show a dashed outline. Labels identify which player's slot is which.

### ④ Game Log (right side)
Scrolling text panel. Records: who played what card, who won each trick, Weis announcements, round scores.

### ⑤ Human Hand (bottom strip)
9 cards dealt, decreasing to 0 over the round. Playable cards glow gold (`box-shadow: 0 0 8px #ffcc00`). Illegal cards are dimmed (opacity 0.4, `cursor: not-allowed`). Click a valid card to play it. The server validates; on error the hand re-enables.

---

## Trump Selection

Triggered by `trump_request` from the server. A modal overlay appears (game dims to 55% opacity behind it):

- 2×3 grid: Eicheln, Rosen, Schellen, Schilten (red), Oben, Unten (blue)
- "Schieben" button below, only shown when `can_schieben: true`
- Clicking a suit sends `choose_trump`; clicking Schieben sends `schieben`
- If the human schiebt, the modal closes and re-opens when the server sends a second `trump_request` (without `can_schieben`)

---

## Weis Declaration

Triggered by `weis_request` after trump is chosen, before the first trick.

1. Modal appears (same overlay style as trump selection)
2. Lists all detected combinations with point values (server-computed)
3. Two buttons: **"Ansagen (N Pkt)"** and **"Schweigen"**
4. Human sends `declare_weis`; server resolves AI weis decisions immediately
5. Server sends `weis_result` — modal closes, result summary appears in game log, scores update in AI bar
6. Game proceeds to first trick

---

## WebSocket Protocol

All messages are JSON with a `type` field.

### Server → Client

| type | key payload fields | when |
|---|---|---|
| `game_start` | `hand` (array of card codes), `dealer`, `first_player`, `players` (array of `{name, position, is_partner}`) | on connect |
| `trump_request` | `can_schieben` | human must choose trump |
| `your_turn` | `valid_cards` | start of human's trick turn |
| `card_played` | `player`, `card` | after any card is played (AI or human) |
| `trick_end` | `winner`, `points_sn`, `points_ow` | after all 4 cards in trick |
| `weis_request` | `your_weis` | human has declarable combinations |
| `weis_result` | `announcements` (array of `{player, weis, points}`) | weis resolved |
| `round_end` | `score_sn`, `score_ow`, `winner_team` | after 9 tricks; server waits 2s then auto-starts next round |
| `game_end` | `winner_team`, `final_scores` | score limit reached |
| `error` | `message` | invalid action received |

### Client → Server

| type | payload |
|---|---|
| `choose_trump` | `suit`: one of `Eicheln`, `Rosen`, `Schellen`, `Schilten`, `Oben`, `Unten` |
| `schieben` | *(empty)* |
| `play_card` | `card`: card code string e.g. `"EA"`, `"RK"` |
| `declare_weis` | `weis`: array of combination names, `announce`: bool |

The server validates all actions. On an illegal `play_card`, it responds with `error` and re-sends `your_turn` with the valid card list.

---

## Card Rendering

Card codes follow the existing CSS convention already in `game.css`:
- Prefix: `E` (Eicheln), `R` (Rosen), `SE` (Schellen), `SI` (Schilten)
- Suffix: `A`, `K`, `O`, `U`, `B`, `9`, `8`, `7`, `6`
- Example: `EA` = Eicheln Ass, `SEK` = Schellen König

Cards are rendered as `<div class="card"><div class="face back cardXX"></div></div>` using the existing sprite sheet. No new image assets needed.

---

## Running the Game

```bash
# Install dependencies (once)
pip install fastapi uvicorn websockets

# Start the server
cd ausbau
uvicorn server:app --reload --port 8765

# Open in browser
# http://localhost:8765
```

---

## Out of Scope

- Networked multiplayer (multiple humans on different machines)
- User accounts or persistent login
- Mobile/responsive layout
- AI difficulty settings (AI uses existing `max_game()` logic as-is)
