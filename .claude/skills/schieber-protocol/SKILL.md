---
name: schieber-protocol
description: Ground-truth WebSocket message contract between Schieber backend (`ausbau/server.py` + `ausbau/game_session.py`) and frontend (`ausbau/html5/js/schieber.js`). Read before adding, changing, or validating any `send_json` / `receive_json` / `ws.onmessage` / `ws.send` call. Consulted by schieber-backend, schieber-frontend, schieber-qa, schieber-reviewer. If a code path sends or reads a field not listed here, either the code is wrong or this skill is out of date — reconcile before proceeding.
---

# Schieber WebSocket Protocol

Ground-truth message contract between the Schieber server (`ausbau/server.py` + `ausbau/game_session.py`) and the browser client (`ausbau/html5/js/schieber.js`).

**Connection model (multiplayer):** Each room is identified by a 6-char code. Each player opens one WebSocket to `/ws/{code}`. The server holds a `GameSession` per room and routes messages per-seat. Spectators connect to the same `/ws/{code}` and receive a TV-mode broadcast (no hands).

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

Internal: `comps` (Süd), `compo` (Ost), `compn` (Nord), `compe` (West).
Teams: `(compo, compe)` is East-West (`ow`); `(compn, comps)` is North-South (`sn`).

## Routing helpers

```python
async def send_to_seat(self, position: str, msg: dict) -> None:
    seat = self._seat(position)
    if seat.websocket is not None and not seat.is_ai:
        try:
            await seat.websocket.send_json(msg)
        except Exception:
            await self._disconnect_seat(position)


async def broadcast(self, msg: dict, *, except_seat: str | None = None) -> None:
    for seat in self.seats:
        if seat.position != except_seat:
            await self.send_to_seat(seat.position, msg)
    for spec in list(self.spectators):
        try:
            await spec.websocket.send_json(msg)
        except Exception:
            self.spectators.remove(spec)


async def broadcast_per_seat(self, msg_factory) -> None:
    """Each seat receives msg_factory(seat); spectators receive msg_factory(None)."""
    for seat in self.seats:
        await self.send_to_seat(seat.position, msg_factory(seat))
    tv_msg = msg_factory(None)
    for spec in list(self.spectators):
        try:
            await spec.websocket.send_json(tv_msg)
        except Exception:
            self.spectators.remove(spec)
```

## Server → Client Messages

### `game_start` (broadcast_per_seat)

For seat `compn`:
```json
{
  "type": "game_start",
  "your_position": "compn",
  "your_hand": ["EA","SK", ...],
  "first_player": "compo",
  "players": [
    {"position": "compo", "display_name": "alice",       "card_count": 9, "is_partner": true},
    {"position": "compe", "display_name": "AI (compe)",  "card_count": 9, "is_partner": false},
    {"position": "comps", "display_name": "Guest-3f9a",  "card_count": 9, "is_partner": false}
  ],
  "scores": {"sn": 0, "ow": 0},
  "target": 1000,
  "variant": {"trumpf_bock": false, "match_bonus": true, "stoeck": true}
}
```

For spectators (TV mode): `your_position: null`, `your_hand: null`, `players` lists all 4 with no `is_partner` field.

### `trump_request` / `trump_pending` / `trump_chosen`

`trump_request` → only the seat whose turn it is to choose:
```json
{"type": "trump_request", "schieben_allowed": true}
```

`trump_pending` → broadcast to others + spectators:
```json
{"type": "trump_pending", "by_position": "compo"}
```

`trump_chosen` → broadcast (final):
```json
{"type": "trump_chosen", "by_position": "compo", "operator": "Eicheln"}
```

### `weis_request` / `weis_resolution`

`weis_request` → each seat individually with their own weis:
```json
{"type": "weis_request", "your_weis": [{"name": "Dreier", "suit": "Eicheln", "points": 20}]}
```

`weis_resolution` → broadcast (everyone sees winner team and per-position weis):
```json
{
  "type": "weis_resolution",
  "winning_team": "sn",
  "weis_by_position": {
    "compo": [...], "compn": [...], "compe": [...], "comps": [...]
  }
}
```

### `play_request` / `play_pending` / `card_played`

`play_request` → only the seat whose turn it is:
```json
{
  "type": "play_request",
  "trick_so_far": [{"position": "compe", "card": "EA"}],
  "lead_suit": "Eicheln",
  "valid_cards": ["E6","E8","SI9"]
}
```

`play_pending` → broadcast to others + spectators:
```json
{"type": "play_pending", "by_position": "compn", "trick_so_far": [...]}
```

`card_played` → broadcast (final):
```json
{"type": "card_played", "by_position": "compn", "card": "E6"}
```

### `trick_end` / `spiel_end` / `game_end`

```json
{"type": "trick_end", "winner_position": "compe", "winner_team": "ow", "points": 14}
```

```json
{
  "type": "spiel_end",
  "scores": {"sn": 157, "ow": 100},
  "weis_added": {"sn": 20, "ow": 0},
  "match": false,
  "stoeck_team": "sn"
}
```

```json
{"type": "game_end", "winner_team": "sn", "scores": {"sn": 1031, "ow": 940}}
```

### Lifecycle events (broadcast)

```json
{"type": "seat_paused", "position": "compn", "reconnect_deadline_secs": 60, "display_name": "bob"}
{"type": "seat_reclaimed", "position": "compn", "display_name": "bob"}
{"type": "seat_ai_takeover", "position": "compn"}
{"type": "seat_changed", "seat": {...}, "reason": "join"|"leave"|"disconnect"|"kick"|"ai_takeover"}
{"type": "seat_kicked", "position": "compn", "by_host": true}
{"type": "host_changed", "old_host_position": "compn", "new_host_position": "compo", "new_host_display_name": "alice"}
{"type": "seat_swap_request", "from_position": "compn", "from_display_name": "alice"}
{"type": "seat_swap_committed", "swaps": [["compn", "compe"], ["compe", "compn"]]}
{"type": "seat_swap_expired", "from_position": "compn"}
```

### `error` (single seat only)

```json
{"type": "error", "message": "card not in hand"}
```

Sent only to the seat that triggered. Followed by re-send of the most-recent prompt to the same seat.

### `room_resume` (reconnect / spectator attach)

For a reclaiming seat:
```json
{
  "type": "room_resume",
  "your_position": "compn",
  "your_hand": ["E6","R9", ...],
  "phase": "play",
  "scores": {"sn": 80, "ow": 60},
  "operator": "Eicheln",
  "variant": {"trumpf_bock": false, "match_bonus": true, "stoeck": true},
  "trick_so_far": [{"position": "compo", "card": "EA"}],
  "missed_tricks": [
    {"by": ["compo:E7","compn:R6","compe:RA","comps:E9"],
     "winner_position": "compe", "points": 18}
  ],
  "your_turn": false,
  "current_seat_turn": "comps"
}
```

For a spectator: `your_position: null`, `your_hand: null`, `your_turn: null`.

`missed_tricks` includes up to 3 most-recent completed tricks.

## Client → Server Messages

Same shape as today's single-WS protocol:

```json
{"type": "choose_trump", "operator": "Eicheln"}
{"type": "schieben"}
{"type": "play_card", "card": "E6"}
```

The server attributes each message to the WS that sent it (= that seat). Validation: right seat's turn, card in seat's hand, etc. Out-of-turn or invalid messages → `error` reply on the same seat's WS only.

## Reconnect & replay

**Disconnect detection:** Three converging paths:
1. `WebSocketDisconnect` raised in the WS reader task.
2. `await ws.send_json(...)` raises (broken pipe).
3. `receive_json()` raises any other exception.

**60-second grace:** On disconnect during play (not lobby), server broadcasts `seat_paused` with countdown. A reconnect timer fires after 60 s and converts the seat to AI (but retains `principal` ownership). Reconnecting before timeout cancels the timer and reclaims the seat.

**Spectators:** Simpler than seat reconnect: no timer, no AI takeover. WS drop removes the spectator; reconnecting requires another `/spectate` POST.

**Replay buffer:** On reconnect, `room_resume` includes `missed_tricks` (up to 3 most-recent completed tricks) so the client can catch up on missed plays.

**Ownership distinction:** Lost connection retains seat ownership (human can reclaim); explicit `/leave` call releases ownership (seat drops to AI immediately).

## Invariants

1. The server validates every client message against the current game state. Out-of-turn or invalid messages return `error` on the same seat's WS only, followed by re-send of the most-recent prompt.
2. Each seat sees only its own hand. Spectators see no hands.
3. Lifecycle events (`seat_paused`, `seat_reclaimed`, `seat_ai_takeover`, `host_changed`, etc.) broadcast to all seats + spectators.
4. The 60 s reconnect grace fires only on lost connections, not on explicit `/leave` calls.
5. After AI-takeover, the seat retains its `principal` so the original human can reclaim by reconnecting to `/ws/{code}`.

## When to Update This Skill

- A new message type is added to backend or frontend → add the type here first, then implement.
- A field is added/removed/renamed → update here, then update both sides.
- Semantics change (e.g., "`schieben_allowed` now also means X") → update the relevant prose.

Drift between code and this skill is a defect, caught in QA.
