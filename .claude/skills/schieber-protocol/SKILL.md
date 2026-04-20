---
name: schieber-protocol
description: Ground-truth WebSocket message contract between Schieber backend (`ausbau/server.py` + `ausbau/game_session.py`) and frontend (`ausbau/html5/js/schieber.js`). Read before adding, changing, or validating any `send_json` / `receive_json` / `ws.onmessage` / `ws.send` call. Consulted by schieber-backend, schieber-frontend, schieber-qa, schieber-reviewer. If a code path sends or reads a field not listed here, either the code is wrong or this skill is out of date — reconcile before proceeding.
---

# Schieber WebSocket Protocol

Authoritative message contract. Backend at `ws://.../ws` pushes state, client sends user actions.

## Card Codes

Every card is a string `<suit_prefix><rank_suffix>`.

| Suit | Prefix | | Rank | Suffix |
|------|--------|---|------|--------|
| Eicheln | `E` | | Ass | `A` |
| Rosen | `R` | | Koenig | `K` |
| Schellen | `SE` | | Ober | `O` |
| Schilten | `SI` | | Under | `U` |
| | | | Banner | `B` |
| | | | Neun | `9` |
| | | | Acht | `8` |
| | | | Sieben | `7` |
| | | | Sechs | `6` |

Example: `EA` = Eichel-Ass, `SIU` = Schilten-Under (Trumpf-Under in Schilten game).

## Position Keys

Internal: `comps` (Süd / human), `compo` (Ost), `compn` (Nord), `compe` (West).
Display names: `"Süd"`, `"Ost"`, `"Nord"`, `"West"`.

Server sends both `player_key` (internal) and `player` (display) in most events; client may use either.

## Server → Client

### `game_start`

First message on connection. One-shot.
```
{ "type": "game_start",
  "hand": ["EA","EK",...],       // 9 codes, human's cards
  "first_player": "Süd",         // display name of starter
  "players": [                   // the three NON-HUMAN seats (compe, compn, compo)
    { "name": "West", "position": "compe", "is_partner": false, "card_count": 9 },
    { "name": "Nord", "position": "compn", "is_partner": true,  "card_count": 9 },
    { "name": "Ost",  "position": "compo", "is_partner": false, "card_count": 9 }
  ],
  "scores": { "sn": <int>, "ow": <int> },  // running totals at deal time (0 for spiel 1)
  "target": 1000 }               // game-end target score; stable for the session
```

`players` enumerates the three AI seats only — the human (`comps`) is implicit and rendered at the bottom of the table. Each entry: `name` (display), `position` (internal key), `is_partner` (true for the human's partner, i.e. `compn`), `card_count` (cards remaining — 9 at deal, decremented client-side on `card_played`). `scores` and `target` drive the HUD.

### `trump_request`

Server asks a player (human = `comps`) to choose trump or schieben.
```
{ "type": "trump_request",
  "can_schieben": true/false }   // false after one schieben
```
Human replies with `choose_trump` or `schieben`.

### `trump_chosen`

Broadcast after any player (human or AI) chose trump.
```
{ "type": "trump_chosen",
  "suit": "Eicheln"|"Rosen"|"Schellen"|"Schilten"|"Oben"|"Unten",
  "by": "Süd" }                  // display name of chooser
```

### `weis_request`

Server asks human which Weis to announce (Weis already detected server-side).
```
{ "type": "weis_request",
  "your_weis": [                 // list of Weis dicts (may be empty → request is skipped)
    { "name": "Dreier", "suit": "Eicheln", "points": 20 },
    { "name": "Viererle", "suit": null, "points": 100 }
  ] }
```

Each entry has `name` (German label), `suit` (suit where the sequence lives, or `null` for rank-based "Vier Gleiche"), and `points` (the Weis's own value). Human replies with `declare_weis`.

### `weis_result`

Broadcast after the Weis phase resolves (including scoring).
```
{ "type": "weis_result",
  "announcements": [
    { "player": "Süd",
      "weis": [ { "name": "Dreier", "suit": "Eicheln", "points": 20 }, ... ],
      "points": 20 },            // sum for this player's announced weis
    ...
  ],
  "scores": { "sn": <int>, "ow": <int> } }  // running totals AFTER weis are added
```

`announcements[].weis` are dicts (same shape as `weis_request.your_weis` entries). `announcements[].points` is the sum for that player. Entries are ordered by seat. Players with no announced Weis are omitted. `scores` reflects totals after the winning-team's Weis points are added.

### `your_turn`

Server prompts human to play a card. Arrives whenever `comps` is on turn.
```
{ "type": "your_turn",
  "valid_cards": ["EA","RO",...] }  // codes currently legal to play
```
Human replies with `play_card`. If human replies with an illegal card, server sends `error` + repeats `your_turn`.

### `card_played`

Broadcast whenever any player (including human) plays a card.
```
{ "type": "card_played",
  "player": "Süd",                // display
  "player_key": "comps",          // internal
  "card": "EA",
  "trick_so_far": [               // optional — cards played in the current trick so far, in play order
    { "player_key": "compn", "card": "EK" },
    ...
  ] }
```

`trick_so_far` is optional; live clients can reconstruct the trick from the stream of `card_played` events themselves. It is intended for reconnect / observer clients that join mid-trick — when emitted, each entry represents one already-played card in this same trick and the final entry is the current card.

### `trick_end`

Broadcast after the 4th card of a trick. Sent before the next `your_turn` / `card_played`.
```
{ "type": "trick_end",
  "winner": "Süd",                // display
  "winner_key": "comps",          // internal
  "points": <int>,                // REQUIRED — point value of THIS trick only
  "points_sn": <int>,             // optional — running team-SN total after this trick
  "points_ow": <int>,             // optional — running team-OW total after this trick
  "cards": [                      // optional — full trick for replay (reconnect-only)
    { "player_key": "...", "card": "..." }, ...
  ] }
```

`points` is the per-trick value (0..any). `points_sn`/`points_ow` are convenience running totals; clients may use them or keep their own totals. `cards` is optional and intended for reconnect / observer clients — live clients already have the cards from the preceding `card_played × 4` stream.

### `round_end`

After 9 tricks.
```
{ "type": "round_end",
  "score_sn": <int>,
  "score_ow": <int>,
  "target": 1000 }
```
Followed immediately by a fresh `game_start` unless `game_end`.

### `game_end`

When a team reaches target score.
```
{ "type": "game_end",
  "winner_team": "sn"|"ow",
  "final_scores": { "sn": <int>, "ow": <int> } }
```

### `error`

Server rejected a client action. Client should surface to user.
```
{ "type": "error",
  "message": "Ungültige Karte: E6" }
```

## Client → Server

Sent only in response to a server prompt (`trump_request`, `weis_request`, `your_turn`). Spontaneous client messages are not expected.

### `choose_trump`
```
{ "type": "choose_trump",
  "suit": "Eicheln"|"Rosen"|"Schellen"|"Schilten"|"Oben"|"Unten" }
```

### `schieben`
```
{ "type": "schieben" }
```
Valid only when `trump_request.can_schieben` was `true`.

### `declare_weis`
```
{ "type": "declare_weis",
  "weis": ["Dreier"],             // subset of `weis_request.your_weis`
  "announce": true/false }        // false = decline to announce any
```

### `play_card`
```
{ "type": "play_card",
  "card": "EA" }
```
Must be in the most recent `your_turn.valid_cards`.

## Invariants

1. **Every card string** in any message is a valid code from the table above.
2. **Every `*_key`** field is one of `comps`, `compo`, `compn`, `compe`.
3. **Every display-name `player` / `winner` / `by` / `first_player`** is one of `"Süd"`, `"Ost"`, `"Nord"`, `"West"`.
4. **Turn order** is `comps → compo → compn → compe → comps …` wrapped so the lead player starts each trick.
5. **No silent failures.** If a client action is invalid, server responds with `error` and re-sends the most recent prompt (`your_turn` or `trump_request`).
6. **Broadcast ordering** for a trick: `card_played × 4` then `trick_end`. For a round end: `trick_end` (last trick) then `round_end`. For a game end: `round_end` then `game_end`.

## When to Update This Skill

- A new message type is added to backend or frontend → add the type here first, then implement.
- A field is added/removed/renamed → update here, then update both sides.
- Semantics change ("`can_schieben` now also means X") → update the relevant prose.

Drift between code and this skill is a defect, caught in QA.
