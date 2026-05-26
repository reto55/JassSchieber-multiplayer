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

`winning_team` is `"sn"`, `"ow"`, or `"tie"`. Per Task 11 it is computed from the sum of declared (announced) weis points per team for THIS phase (tie → `"tie"`, no points awarded). Seats that declined or had no weis are omitted from `weis_by_position` (the field maps only declared positions to their announced weis lists).

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

`stoeck_team` ∈ `"sn" | "ow" | "both" | null`. `"both"` is the (rare but legal) case where both teams hold King + Ober of the trump suit and each scores +20; `null` means no team scored Stöck this spiel (Oben/Unten round, variant disabled, or no holder).

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
{"type": "spectator_count_changed", "count": 3}
```

`spectator_count_changed` is broadcast to all seats + spectators whenever a spectator joins (`POST /rooms/{code}/spectate`) or leaves (`POST /rooms/{code}/leave-spectator`). Lobby clients use it to refresh the displayed spectator count without polling.

### `error`

Two distinct, mutually exclusive shapes. The presence of a `reason` field is what marks an `error` as **fatal/terminal**.

**Validation error (non-fatal, single seat only)** — no `reason` field:
```json
{"type": "error", "message": "card not in hand"}
```

Sent only to the seat that triggered (out-of-turn, card not in hand, spectator write, internal error). Followed by re-send of the most-recent prompt to the same seat. The socket stays open.

**Fatal error (terminal, pre-close)** — carries a `reason` field:
```json
{"type": "error", "reason": "room_not_found", "message": "Dieser Raum existiert nicht mehr."}
```

Sent by `/ws/{code}` immediately **before** `websocket.close(code=1008, ...)`. There is NO prompt re-send — the socket closes right after. `reason` is one of exactly:

| `reason` | When | `message` (German) |
|----------|------|--------------------|
| `"no_auth"` | No valid session/guest cookie | `Nicht angemeldet. Bitte lade die Seite neu.` |
| `"room_not_found"` | `get_room(code)` returned `None` (expired/reaped/unknown code) | `Dieser Raum existiert nicht mehr.` |
| `"no_seat_slot"` | Principal owns neither a seat nor a spectator slot in this room | `Kein freier Platz in diesem Raum.` |

Rationale: Apache `mod_proxy_wstunnel` does not reliably forward the WS close *reason* to the browser, so the client cannot depend on `CloseEvent.reason` to distinguish a fatal room-gone close from a transient drop. The in-band `error` with `reason` gives the client a reliable signal to redirect (fatal) vs. auto-reconnect (transient). The `send_json` is wrapped in try/except so a send failure cannot crash the handler before the close.

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

### `chat_message` (broadcast)

Sent to all seats **and** spectators whenever a seated player sends a chat message.
Spectators receive it but cannot send chat (their WS is write-protected).

```json
{
  "type": "chat_message",
  "from_position": "comps",
  "from_name": "alice",
  "text": "Schönes Spiel!"
}
```

`from_position` is the sender's seat position (`"compo"` / `"compn"` / `"compe"` / `"comps"`).
`from_name` is `seat.display_name()` — the human's username/display name, or `"AI (position)"`.
`text` is server-truncated to 200 characters and stripped of leading/trailing whitespace.

## Client → Server Messages

Same shape as today's single-WS protocol:

```json
{"type": "choose_trump", "operator": "Eicheln"}
{"type": "schieben"}
{"type": "play_card", "card": "E6"}
```

**Chat** (seated players only; intercepted before the phase queue):
```json
{"type": "chat", "text": "Guet Glück!"}
```

Server broadcasts a `chat_message` to all seats + spectators. Spectators who attempt to send any message still receive `{"type": "error", "message": "spectators are read-only"}`.

`announce_weis` — reply to a `weis_request`:
```json
{"type": "announce_weis", "announce": true,  "weis": ["Dreier"]}
{"type": "announce_weis", "announce": true,  "weis": null}
{"type": "announce_weis", "announce": false}
```

Semantics:
- `announce=false` (or `weis=[]`) → seat declines; their entry is excluded from `weis_resolution.weis_by_position`.
- `announce=true` with `weis=null` (or missing) → announce ALL eligible weis from this seat's `your_weis`.
- `announce=true` with `weis=[<name>, ...]` → announce only the entries whose `name` matches; entries not in this seat's `your_weis` are dropped.
- Empty resulting set → seat is excluded from `weis_resolution.weis_by_position`.

A seat that received `your_weis: []` may reply with `{"type": "announce_weis", "announce": false}` (recommended) or skip silently — Task 11's multi-seat phase requires every seat to respond before broadcasting `weis_resolution`.

Legacy single-WS path (`/ws`): used `{"type": "declare_weis", "announce": bool, "weis": [...]}`. The multi-seat path standardises on `announce_weis`. Clients on `/ws/{code}` MUST use `announce_weis`.

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

**Fatal vs. transient close:** A `1008` close from `/ws/{code}` is always preceded by a fatal `error` (with `reason`, see the `error` section). The client must treat a close carrying one of those reasons as terminal (redirect, do not reconnect). Any other close (e.g. `1006` transient drop, gunicorn restart) has no preceding fatal `error` and is eligible for auto-reconnect, which restores state via `room_resume` on the seat-reclaim path.

## Invariants

1. The server validates every client message against the current game state. Out-of-turn or invalid messages return `error` on the same seat's WS only, followed by re-send of the most-recent prompt.
2. Each seat sees only its own hand. Spectators see no hands.
3. Lifecycle events (`seat_paused`, `seat_reclaimed`, `seat_ai_takeover`, `host_changed`, etc.) broadcast to all seats + spectators.
4. The 60 s reconnect grace fires only on lost connections, not on explicit `/leave` calls.
5. After AI-takeover, the seat retains its `principal` so the original human can reclaim by reconnecting to `/ws/{code}`.
6. Every fatal `1008` close from `/ws/{code}` is preceded by an `error` carrying a `reason` (`no_auth` | `room_not_found` | `no_seat_slot`); a validation `error` never carries `reason` and never precedes a close.

## When to Update This Skill

- A new message type is added to backend or frontend → add the type here first, then implement.
- A field is added/removed/renamed → update here, then update both sides.
- Semantics change (e.g., "`schieben_allowed` now also means X") → update the relevant prose.

Drift between code and this skill is a defect, caught in QA.
