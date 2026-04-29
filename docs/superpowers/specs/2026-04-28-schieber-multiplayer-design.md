# Schieber — Networked Multiplayer Design

**Date:** 2026-04-28
**Status:** Draft (pending user review before plan)
**Scope:** Sub-project A. Sub-projects B (user accounts) is done; sub-project C (AI difficulty) is independent.

## 1. Overview & Scope

### 1.1 Goal

Multiple humans on different machines play one Schieber game together via a shared private room. Identity comes from sub-project B (`AuthedUser` or `Guest`). Room state is in-memory single-instance; restart drops everything.

### 1.2 Decisions

| Question | Choice |
|---|---|
| Meeting model | Private rooms only, 6-char codes; no public matchmaking |
| AI fill | Dynamic — humans displace AI as they join (until "start" clicked, seats lock) |
| Disconnect handling | Pause 60 s, then AI takes over; reconnect reclaims the seat |
| State persistence | In-memory only; restart drops rooms |
| Spectators | TV mode (played cards + scores; no hands visible) |
| Variant settings | Per-room flags: `trumpf_bock`, `match_bonus`, `stoeck` |
| Reconnect-replay | Catch up on missed tricks (last 3) |
| Mid-game seat changes | Allowed (with rules — see §4) |
| Host transfer | Oldest-connected human becomes host |
| Multi-room | One principal can be in 2+ rooms simultaneously |
| Architecture | Approach A — extend `GameSession` in-place |

### 1.3 Stack additions

None. All Python stdlib + existing FastAPI + auth stack from sub-project B.

### 1.4 New files

- `ausbau/room.py` — room registry, code generation, `Seat` / `Spectator` / `Variant` dataclasses, lifecycle helpers.
- `ausbau/html5/lobby.html` — Jinja2 template for the lobby UI.

### 1.5 Touched files

- `ausbau/server.py` — new `/rooms/*` HTTP endpoints + new `/ws/{code}` WS endpoint replacing `/ws`.
- `ausbau/game_session.py` — significant extension: per-seat WS routing, per-seat hand redaction, AI-takeover state transitions, variant arithmetic, reconnect timers.
- `ausbau/html5/game.html` — game UI now bootstrapped from a room; lobby links.
- `ausbau/html5/js/schieber.js` — client-side room lifecycle, lobby state, per-seat rendering.
- `.claude/skills/schieber-protocol/SKILL.md` — protocol skill must be updated **before** any code change (per harness convention).

### 1.6 What stays untouched

- `Cards_refactored.py` (or `Cards.py`) and the rule-evaluation modules (`utils/card_utils.py`, `utils/game_utils.py`).
- `frontend/auth/*` (entire auth package — only `frontend/auth/deps.py` gains a `make_current_principal_dep` helper).
- All auth tests.
- The DB schema. Multiplayer adds zero tables.

### 1.7 Public surface added

```
POST   /rooms                          create a room (caller becomes host)
GET    /rooms/{code}                   inspect a room (any principal)
GET    /rooms/mine                     list rooms the caller is in
POST   /rooms/{code}/join              claim a seat (boots an AI)
POST   /rooms/{code}/leave             leave seat (or kick, if host in lobby)
POST   /rooms/{code}/spectate          join as spectator
POST   /rooms/{code}/leave-spectator   leave spectator slot
POST   /rooms/{code}/start             host-only; transitions to playing
POST   /rooms/{code}/seat              mid-game seat-swap request / accept
WS     /ws/{code}                      game socket; cookie identifies seat
```

Plus `/lobby?code=…` HTML page (Jinja).

---

## 2. Architecture

### 2.1 Module layout

```
ausbau/
  room.py                  ← NEW: registry, codes, Seat / Spectator / Variant,
                              create_room / get_room / remove_room
  game_session.py          ← EXTENDED: now accepts seat list + spectators;
                              previously single-WS, now multi-WS with per-seat
                              redaction and reconnect/AI-takeover flow
  server.py                ← NEW endpoints (above) + replaces /ws → /ws/{code}
  html5/
    game.html              ← Existing single-page game; gains lobby UI
    lobby.html             ← Standalone lobby page (Jinja2)
    js/schieber.js         ← Lobby state machine + per-seat rendering
```

### 2.2 Global state

```python
# ausbau/room.py
ROOMS: dict[str, "GameSession"] = {}     # 6-char code → live session
```

Single global dict, in-memory, fine for single-instance v1. Each `GameSession` owns an `asyncio.Lock` to serialise mutations from its multiple WSs.

### 2.3 Reaper

A startup-spawned task scans `ROOMS` every 60 s and removes rooms that:
- have `state == "finished"` for >5 min, OR
- have zero connected humans AND zero seated humans for >5 min.

Reaper closes any orphaned spectator WSs before deletion.

### 2.4 Configuration

No new env vars. Module constants in `ausbau/room.py`:
- `RECONNECT_GRACE_SECONDS = 60`
- `SEAT_SWAP_REQUEST_TTL_SECONDS = 30`
- `SPECTATOR_CAP_PER_ROOM = 20`
- `REAPER_INTERVAL_SECONDS = 60`
- `ROOM_FINISHED_LINGER_SECONDS = 300`
- `REPLAY_BUFFER_TRICK_COUNT = 3`

### 2.5 No DB changes

Game data is still anonymous — `spieler` table unchanged. Sub-project B was identity-only by design; multiplayer follows.

---

## 3. Room State Model

### 3.1 Principal type

```python
# Principal is either AuthedUser or Guest from sub-project B
from frontend.auth.models import User
from frontend.auth.guest import Guest

Principal = User | Guest

def principal_id(p: Principal) -> str:
    if isinstance(p, User):
        return p.id
    return f"guest:{p.guest_id}"
```

`principal_id` is the stable string used as a key in seat/spectator lookups. Distinct namespace for guest vs user prevents collisions.

### 3.2 Position

```python
POSITIONS = ('compo', 'compn', 'compe', 'comps')   # W, N, E, S
```

Teams: `(compo, compe)` is East-West (`ow`); `(compn, comps)` is North-South (`sn`).

### 3.3 Seat

```python
@dataclass
class Seat:
    position: str                                 # one of POSITIONS
    principal: Optional[Principal] = None         # None ⇒ AI bot
    websocket: Optional[WebSocket] = None         # None ⇒ disconnected
    is_ai: bool = True                            # True when principal is None
    reconnect_deadline: Optional[float] = None    # set on disconnect; cleared on reclaim
    connected_since: Optional[float] = None       # time.monotonic() of latest WS attach
    # Per-seat input queue, populated by the WS reader task; consumed by the game loop
    incoming: asyncio.Queue = field(default_factory=asyncio.Queue)
    # Per-seat condition for state transitions (paused → reclaimed, or paused → AI)
    state_event: asyncio.Event = field(default_factory=asyncio.Event)

    def display_name(self) -> str:
        if self.is_ai:
            return f"AI ({self.position})"
        if isinstance(self.principal, User):
            return self.principal.username
        if isinstance(self.principal, Guest):
            return self.principal.display_name
        return self.position
```

### 3.4 Spectator

```python
@dataclass
class Spectator:
    principal: Principal
    websocket: WebSocket
```

### 3.5 Variant

```python
@dataclass(frozen=True)
class Variant:
    trumpf_bock: bool = False     # 5x trump multiplier (off by default)
    match_bonus: bool = True      # +100 for taking all 9 tricks
    stoeck: bool = True           # +20 for König+Ober of trump
```

### 3.6 GameSession (extended)

Approach A keeps room and game in one class. Constructor:

```python
class GameSession:
    def __init__(
        self,
        *,
        code: str,
        host_principal_id: str,
        variant: Variant = Variant(),
        end_game: int = 1000,
    ):
        self.code = code
        self.variant = variant
        self.end_game = end_game

        # Lobby state
        self.host_principal_id = host_principal_id
        self.seats: list[Seat] = [Seat(position=POSITIONS[i]) for i in range(4)]
        self.spectators: list[Spectator] = []
        self.state: str = "lobby"                # 'lobby' | 'playing' | 'finished'

        # Game state (initialised when start() is called)
        self.point_sn: int = 0
        self.point_ow: int = 0
        self.current_play: Optional[Play] = None

        # Concurrency
        self._lock = asyncio.Lock()
        self._reconnect_tasks: dict[str, asyncio.Task] = {}
        self._game_task: Optional[asyncio.Task] = None

        # Replay buffer (last N completed tricks for reconnect_replay)
        self._completed_tricks: list[dict] = []

        # Mid-game seat-swap requests: {(from_pos, to_pos): expires_at}
        self._swap_requests: dict[tuple[str, str], float] = {}
```

### 3.7 Room registry

```python
# ausbau/room.py
import secrets

ROOMS: dict[str, "GameSession"] = {}

_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 0/O/1/I excluded


def make_code() -> str:
    while True:
        code = ''.join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
        if code not in ROOMS:
            return code


def create_room(*, host: Principal, variant: Variant) -> "GameSession":
    code = make_code()
    session = GameSession(
        code=code,
        host_principal_id=principal_id(host),
        variant=variant,
    )
    # Host claims seat 0 (compo)
    session.seats[0].principal = host
    session.seats[0].is_ai = False
    ROOMS[code] = session
    return session


def get_room(code: str) -> Optional["GameSession"]:
    return ROOMS.get(code.upper())


def remove_room(code: str) -> None:
    ROOMS.pop(code, None)


def find_rooms_for_principal(p: Principal) -> list[dict]:
    pid = principal_id(p)
    out = []
    for room in ROOMS.values():
        for seat in room.seats:
            if seat.principal and principal_id(seat.principal) == pid:
                out.append({"code": room.code, "role": "seat",
                            "position": seat.position, "state": room.state})
                break
        else:
            for spec in room.spectators:
                if principal_id(spec.principal) == pid:
                    out.append({"code": room.code, "role": "spectator",
                                "state": room.state})
                    break
    return out
```

---

## 4. HTTP API Surface

All `/rooms/*` routes return JSON unless noted. State-changing routes require `X-Requested-With: schieber` header (CSRF, per sub-project B). Auth: every route requires either `schieber_session` or `schieber_guest` cookie. The `current_principal` dependency yields a `User` or `Guest` (issuing a fresh guest cookie if neither cookie present).

### 4.1 `current_principal` dependency

Add `make_current_principal_dep(get_session)` to `frontend/auth/deps.py`. Resolution order: valid `schieber_session` → `User`; valid `schieber_guest` → `Guest`; neither → mint guest cookie + return new `Guest`.

### 4.2 Endpoints

```
POST /rooms                            {variant: {trumpf_bock?, match_bonus?, stoeck?}}
                                        → 201 {code, room_state}
                                        host = caller; auto-claims seat 0;
                                        seats 1-3 are AI by default

GET  /rooms/{code}                     → 200 {room_state}
                                        → 404 if no such room

GET  /rooms/mine                       → 200 [{code, role, position?, state}, ...]
                                        rooms in which caller is seated or spectating

POST /rooms/{code}/join                {seat?: int}
                                        → 200 {seat: int, room_state}
                                        → 409 if room full / state != 'lobby'
                                        → 410 if room state == 'finished'
                                        seat omitted ⇒ first AI seat

POST /rooms/{code}/leave               {target_position?: str}
                                        → 204
                                        - if target_position omitted: caller leaves own seat
                                          - lobby: AI refills; if host, host transfers
                                          - mid-game: AI takes over immediately, NO 60s grace
                                        - if target_position set: kick (host-only, lobby only).
                                          400 if mid-game; 403 if not host

POST /rooms/{code}/spectate            → 200 {room_state}
                                        → 409 if caller already has a seat
                                        → 503 if spectator cap reached

POST /rooms/{code}/leave-spectator     → 204

POST /rooms/{code}/start               → 204
                                        → 403 if not host
                                        → 409 if state != 'lobby'
                                        locks seats; transitions state='playing';
                                        starts the game loop background task

POST /rooms/{code}/seat                {to: int, accept?: bool}
                                        → 200 {room_state}
                                        - mid-game seat swap (humans only).
                                          See §4.3 for protocol.

WS   /ws/{code}                        cookie required.
                                        - if principal owns a seat: attach WS,
                                          cancel reconnect timer (if any).
                                        - else if in spectator list: attach WS.
                                        - else: close 1008 "no seat or spectator slot"
```

### 4.3 Mid-game seat swap protocol

1. Player A (seat `compn`) wants to swap with player B (seat `compe`).
2. A calls `POST /rooms/{code}/seat` with body `{to: 2}` (compe index).
3. Server records request `(compn, compe)` with TTL = `SEAT_SWAP_REQUEST_TTL_SECONDS`. Server pushes `seat_swap_request` to B's WS:
   ```json
   {"type": "seat_swap_request", "from_position": "compn", "from_display_name": "alice"}
   ```
4. B accepts via `POST /rooms/{code}/seat` with body `{to: 1, accept: true}` (compn index, accepting alice's offer).
5. Swap takes effect at the next trick boundary — server waits for the current trick to complete, then atomically swaps the two seats' principals + WSs + hands. Scores stay attached to teams (NS / EW).
6. Server broadcasts `seat_swap_committed`:
   ```json
   {"type": "seat_swap_committed", "swaps": [["compn", "compe"], ["compe", "compn"]]}
   ```
7. If TTL expires before B accepts, request is dropped; B's WS receives `seat_swap_expired`.

Restrictions:
- Both seats must be human (no human↔AI swaps).
- Both players must be currently connected (no swapping with a paused seat).
- Concurrent swap requests from the same `from_position` overwrite earlier ones (last-write-wins).

### 4.4 Variant + end_game

`POST /rooms` body:

```json
{"variant": {"trumpf_bock": false, "match_bonus": true, "stoeck": true}}
```

All variant fields optional; defaults from §3.5. `end_game` is locked at 1000 in v1.

### 4.5 Room state JSON

```json
{
  "code": "ABCDEF",
  "host_principal_id": "guest:deadbeef..." or "<user-uuid>",
  "state": "lobby" | "playing" | "finished",
  "variant": {"trumpf_bock": false, "match_bonus": true, "stoeck": true},
  "end_game": 1000,
  "seats": [
    {"position": "compo", "display_name": "alice",        "is_ai": false, "connected": true,
     "is_host": true,  "principal_id": "<uuid>"},
    {"position": "compn", "display_name": "bob",          "is_ai": false, "connected": false,
     "is_host": false, "principal_id": "guest:..."},
    {"position": "compe", "display_name": "AI (compe)",   "is_ai": true,  "connected": true,
     "is_host": false, "principal_id": null},
    {"position": "comps", "display_name": "Guest-3f9a",   "is_ai": false, "connected": true,
     "is_host": false, "principal_id": "guest:..."}
  ],
  "spectator_count": 0,
  "scores": {"sn": 0, "ow": 0}
}
```

### 4.6 Lobby HTML page

`GET /lobby?code=ABCDEF` returns a Jinja2 template (`ausbau/html5/lobby.html`) that:
- Renders the room state inline (seats with display names, host marker, AI flags).
- Offers Join / Leave / Spectate / Start buttons (host-only ones gated by `is_host`).
- Vanilla `fetch()` for state-changing endpoints with `X-Requested-With: schieber`.
- Vanilla WS to `/ws/{code}` once seated; switches the page to `game.html`-equivalent rendering.

The page is one Jinja file (~80 LoC HTML+JS).

---

## 5. WS Protocol Changes

The protocol skill (`.claude/skills/schieber-protocol/SKILL.md`) must be updated **before** code changes. This section is the authoritative source for the new protocol.

### 5.1 Routing helpers (added to GameSession)

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

### 5.2 Server → client messages

#### 5.2.1 `game_start` (broadcast_per_seat)

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

#### 5.2.2 `trump_request` / `trump_pending` / `trump_chosen`

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

#### 5.2.3 `weis_request` / `weis_resolution`

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

#### 5.2.4 `play_request` / `play_pending` / `card_played`

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

#### 5.2.5 `trick_end` / `spiel_end` / `game_end`

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

#### 5.2.6 Lifecycle events (broadcast)

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

#### 5.2.7 `error` (single seat only)

```json
{"type": "error", "message": "card not in hand"}
```

Sent only to the seat that triggered. Followed by re-send of the most-recent prompt to the same seat.

#### 5.2.8 `room_resume` (reconnect / spectator attach)

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

`missed_tricks` includes up to `REPLAY_BUFFER_TRICK_COUNT` (= 3) most-recent completed tricks.

### 5.3 Client → server messages

Same shape as today's single-WS protocol:

```json
{"type": "choose_trump", "operator": "Eicheln"}
{"type": "schieben"}
{"type": "play_card", "card": "E6"}
```

The server attributes each message to the WS that sent it (= that seat). Validation: right seat's turn, card in seat's hand, etc. Out-of-turn or invalid messages → `error` reply on the same seat's WS only.

### 5.4 Protocol skill update (precondition for code changes)

`.claude/skills/schieber-protocol/SKILL.md` must be rewritten for the multi-WS protocol BEFORE any backend or frontend code changes. This is Task 0 of the implementation plan.

---

## 6. Reconnect Mechanics

### 6.1 Disconnect detection

Three converging paths into `_disconnect_seat(position)`:
1. `WebSocketDisconnect` raised in the WS reader task.
2. `await ws.send_json(...)` raises (broken pipe).
3. `receive_json()` raises any other exception.

### 6.2 `_disconnect_seat`

```python
async def _disconnect_seat(self, position: str) -> None:
    seat = self._seat(position)
    if seat.is_ai or seat.websocket is None:
        return  # already disconnected or AI
    try:
        await seat.websocket.close()
    except Exception:
        pass
    seat.websocket = None
    seat.connected_since = None

    if self.state == "lobby":
        # No grace in lobby; drop seat to AI immediately
        was_host = (principal_id(seat.principal) == self.host_principal_id) if seat.principal else False
        seat.principal = None
        seat.is_ai = True
        seat.reconnect_deadline = None
        await self.broadcast({
            "type": "seat_changed",
            "seat": self._seat_to_dict(seat),
            "reason": "disconnect",
        })
        if was_host:
            await self._transfer_host()
        return

    # Mid-game: 60s grace
    seat.reconnect_deadline = time.monotonic() + RECONNECT_GRACE_SECONDS
    await self.broadcast({
        "type": "seat_paused",
        "position": position,
        "reconnect_deadline_secs": RECONNECT_GRACE_SECONDS,
        "display_name": seat.display_name(),
    })
    self._reconnect_tasks[position] = asyncio.create_task(
        self._reconnect_timeout(position)
    )
    seat.state_event.set()  # wake any awaiters
```

### 6.3 `_reconnect_timeout`

```python
async def _reconnect_timeout(self, position: str) -> None:
    try:
        await asyncio.sleep(RECONNECT_GRACE_SECONDS)
    except asyncio.CancelledError:
        return
    seat = self._seat(position)
    if seat.websocket is not None:
        return  # raced; reclaimed
    # Flip to AI but KEEP seat.principal — this lets the disconnected human
    # reclaim the seat later (during the same room lifetime) by reconnecting
    # to /ws/{code}. _seat_for_principal must find the seat, so principal stays.
    # Only websocket and reconnect_deadline are cleared. is_ai=True ensures the
    # game loop uses ai_select_action, not the (absent) WS, for further moves.
    seat.is_ai = True
    seat.reconnect_deadline = None
    self._reconnect_tasks.pop(position, None)
    await self.broadcast({"type": "seat_ai_takeover", "position": position})
    seat.state_event.set()
```

After an AI-takeover, the seat's `principal` is still the original human — the seat is "owned" by them but currently played by AI. A reconnect to `/ws/{code}` from that principal lands in `_seat_for_principal`, finds the seat, and `_reclaim_seat` flips `is_ai=False` and re-attaches their WS.

If the seat is explicitly leftvia `POST /rooms/{code}/leave`, that path DOES clear `principal` (the leaver gives up ownership). The distinction: lost connection retains seat ownership; explicit leave releases it.

### 6.4 `_reclaim_seat` (called from WS endpoint)

```python
async def _reclaim_seat(self, position: str, ws: WebSocket, principal: Principal) -> None:
    seat = self._seat(position)
    task = self._reconnect_tasks.pop(position, None)
    if task is not None and not task.done():
        task.cancel()
    seat.principal = principal
    seat.is_ai = False
    seat.websocket = ws
    seat.reconnect_deadline = None
    seat.connected_since = time.monotonic()
    await ws.send_json(self._room_resume_message_for(position))
    await self.broadcast(
        {"type": "seat_reclaimed", "position": position, "display_name": seat.display_name()},
        except_seat=position,
    )
    seat.state_event.set()
```

### 6.5 Game loop interaction

The phase loops (`_trump_phase`, `_weis_phase`, `_play_trick`) wait for input through `_await_seat_action`:

```python
async def _await_seat_action(self, position: str, valid_actions: dict) -> dict:
    seat = self._seat(position)
    while True:
        if seat.is_ai:
            return self._compute_ai_action(seat, valid_actions)
        if seat.websocket is None:
            # Disconnected; either reclaim or AI takeover will set state_event
            seat.state_event.clear()
            await seat.state_event.wait()
            continue
        try:
            msg = await self._wait_for_seat_message(position, valid_actions)
            return msg
        except WebSocketDisconnect:
            await self._disconnect_seat(position)
            continue
```

`_wait_for_seat_message` consumes from `seat.incoming` queue (populated by the WS reader task) and validates against `valid_actions`. Invalid messages → `error` reply + re-send prompt + loop.

### 6.6 Edge cases

- All 4 humans disconnect simultaneously → 4 timers fire, all 4 seats become AI. Game continues with AIs. After spiel ends with no humans connected, room is reaped.
- Reconnect arrives just as timer fires → race resolved by `seat.websocket is None` re-check after `asyncio.sleep`.
- Host disconnects mid-game → 60 s grace as for any seat. After timeout, AI takes over AND host transfers.
- Reconnect to a finished game → `room_resume` with `phase: "finished"`.
- Server restart during a paused seat → game lost. Client shows "lost connection" and offers a fresh room.

---

## 7. Variant Settings

Three flags, set per-room at creation, immutable thereafter.

### 7.1 `trumpf_bock` (5x trump multiplier)

**Default: false.** When true, every trick in a trump-mode round is multiplied by 5.

Implementation: per-trick scoring helper returns `pts * 5` when `operator in SUITS` and `variant.trumpf_bock`. No-op for `Oben` / `Unten`.

```python
def trick_points(cards, operator: str, *, trumpf_bock: bool) -> int:
    pts = sum(_card_value(c, operator) for c in cards)
    if trumpf_bock and operator in SUITS:
        pts *= 5
    return pts
```

Multiplier applies to per-trick total only — NOT to weis or stoeck.

### 7.2 `match_bonus` (+100 for 9-of-9)

**Default: true.** If one team wins all 9 tricks in a single spiel and `match_bonus` is true, +100 to that team's spiel score.

```python
if self.variant.match_bonus and self._all_9_tricks_one_team(trick_winners):
    if winning_team == "sn": sn_spiel_pts += 100
    else: ow_spiel_pts += 100
```

The existing "+5 for last trick" bonus is unchanged — separate rule.

### 7.3 `stoeck` (+20 for König+Ober of trump)

**Default: true.** When true, the existing `detect_stock` logic awards +20 to the holding player's team. When false, no bonus, no detection.

```python
if self.variant.stoeck:
    sn_stoeck, ow_stoeck = self._detect_stoeck_team(play, operator)
    if sn_stoeck: sn_spiel_pts += 20
    if ow_stoeck: ow_spiel_pts += 20
```

### 7.4 Spec / message exposure

Variant flags appear in:
- Room state JSON (§4.5)
- `game_start` (§5.2.1)
- `spiel_end`'s `match` field (§5.2.5)

### 7.5 Server-only arithmetic

All variant calculations server-side. Client only renders.

### 7.6 Lobby UI

Three checkboxes in `lobby.html`. Defaults: match=on, stoeck=on, bock=off. Locked at room creation.

### 7.7 Out of scope (future variant specs)

Slalom, Misère, Differenzler / Coiffeur full menu, configurable end_game.

---

## 8. Host Transfer

### 8.1 Host privileges

| Action | Host-only | Anyone |
|---|---|---|
| Create room | (caller becomes host) | — |
| Start game | ✓ | — |
| Set variant (at creation) | ✓ | — |
| Kick (lobby only) | ✓ | — |
| Join / leave / spectate | — | ✓ |
| Play own seat | — | ✓ (own seat only) |
| Trigger seat-swap with another human | — | ✓ |

### 8.2 Transfer triggers

- Host disconnects in lobby → immediate transfer.
- Host disconnects mid-game → 60 s reconnect grace; transfer triggers if AI-takeover fires.
- Host calls `/leave` → immediate transfer before leave completes.

### 8.3 Transfer rule

**Oldest-connected human becomes host.** Among seats currently held by a connected human (`is_ai=False AND websocket is not None`), pick the one with the smallest `connected_since`. Tie-break: alphabetical `principal_id`.

If no humans are currently connected, host transfer is deferred — room temporarily has no host. Lobby actions that require a host return 409 "no host" until a human reconnects.

### 8.4 Kick

`POST /rooms/{code}/leave` with `target_position` set:
- Caller must be host (else 403).
- Room must be in lobby state (else 400).
- Drops target seat back to AI; broadcasts `seat_kicked`.
- Target's WS receives close 1008 with reason "kicked from room".

Mid-game kicks are not allowed.

### 8.5 Transfer message

```json
{"type": "host_changed", "old_host_position": "compn", "new_host_position": "compo", "new_host_display_name": "alice"}
```

Broadcast on every transfer (including AI-takeover-triggered transfer).

### 8.6 Edge cases

- All humans disconnect → no host; lobby actions blocked. First reconnect becomes host.
- All humans leave the lobby → empty room, reaped on next cycle.
- Host kicks themselves (target_position = own seat) → treated as ordinary leave.
- Two humans race to leave → handled in order under `_lock`.

---

## 9. Spectator Mechanics

### 9.1 Joining

`POST /rooms/{code}/spectate` adds caller to `room.spectators`. 409 if caller already has a seat. 503 if cap reached. Then client opens `/ws/{code}` to start receiving live events.

### 9.2 Leaving

`POST /rooms/{code}/leave-spectator` removes from list and closes the WS server-side. Closing the WS without the endpoint also works.

### 9.3 WS lifecycle

```python
# Inside /ws/{code}, after principal resolved:
seat = self._seat_for_principal(principal)
if seat is not None:
    await self._reclaim_seat(seat.position, ws, principal)
elif spec := self._spectator_for_principal(principal):
    spec.websocket = ws
    await ws.send_json(self._room_resume_message_for(None))
else:
    await ws.close(code=1008, reason="no seat or spectator slot")
```

### 9.4 What spectators see

TV mode (Q7=a):
- All broadcasts (`card_played`, `trick_end`, `spiel_end`, `game_end`, `trump_chosen`, `weis_resolution`, `*_pending`).
- All lifecycle events (`seat_paused`, `seat_reclaimed`, `seat_ai_takeover`, `host_changed`, `seat_kicked`).
- `room_resume` with `your_position: null`, `your_hand: null`.

Spectators do NOT see: `your_hand`, `play_request`, `trump_request`, `weis_request`, or `error`.

### 9.5 Privacy

Room state JSON exposes `spectator_count` only — no names. Lobby UI does not list spectators.

### 9.6 Read-only

Spectators cannot send game messages. Any incoming WS message is replied with `error: spectators are read-only`. Chat is deferred from v1.

### 9.7 Spectator reconnect

Simpler than seat reconnect: no timer, no AI takeover. WS drop removes the spectator. Reconnecting requires another `/spectate` POST.

### 9.8 Capacity

Soft cap: `SPECTATOR_CAP_PER_ROOM = 20`. Past cap, `/spectate` returns 503.

---

## 10. Multi-Room Support

### 10.1 Independence

Rooms are isolated. A principal may be in 2+ rooms simultaneously; each `/ws/{code}` is independent.

### 10.2 No global principal-to-room map

Lookup uses `find_rooms_for_principal(principal)` which scans `ROOMS.values()`. O(N) over rooms; N capped by single-instance constraint.

### 10.3 `/rooms/mine`

```
GET /rooms/mine
  → 200 [
      {"code": "ABCDEF", "role": "seat", "position": "compn", "state": "playing"},
      {"code": "GHIJKL", "role": "spectator", "state": "lobby"}
    ]
```

Used by lobby home page to show active rooms.

### 10.4 Cross-room interactions

None. Events in room A don't reach room B even with the same principal in both.

### 10.5 Notification

No cross-room "your turn" notifications in v1.

### 10.6 Seat swap and multi-room

Swap requests scoped to the originating room.

### 10.7 Disconnect timer per room

Each room runs its own reconnect timer per seat. Reconnecting to room A only reclaims room-A seat; room B requires a separate `/ws/{B}` connection.

### 10.8 Multi-room and host

Host of A is just a player in B. No privilege bleed.

### 10.9 No per-principal cap

A principal can be in 50 rooms if they want.

---

## 11. Testing Strategy

### 11.1 Test layout

```
tests/multiplayer/
  __init__.py
  conftest.py                   ← fake WS, fast-clock, in-memory ROOMS reset per test
  test_room_lifecycle.py        ← create / join / leave / start / finish
  test_room_codes.py            ← code generation, collisions, lookup
  test_seat_assignment.py       ← AI fill, human displaces AI, kick
  test_host_transfer.py         ← disconnect → transfer; oldest-connected rule
  test_variants.py              ← trumpf_bock, match_bonus, stoeck arithmetic
  test_per_seat_redaction.py    ← game_start sends only own hand; spectators see none
  test_disconnect_reconnect.py  ← 60s timer, AI takeover, reclaim cancels timer
  test_seat_swap.py             ← human↔human two-step accept, expiry, AI rejected
  test_spectator.py             ← TV mode, no hands, cap, double-attempt 409
  test_multi_room.py            ← same principal in 2 rooms, /rooms/mine, isolation
  test_protocol_messages.py     ← every server-pushed message has expected JSON shape
```

### 11.2 FakeWebSocket

```python
class FakeWebSocket:
    def __init__(self):
        self.sent: list[dict] = []
        self.incoming: asyncio.Queue = asyncio.Queue()
        self.cookies: dict = {}
        self.closed = False
        self.close_code: int | None = None

    async def accept(self): pass
    async def send_json(self, msg): self.sent.append(msg)
    async def receive_json(self): return await self.incoming.get()
    async def close(self, code=1000, reason=""):
        self.closed = True
        self.close_code = code

    def push(self, msg): self.incoming.put_nowait(msg)
    def last_sent_of_type(self, t):
        return next((m for m in reversed(self.sent) if m["type"] == t), None)
```

Tests use this to inject and assert WS traffic. Production WS is FastAPI's `WebSocket` with the same surface.

### 11.3 Fast-clock

```python
@pytest.fixture
def fast_clock(monkeypatch):
    real_sleep = asyncio.sleep
    async def fake_sleep(seconds):
        await real_sleep(0)
    monkeypatch.setattr("asyncio.sleep", fake_sleep)
```

Scoped to tests that need timer-acceleration. The 60 s reconnect timer fires in <1 ms.

### 11.4 Coverage

**State invariants:** room creation, AI fill, displacement, lobby/playing/finished transitions, locked seats post-start.

**Per-seat redaction:** `game_start.your_hand` per seat; spectator hand-null; `play_request` only to active seat; `play_pending` to others.

**Variant arithmetic:** `match_bonus=true` 9-of-9 NS → +100 NS; `match_bonus=false` 9-of-9 NS → no bonus; `trumpf_bock=true` Eicheln trick → 5x; `trumpf_bock=false` Eicheln trick → 1x; `stoeck=true` NS holds K+O → +20; `stoeck=false` → no.

**Disconnect / reconnect:** timer fires after 60 s (fast-clock), seat → AI; reclaim before timeout cancels timer; reclaim after AI takeover restores human seat.

**Multi-room:** same principal in two rooms; disconnect from A doesn't trigger pause in B; `/rooms/mine` returns both with correct roles.

### 11.5 Don't test

- Real WS handshake (FastAPI's responsibility).
- Real network drops.
- Browser DOM (lobby is a Jinja template — render-only smoke).
- Cross-instance state.

### 11.6 Manual smoke checklist (before deploys)

- 4 humans (4 logins, 4 tabs): create → join → start → play 1 round → spiel_end → game_end. All 4 see consistent scores at every event.
- 1 human + 3 AI: full round, score correctness.
- Disconnect mid-trick: close a tab → other 3 see `seat_paused` → 60 s → see `seat_ai_takeover` → reconnect → see `seat_reclaimed`.
- Host transfer: host closes tab → another human becomes host (host-only buttons appear).
- Seat swap mid-game: A requests, B accepts → swap commits at trick boundary → both have correct hands.
- Spectator: 5th human spectates 4-human game → sees plays, no hands.
- Multi-room: same login in 2 rooms in 2 tabs → both work; disconnect one doesn't affect the other.
- Variants: room with `trumpf_bock=true, match_bonus=false` → confirm 5x trump scoring + no match bonus.

### 11.7 CI assumption

`python run_tests.py` runs the multiplayer suite alongside everything else. No live WS, no live browser.

---

## 12. Out of Scope

### 12.1 Deferred from v1 (Q5)

- In-room chat (text or quick-emote)
- Per-game persisted stats
- Configurable end_game per room (locked at 1000)
- Public room directory

### 12.2 Architectural deferrals (Q6)

- Multi-instance / horizontally scaled
- Redis or DB-backed room state
- Restart resilience for in-progress games

### 12.3 Variant deferrals (§7.7)

Slalom, Misère, Differenzler / Coiffeur full menu, configurable end_game.

### 12.4 Spectator deferrals (§9)

Spectator chat, spectator-as-ghost-of-player POV mode, spectator names broadcast.

### 12.5 Multi-room deferrals (§10)

Cross-room "your turn" notifications, per-principal room-membership cap.

### 12.6 Linkage to sub-project C (AI difficulty)

Each AI seat (`Seat.is_ai = True`) calls a configurable `ai_select_action(seat, game_state)` function. v1 uses today's `ai_select_card` (lead=high / follow=low). Sub-project C will add a `Seat.ai_difficulty: str | None` field and a strength-aware `ai_select_action`. No other multiplayer code changes.

### 12.7 Linkage to sub-project B (accounts, done)

Multiplayer uses `current_principal` (User or Guest). No new auth concerns. No new DB tables. Multi-room works because guest cookies persist 30 days and authed cookies are server-issued — same principal has same id across tabs.

### 12.8 Far future

Tournament mode (best-of-N rooms, brackets), save/replay completed games, voice chat, friend list, per-user game history dashboard (depends on §12.1 stats).
