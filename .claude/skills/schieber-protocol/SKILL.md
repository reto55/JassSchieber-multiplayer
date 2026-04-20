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
  "first_player": "Süd" }        // display name of starter
```

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
  "your_weis": ["Dreier","50"] } // list of Weis names found
```
Human replies with `declare_weis`.

### `weis_result`

Broadcast after the Weis phase resolves (including scoring).
```
{ "type": "weis_result",
  "announcements": [
    { "player": "Süd", "weis": ["Dreier"] },
    ...
  ],
  "scores": { "sn": <int>, "ow": <int> } }
```

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
  "trick_so_far": [
    { "player_key": "compn", "card": "EK" },
    ...
  ] }
```

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
