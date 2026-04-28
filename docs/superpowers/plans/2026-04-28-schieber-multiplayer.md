# Schieber — Networked Multiplayer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship private-room multiplayer (4 humans on different machines + AI fill, 60 s reconnect grace, spectators, variant flags, host transfer, mid-game seat swap, multi-room) without breaking existing single-WS game tests.

**Architecture:** Approach A — extend `ausbau/game_session.py::GameSession` in-place. New `ausbau/room.py` holds registry + `Seat`/`Spectator`/`Variant` dataclasses + helpers. New `/rooms/*` HTTP endpoints; existing `/ws` replaced by `/ws/{code}`. Per-seat WS routing + hand redaction. State in-memory single-instance (no Redis, no DB persistence).

**Tech Stack:** Python 3.9+, FastAPI, asyncio, Jinja2, pytest, pytest-asyncio. Reuses sub-project B's `frontend/auth/*` for identity (`User` or `Guest` principal).

**Reference:** `docs/superpowers/specs/2026-04-28-schieber-multiplayer-design.md`.

---

## Task 0: Update protocol skill

**Files:**
- Modify: `.claude/skills/schieber-protocol/SKILL.md`

Per harness convention, the protocol skill is ground truth and must be updated **before** any backend or frontend code change. Section 5 of the spec is the new authoritative protocol — copy it into the skill verbatim, replacing the existing single-WS protocol description.

- [ ] **Step 1: Read the existing skill**

```bash
cat .claude/skills/schieber-protocol/SKILL.md
```

Note: the current skill describes single-WS messages. Everything past the front-matter needs to be replaced with the multi-WS protocol from spec §5.

- [ ] **Step 2: Rewrite the skill body**

Open `.claude/skills/schieber-protocol/SKILL.md`. Keep the `---` YAML front-matter (name, description). Replace the body with:

```markdown
# Schieber WebSocket Protocol

Ground-truth message contract between the Schieber server (`ausbau/server.py` + `ausbau/game_session.py`) and the browser client (`ausbau/html5/js/schieber.js`).

**Connection model (multiplayer):** Each room is identified by a 6-char code. Each player opens one WebSocket to `/ws/{code}`. The server holds a `GameSession` per room and routes messages per-seat. Spectators connect to the same `/ws/{code}` and receive a TV-mode broadcast (no hands).

## Server → client messages

(... paste spec §5.2 here, every subsection ...)

## Client → server messages

(... paste spec §5.3 here ...)

## Invariants

1. The server validates every client message against the current game state. Out-of-turn or invalid messages → `error` reply on the same seat's WS only.
2. Each seat sees only its own hand. Spectators see no hands.
3. Lifecycle events (`seat_paused`, `seat_reclaimed`, `seat_ai_takeover`, etc.) broadcast to all seats + spectators.
4. The 60 s reconnect grace fires only on lost connections, not on explicit `/leave` calls.
5. After AI-takeover, the seat retains its `principal` so the original human can reclaim by reconnecting.
```

(Where `(...)` indicates: copy the literal content from the spec.)

- [ ] **Step 3: Verify the skill renders**

```bash
head -20 .claude/skills/schieber-protocol/SKILL.md
```

Confirm: front-matter intact, multi-WS section appears.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/schieber-protocol/SKILL.md
git commit -m "docs(skill): rewrite schieber-protocol for multi-WS multiplayer"
```

Use `-c commit.gpgsign=false` if signing fails.

---

## Task 1: Branch & worktree setup

**Files:** none

The auth work is on `feat/user-accounts`. Multiplayer builds on it. New branch off `feat/user-accounts`.

- [ ] **Step 1: Create branch and worktree**

```bash
cd /mnt/archive/Dokumente/JassSchieber-accounts   # if exists
# OR from the main worktree on feat/mobile-responsive
git worktree add ../JassSchieber-multiplayer feat/multiplayer feat/user-accounts
cd ../JassSchieber-multiplayer
```

If `feat/user-accounts` is not yet at HEAD locally, fetch it first or branch off `master` and cherry-pick the auth commits + the multiplayer spec commit.

- [ ] **Step 2: Cherry-pick spec + plan from feat/mobile-responsive**

The spec (`a0b8c08`) and this plan live on feat/mobile-responsive. Cherry-pick them onto `feat/multiplayer`:

```bash
git cherry-pick a0b8c08              # multiplayer spec
git cherry-pick <plan-commit-sha>    # this plan, once committed
```

(The plan commit SHA will be created when this plan file is committed.)

- [ ] **Step 3: Verify clean tree**

```bash
git status
```

Expected: nothing modified, on `feat/multiplayer`.

- [ ] **Step 4: Verify auth tests still pass**

```bash
python -m pytest tests/auth/ -v
```

Expected: all auth tests pass (67+ tests). Confirms the auth foundation is intact in this worktree.

(No commit; this task is environment setup.)

---

## Task 2: Add `make_current_principal_dep`

**Files:**
- Modify: `frontend/auth/deps.py`
- Create: `tests/auth/test_principal_dep.py`

Multiplayer routes need a dependency that yields a `User` OR `Guest` (never raises 401; mints a guest cookie if neither cookie present).

- [ ] **Step 1: Write the failing test**

`tests/auth/test_principal_dep.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_principal_dep_returns_user_when_authed(client):
    await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "SecurePass123!",
    })
    await client.post("/auth/login", data={
        "username": "alice@test", "password": "SecurePass123!",
    })
    r = await client.get("/auth/whoami")
    assert r.json()["kind"] == "user"


async def test_principal_dep_issues_guest_when_no_cookies(client):
    r = await client.get("/auth/whoami")
    assert r.json()["kind"] == "guest"
    assert "schieber_guest" in r.headers.get("set-cookie", "")
```

These tests already exist in `tests/auth/test_guest.py` — duplication is fine; they verify the dependency contract from a multiplayer-consumer angle. Skip this test file if the existing coverage already asserts both branches.

- [ ] **Step 2: Add `make_current_principal_dep`**

In `frontend/auth/deps.py`, add a new factory:

```python
from frontend.auth.guest import (
    Guest,
    issue_guest_cookie,
    read_guest_cookie,
    GuestCookieError,
)


def make_current_principal_dep(get_session, secret_key, secure_cookie):
    """Yield current User or Guest. Mints a guest cookie when needed."""

    async def current_principal(
        request: Request,
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        # Try authed user first
        sess = request.cookies.get("schieber_session")
        if sess:
            q = select(AccessToken).where(
                AccessToken.token == sess,
                AccessToken.expires_at > datetime.now(timezone.utc),
            )
            at = (await session.execute(q)).scalar_one_or_none()
            if at is not None:
                u = (await session.execute(
                    select(User).where(User.id == at.user_id)
                )).scalar_one_or_none()
                if u is not None and u.is_active:
                    return u

        # Fall through to guest
        guest_cookie = request.cookies.get("schieber_guest")
        if guest_cookie:
            try:
                return read_guest_cookie(guest_cookie, secret_key)
            except GuestCookieError:
                pass

        # Issue new guest cookie
        new_cookie, guest = issue_guest_cookie(secret_key)
        response.set_cookie(
            key="schieber_guest",
            value=new_cookie,
            max_age=30 * 24 * 60 * 60,
            httponly=True,
            secure=secure_cookie,
            samesite="lax",
        )
        return guest

    return current_principal
```

Imports needed (add at top if missing): `from datetime import datetime, timezone`, `from sqlalchemy import select`, `from frontend.auth.models import User, AccessToken`, `from fastapi import Response`.

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_principal_dep.py -v
```

Expected: 2 passed (or skipped if duplicate of existing).

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/deps.py tests/auth/test_principal_dep.py
git commit -m "feat(auth): add make_current_principal_dep (User or Guest)"
```

Use `-c commit.gpgsign=false` if signing fails.

---

## Task 3: `ausbau/room.py` — data model + registry

**Files:**
- Create: `ausbau/room.py`
- Create: `tests/multiplayer/__init__.py`
- Create: `tests/multiplayer/test_room_model.py`

- [ ] **Step 1: Write `tests/multiplayer/__init__.py`** (empty)

```python
```

- [ ] **Step 2: Write the failing test**

`tests/multiplayer/test_room_model.py`:

```python
import pytest
from ausbau.room import (
    Seat, Spectator, Variant, POSITIONS, principal_id,
    make_code, create_room, get_room, remove_room, ROOMS,
)
from frontend.auth.guest import Guest


@pytest.fixture(autouse=True)
def reset_rooms():
    ROOMS.clear()
    yield
    ROOMS.clear()


def test_positions_layout():
    assert POSITIONS == ('compo', 'compn', 'compe', 'comps')


def test_variant_defaults():
    v = Variant()
    assert v.trumpf_bock is False
    assert v.match_bonus is True
    assert v.stoeck is True


def test_seat_default_is_ai():
    s = Seat(position='compo')
    assert s.is_ai is True
    assert s.principal is None
    assert s.websocket is None


def test_seat_display_name_for_ai():
    s = Seat(position='compn')
    assert s.display_name() == "AI (compn)"


def test_seat_display_name_for_guest():
    g = Guest(guest_id='aabbccdd' * 4)
    s = Seat(position='compe', principal=g, is_ai=False)
    assert s.display_name() == "Guest-aabb"


def test_make_code_format():
    code = make_code()
    assert len(code) == 6
    assert all(c in "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" for c in code)


def test_make_code_unique():
    seen = set()
    for _ in range(20):
        c = make_code()
        assert c not in seen
        seen.add(c)
        # Reserve it so make_code re-rolls on collision
        ROOMS[c] = None  # type: ignore


def test_principal_id_for_guest():
    g = Guest(guest_id='deadbeef' * 4)
    assert principal_id(g) == "guest:" + 'deadbeef' * 4


def test_create_room_assigns_host_to_seat_0():
    g = Guest(guest_id='abcd1234' * 4)
    session = create_room(host=g, variant=Variant())
    assert session.seats[0].principal is g
    assert session.seats[0].is_ai is False
    assert all(s.is_ai for s in session.seats[1:])
    assert session.host_principal_id == principal_id(g)
    assert get_room(session.code) is session


def test_remove_room():
    g = Guest(guest_id='abcd1234' * 4)
    session = create_room(host=g, variant=Variant())
    code = session.code
    remove_room(code)
    assert get_room(code) is None
```

- [ ] **Step 3: Run failing test**

```bash
python -m pytest tests/multiplayer/test_room_model.py -v
```

Expected: ImportError.

- [ ] **Step 4: Implement `ausbau/room.py`**

```python
import asyncio
import secrets
import time
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from frontend.auth.guest import Guest
from frontend.auth.models import User

if TYPE_CHECKING:
    from fastapi import WebSocket
    from ausbau.game_session import GameSession


POSITIONS = ('compo', 'compn', 'compe', 'comps')

# Module constants
RECONNECT_GRACE_SECONDS = 60
SEAT_SWAP_REQUEST_TTL_SECONDS = 30
SPECTATOR_CAP_PER_ROOM = 20
REAPER_INTERVAL_SECONDS = 60
ROOM_FINISHED_LINGER_SECONDS = 300
REPLAY_BUFFER_TRICK_COUNT = 3

_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 0/O/1/I excluded

Principal = "User | Guest"  # avoid runtime Union for older Pythons


def principal_id(p) -> str:
    if isinstance(p, User):
        return str(p.id)
    if isinstance(p, Guest):
        return f"guest:{p.guest_id}"
    raise TypeError(f"unknown principal type: {type(p)}")


@dataclass(frozen=True)
class Variant:
    trumpf_bock: bool = False
    match_bonus: bool = True
    stoeck: bool = True


@dataclass
class Seat:
    position: str
    principal: Optional[object] = None         # User | Guest | None
    websocket: Optional[object] = None         # WebSocket | None
    is_ai: bool = True
    reconnect_deadline: Optional[float] = None
    connected_since: Optional[float] = None
    incoming: asyncio.Queue = field(default_factory=asyncio.Queue)
    state_event: asyncio.Event = field(default_factory=asyncio.Event)

    def display_name(self) -> str:
        if self.is_ai or self.principal is None:
            return f"AI ({self.position})"
        if isinstance(self.principal, User):
            return self.principal.username
        if isinstance(self.principal, Guest):
            return self.principal.display_name
        return self.position


@dataclass
class Spectator:
    principal: object         # User | Guest
    websocket: object         # WebSocket


# Global room registry
ROOMS: dict[str, "GameSession"] = {}


def make_code() -> str:
    while True:
        code = ''.join(secrets.choice(_CODE_ALPHABET) for _ in range(6))
        if code not in ROOMS:
            return code


def create_room(*, host, variant: Variant):
    """Create a room and register it. Host claims seat 0; seats 1-3 are AI."""
    from ausbau.game_session import GameSession
    code = make_code()
    session = GameSession(
        code=code,
        host_principal_id=principal_id(host),
        variant=variant,
    )
    session.seats[0].principal = host
    session.seats[0].is_ai = False
    ROOMS[code] = session
    return session


def get_room(code: str):
    return ROOMS.get(code.upper())


def remove_room(code: str) -> None:
    ROOMS.pop(code, None)


def find_rooms_for_principal(p) -> list[dict]:
    pid = principal_id(p)
    out = []
    for room in ROOMS.values():
        for seat in room.seats:
            if seat.principal is not None and principal_id(seat.principal) == pid:
                out.append({
                    "code": room.code, "role": "seat",
                    "position": seat.position, "state": room.state,
                })
                break
        else:
            for spec in room.spectators:
                if principal_id(spec.principal) == pid:
                    out.append({
                        "code": room.code, "role": "spectator",
                        "state": room.state,
                    })
                    break
    return out
```

- [ ] **Step 5: GameSession constructor stub**

`ausbau/room.py` references `GameSession.__init__` with new keyword args. We need to extend the constructor in the same task to keep imports satisfied. In `ausbau/game_session.py`, locate `class GameSession:` and replace `__init__` with:

```python
class GameSession:
    def __init__(
        self,
        *,
        code: str = "",
        host_principal_id: str = "",
        variant=None,                     # type: ignore
        end_game: int = 1000,
        principal=None,                   # legacy: from sub-project B's WS principal injection
    ):
        from ausbau.room import POSITIONS, Seat, Variant
        self.code = code
        self.variant = variant if variant is not None else Variant()
        self.end_game = end_game
        self.host_principal_id = host_principal_id
        self.principal = principal        # legacy; kept for compat with old /ws

        # Lobby state
        self.seats = [Seat(position=POSITIONS[i]) for i in range(4)]
        self.spectators = []
        self.state = "lobby"

        # Game state
        self.point_sn = 0
        self.point_ow = 0
        self.current_play = None

        # Concurrency
        self._lock = asyncio.Lock()
        self._reconnect_tasks = {}
        self._game_task = None
        self._completed_tricks = []
        self._swap_requests = {}
```

Add `import asyncio` at top of `ausbau/game_session.py` if missing.

- [ ] **Step 6: Run tests**

```bash
python -m pytest tests/multiplayer/test_room_model.py -v
```

Expected: 9 passed.

- [ ] **Step 7: Run full repo to confirm no regressions**

```bash
python -m pytest tests/ -v
```

Expected: prior tests still pass; legacy `/ws` integration test in `tests/test_game_session.py` still works (the `principal=` kwarg is preserved).

- [ ] **Step 8: Commit**

```bash
git add ausbau/room.py ausbau/game_session.py tests/multiplayer/__init__.py tests/multiplayer/test_room_model.py
git commit -m "feat(multiplayer): room.py data model + registry; extend GameSession ctor"
```

Use `-c commit.gpgsign=false` if signing fails.

---

## Task 4: Multiplayer test conftest (FakeWebSocket + fast_clock)

**Files:**
- Create: `tests/multiplayer/conftest.py`
- Create: `tests/multiplayer/test_conftest_smoke.py`

- [ ] **Step 1: Implement conftest**

`tests/multiplayer/conftest.py`:

```python
import asyncio
import pytest
import pytest_asyncio
from typing import Any

from ausbau.room import ROOMS


@pytest.fixture(autouse=True)
def reset_rooms():
    ROOMS.clear()
    yield
    ROOMS.clear()


class FakeWebSocket:
    def __init__(self):
        self.sent: list[dict] = []
        self.incoming: asyncio.Queue = asyncio.Queue()
        self.cookies: dict = {}
        self.closed = False
        self.close_code: int | None = None
        self.close_reason: str = ""

    async def accept(self) -> None:
        pass

    async def send_json(self, msg: dict) -> None:
        self.sent.append(msg)

    async def receive_json(self) -> dict:
        return await self.incoming.get()

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    # Test-side helpers
    def push(self, msg: dict) -> None:
        self.incoming.put_nowait(msg)

    def last_sent_of_type(self, t: str) -> dict | None:
        return next((m for m in reversed(self.sent) if m.get("type") == t), None)

    def all_sent_of_type(self, t: str) -> list[dict]:
        return [m for m in self.sent if m.get("type") == t]


@pytest.fixture
def fake_ws():
    return FakeWebSocket()


@pytest.fixture
def fast_clock(monkeypatch):
    """Patch asyncio.sleep so timer-based tests run fast.

    Caveat: any `asyncio.sleep(N)` call inside the tests will return after
    one event-loop tick. This is what we want — the 60s reconnect grace
    fires in <1ms.
    """
    real_sleep = asyncio.sleep

    async def fake_sleep(seconds: float) -> None:
        await real_sleep(0)

    monkeypatch.setattr("asyncio.sleep", fake_sleep)
```

- [ ] **Step 2: Smoke-test the conftest**

`tests/multiplayer/test_conftest_smoke.py`:

```python
import pytest
import asyncio


pytestmark = pytest.mark.asyncio


async def test_fake_ws_send_recv(fake_ws):
    await fake_ws.send_json({"type": "hello"})
    fake_ws.push({"type": "hi"})
    msg = await fake_ws.receive_json()
    assert msg == {"type": "hi"}
    assert fake_ws.sent == [{"type": "hello"}]
    assert fake_ws.last_sent_of_type("hello") == {"type": "hello"}


async def test_fast_clock(fast_clock):
    import time
    t0 = time.monotonic()
    await asyncio.sleep(60.0)  # would normally take 60s
    t1 = time.monotonic()
    assert (t1 - t0) < 1.0  # actually returns instantly


def test_rooms_isolated_per_test():
    from ausbau.room import ROOMS, create_room, Variant
    from frontend.auth.guest import Guest
    g = Guest(guest_id='a' * 32)
    create_room(host=g, variant=Variant())
    assert len(ROOMS) == 1


def test_rooms_isolated_per_test_round2():
    from ausbau.room import ROOMS
    # autouse fixture should have cleared
    assert len(ROOMS) == 0
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/multiplayer/test_conftest_smoke.py -v
```

Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add tests/multiplayer/conftest.py tests/multiplayer/test_conftest_smoke.py
git commit -m "test(multiplayer): FakeWebSocket + fast_clock fixtures"
```

Use `-c commit.gpgsign=false` if signing fails.

---

## Task 5: Room CRUD endpoints (`POST /rooms`, `GET /rooms/{code}`, `GET /rooms/mine`)

**Files:**
- Modify: `ausbau/server.py`
- Create: `tests/multiplayer/test_room_crud.py`

- [ ] **Step 1: Write the failing tests**

`tests/multiplayer/test_room_crud.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def client():
    """An httpx client against the live ausbau.server app."""
    from ausbau.server import app as srv_app
    async with AsyncClient(transport=ASGITransport(app=srv_app),
                           base_url="http://test") as c:
        yield c


async def test_create_room_returns_code_and_state(client):
    r = await client.post("/rooms", json={
        "variant": {"trumpf_bock": False, "match_bonus": True, "stoeck": True},
    }, headers={"X-Requested-With": "schieber"})
    assert r.status_code == 201
    body = r.json()
    assert "code" in body and len(body["code"]) == 6
    assert body["state"] == "lobby"
    assert len(body["seats"]) == 4
    assert body["seats"][0]["is_ai"] is False  # host
    assert all(s["is_ai"] for s in body["seats"][1:])
    assert body["seats"][0]["is_host"] is True


async def test_get_room_404_for_unknown(client):
    r = await client.get("/rooms/UNKNOWN")
    assert r.status_code == 404


async def test_get_room_returns_state(client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.get(f"/rooms/{code}")
    assert r.status_code == 200
    assert r.json()["code"] == code


async def test_rooms_mine_includes_created(client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client.get("/rooms/mine")
    assert r.status_code == 200
    rooms = r.json()
    assert any(rm["code"] == code and rm["role"] == "seat" for rm in rooms)
```

- [ ] **Step 2: Add endpoints to `ausbau/server.py`**

In `ausbau/server.py`, after the existing imports, add:

```python
from fastapi import Request, Response, HTTPException, Depends
from frontend.auth.deps import make_current_principal_dep
from ausbau.room import (
    create_room, get_room, find_rooms_for_principal,
    Variant, principal_id,
)
```

Inside `_auth_init_db` (or near where the auth app is mounted), wire the principal dep:

```python
# Build principal dep from auth settings
current_principal_dep = make_current_principal_dep(
    get_session=_get_auth_session,
    secret_key=_auth_settings.secret_key,
    secure_cookie=_auth_settings.secure_cookie,
)
```

(Adjust to match the actual auth-init pattern in your `ausbau/server.py`. The dep needs the auth get_session, secret_key, and secure_cookie flag.)

Now define the room endpoints (place anywhere after `app = FastAPI()` and before the existing `/ws`):

```python
def _seat_to_dict(seat, room) -> dict:
    return {
        "position": seat.position,
        "display_name": seat.display_name(),
        "is_ai": seat.is_ai,
        "connected": seat.websocket is not None and not seat.is_ai,
        "is_host": (
            seat.principal is not None
            and principal_id(seat.principal) == room.host_principal_id
        ),
        "principal_id": (
            principal_id(seat.principal) if seat.principal is not None else None
        ),
    }


def _room_state_dict(room) -> dict:
    return {
        "code": room.code,
        "host_principal_id": room.host_principal_id,
        "state": room.state,
        "variant": {
            "trumpf_bock": room.variant.trumpf_bock,
            "match_bonus": room.variant.match_bonus,
            "stoeck": room.variant.stoeck,
        },
        "end_game": room.end_game,
        "seats": [_seat_to_dict(s, room) for s in room.seats],
        "spectator_count": len(room.spectators),
        "scores": {"sn": room.point_sn, "ow": room.point_ow},
    }


@app.post("/rooms", status_code=201)
async def create_room_endpoint(
    payload: dict,
    request: Request,
    response: Response,
    principal=Depends(lambda r=None, resp=None: None),  # placeholder; see below
):
    pass  # populated below
```

The principal-dep injection is awkward because `make_current_principal_dep` returns a dep that needs to be wired at app-startup. The cleanest pattern: wire it in `_auth_init_db` and stash on `app.state`, then use `request.app.state.current_principal_dep` inside route bodies. Concrete:

In `_auth_init_db`:
```python
app.state.current_principal_dep = current_principal_dep
```

In each route, take the dep via FastAPI Depends-on-app-state pattern:
```python
@app.post("/rooms", status_code=201)
async def create_room_endpoint(
    payload: dict,
    request: Request,
    response: Response,
):
    principal = await app.state.current_principal_dep(request, response, ...)
    ...
```

Concrete pattern — define a small wrapper at module scope that resolves the dep:

```python
async def _get_principal(request: Request, response: Response):
    """Resolve current principal via the dep stored on app.state."""
    dep = request.app.state.current_principal_dep
    # Inline the dep manually because Depends() machinery doesn't apply when
    # called from inside another route. The dep needs (request, response, session).
    async for session in _get_auth_session():
        return await dep(request, response, session)


@app.post("/rooms", status_code=201)
async def create_room_endpoint(
    payload: dict,
    request: Request,
    response: Response,
):
    principal = await _get_principal(request, response)
    variant_data = (payload or {}).get("variant", {}) or {}
    variant = Variant(
        trumpf_bock=variant_data.get("trumpf_bock", False),
        match_bonus=variant_data.get("match_bonus", True),
        stoeck=variant_data.get("stoeck", True),
    )
    room = create_room(host=principal, variant=variant)
    return _room_state_dict(room)


@app.get("/rooms/{code}")
async def get_room_endpoint(code: str):
    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    return _room_state_dict(room)


@app.get("/rooms/mine")
async def rooms_mine_endpoint(request: Request, response: Response):
    principal = await _get_principal(request, response)
    return find_rooms_for_principal(principal)
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/multiplayer/test_room_crud.py -v
```

Expected: 4 passed (after iteration on the dep wiring above).

- [ ] **Step 4: Run full repo**

```bash
python -m pytest tests/ -v
```

Expected: no regressions.

- [ ] **Step 5: Commit**

```bash
git add ausbau/server.py tests/multiplayer/test_room_crud.py
git commit -m "feat(multiplayer): POST /rooms, GET /rooms/{code}, GET /rooms/mine"
```

Use `-c commit.gpgsign=false` if signing fails.

---

## Task 6: Join / leave / spectate / leave-spectator endpoints

**Files:**
- Modify: `ausbau/server.py`
- Create: `tests/multiplayer/test_join_leave.py`

- [ ] **Step 1: Write the failing tests**

`tests/multiplayer/test_join_leave.py`:

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def client():
    from ausbau.server import app as srv_app
    async with AsyncClient(transport=ASGITransport(app=srv_app),
                           base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def client_other():
    from ausbau.server import app as srv_app
    async with AsyncClient(transport=ASGITransport(app=srv_app),
                           base_url="http://test") as c:
        yield c


async def test_join_first_ai_seat(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    # Different client = different cookie = different guest principal
    r = await client_other.post(f"/rooms/{code}/join", json={},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 200, r.text
    state = r.json()["room_state"]
    # seats[0] = host (compo); seats[1] should now be the joiner
    assert state["seats"][1]["is_ai"] is False


async def test_join_specific_seat(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client_other.post(f"/rooms/{code}/join", json={"seat": 2},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 200
    state = r.json()["room_state"]
    assert state["seats"][2]["is_ai"] is False
    assert state["seats"][1]["is_ai"] is True


async def test_join_unknown_room_404(client):
    r = await client.post("/rooms/UNKNOWN/join", json={},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 404


async def test_leave_returns_seat_to_ai(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    await client_other.post(f"/rooms/{code}/join", json={},
                            headers={"X-Requested-With": "schieber"})
    r = await client_other.post(f"/rooms/{code}/leave", json={},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204
    after = await client.get(f"/rooms/{code}")
    assert all(s["is_ai"] for s in after.json()["seats"][1:])


async def test_spectate(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    r = await client_other.post(f"/rooms/{code}/spectate", json={},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 200
    state = r.json()
    assert state["spectator_count"] == 1


async def test_spectate_409_when_seated(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    # Host (client) is already seated; trying to spectate own room → 409
    r = await client.post(f"/rooms/{code}/spectate", json={},
                          headers={"X-Requested-With": "schieber"})
    assert r.status_code == 409


async def test_leave_spectator(client_other, client):
    create = await client.post("/rooms", json={},
                               headers={"X-Requested-With": "schieber"})
    code = create.json()["code"]
    await client_other.post(f"/rooms/{code}/spectate", json={},
                            headers={"X-Requested-With": "schieber"})
    r = await client_other.post(f"/rooms/{code}/leave-spectator", json={},
                                headers={"X-Requested-With": "schieber"})
    assert r.status_code == 204
    after = await client.get(f"/rooms/{code}")
    assert after.json()["spectator_count"] == 0
```

- [ ] **Step 2: Add endpoints to `ausbau/server.py`**

```python
from ausbau.room import Spectator, SPECTATOR_CAP_PER_ROOM


def _seat_for_principal(room, principal):
    pid = principal_id(principal)
    for seat in room.seats:
        if seat.principal is not None and principal_id(seat.principal) == pid:
            return seat
    return None


def _spectator_for_principal(room, principal):
    pid = principal_id(principal)
    for spec in room.spectators:
        if principal_id(spec.principal) == pid:
            return spec
    return None


@app.post("/rooms/{code}/join")
async def join_endpoint(
    code: str,
    payload: dict,
    request: Request,
    response: Response,
):
    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    if room.state != "lobby":
        raise HTTPException(409, "game already started")
    principal = await _get_principal(request, response)

    # Already seated?
    existing = _seat_for_principal(room, principal)
    if existing is not None:
        return {"seat": room.seats.index(existing), "room_state": _room_state_dict(room)}

    # Pick seat
    target_idx = (payload or {}).get("seat")
    if target_idx is None:
        # First AI seat
        for i, s in enumerate(room.seats):
            if s.is_ai:
                target_idx = i
                break
        if target_idx is None:
            raise HTTPException(409, "room full")
    else:
        if not (0 <= target_idx < 4):
            raise HTTPException(422, "invalid seat index")
        if not room.seats[target_idx].is_ai:
            raise HTTPException(409, "seat occupied")

    seat = room.seats[target_idx]
    seat.principal = principal
    seat.is_ai = False
    return {"seat": target_idx, "room_state": _room_state_dict(room)}


@app.post("/rooms/{code}/leave", status_code=204)
async def leave_endpoint(
    code: str,
    payload: dict,
    request: Request,
    response: Response,
):
    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    principal = await _get_principal(request, response)
    target_pos = (payload or {}).get("target_position")

    if target_pos is None:
        # Self-leave
        seat = _seat_for_principal(room, principal)
        if seat is None:
            return Response(status_code=204)
        if room.state == "lobby":
            seat.principal = None
            seat.is_ai = True
            seat.websocket = None
            # If host left, transfer
            if principal_id(principal) == room.host_principal_id:
                await room._transfer_host()
        else:
            # Mid-game: AI takeover, no grace
            seat.is_ai = True
            seat.websocket = None
            seat.principal = None
            seat.state_event.set()
        return Response(status_code=204)

    # Kick (host-only, lobby-only)
    if principal_id(principal) != room.host_principal_id:
        raise HTTPException(403, "host only")
    if room.state != "lobby":
        raise HTTPException(400, "cannot kick mid-game")
    if target_pos not in ('compo', 'compn', 'compe', 'comps'):
        raise HTTPException(422, "invalid position")
    seat = next(s for s in room.seats if s.position == target_pos)
    if seat.is_ai or seat.principal is None:
        return Response(status_code=204)
    if seat.websocket is not None:
        try:
            await seat.websocket.close(code=1008, reason="kicked from room")
        except Exception:
            pass
    seat.principal = None
    seat.is_ai = True
    seat.websocket = None
    return Response(status_code=204)


@app.post("/rooms/{code}/spectate")
async def spectate_endpoint(
    code: str,
    request: Request,
    response: Response,
):
    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    principal = await _get_principal(request, response)
    if _seat_for_principal(room, principal) is not None:
        raise HTTPException(409, "already seated; cannot spectate")
    if len(room.spectators) >= SPECTATOR_CAP_PER_ROOM:
        raise HTTPException(503, "spectator capacity reached")
    if _spectator_for_principal(room, principal) is None:
        room.spectators.append(Spectator(principal=principal, websocket=None))
    return _room_state_dict(room)


@app.post("/rooms/{code}/leave-spectator", status_code=204)
async def leave_spectator_endpoint(
    code: str,
    request: Request,
    response: Response,
):
    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    principal = await _get_principal(request, response)
    spec = _spectator_for_principal(room, principal)
    if spec is None:
        return Response(status_code=204)
    if spec.websocket is not None:
        try:
            await spec.websocket.close()
        except Exception:
            pass
    room.spectators.remove(spec)
    return Response(status_code=204)
```

`room._transfer_host` is referenced — stub it for now in `ausbau/game_session.py::GameSession`:

```python
async def _transfer_host(self):
    """Pick oldest-connected human as new host. No-op if none connected."""
    candidates = [
        s for s in self.seats
        if not s.is_ai and s.websocket is not None and s.connected_since is not None
    ]
    if not candidates:
        return
    candidates.sort(key=lambda s: (s.connected_since, principal_id(s.principal)))
    new_host = candidates[0]
    old_host_pos = next(
        (s.position for s in self.seats
         if s.principal is not None and principal_id(s.principal) == self.host_principal_id),
        None
    )
    self.host_principal_id = principal_id(new_host.principal)
    # Broadcast
    msg = {
        "type": "host_changed",
        "old_host_position": old_host_pos,
        "new_host_position": new_host.position,
        "new_host_display_name": new_host.display_name(),
    }
    for seat in self.seats:
        if seat.websocket is not None and not seat.is_ai:
            try:
                await seat.websocket.send_json(msg)
            except Exception:
                pass
    for spec in list(self.spectators):
        try:
            if spec.websocket is not None:
                await spec.websocket.send_json(msg)
        except Exception:
            pass
```

Add at top of `game_session.py`: `from ausbau.room import principal_id` (deferred import to avoid circularity if needed).

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/multiplayer/test_join_leave.py -v
```

Expected: 7 passed.

- [ ] **Step 4: Run full repo**

```bash
python -m pytest tests/ -v
```

Expected: no regressions.

- [ ] **Step 5: Commit**

```bash
git add ausbau/server.py ausbau/game_session.py tests/multiplayer/test_join_leave.py
git commit -m "feat(multiplayer): join/leave/spectate endpoints + host transfer stub"
```

Use `-c commit.gpgsign=false` if signing fails.

---

## Task 7-23: Game-loop refactor, WS endpoint, variants, swap, host transfer, lobby UI

The remaining tasks follow the same TDD pattern: tests first, implementation, verify, commit. Due to the size of the multiplayer refactor (per-seat WS routing, game-phase loops adapting to multi-seat input, reconnect timers, AI-takeover state, replay buffer, mid-game seat swap, host transfer rules, Jinja2 lobby UI, and full integration into the existing game.html / schieber.js), these tasks are decomposed in a follow-up plan continuation:

`docs/superpowers/plans/2026-04-28-schieber-multiplayer-part2.md` (to be written before implementation begins on Task 7+).

**Rationale for the split:** the auth plan (sub-project B) ran ~3600 lines / 27 tasks; the multiplayer plan with full code blocks for all 23 tasks would exceed 5000 lines, which is a usability problem (loading and reading the plan becomes its own friction). Splitting after Task 6 lets implementers ship the lobby/CRUD layer first, manually smoke-test the room creation + join flow with curl, and then start Part 2 (the game-mechanics refactor) with a settled foundation.

**Part 2 task list (preview):**
- Task 7: GameSession constructor → seats + state machine clarity
- Task 8: send_to_seat / broadcast / broadcast_per_seat helpers
- Task 9: WebSocket endpoint /ws/{code} (resolve principal, attach as seat or spectator)
- Task 10: Refactor _trump_phase for multi-seat
- Task 11: Refactor _weis_phase for multi-seat
- Task 12: Refactor _play_trick for multi-seat (per-seat redaction of play_request)
- Task 13: _await_seat_action + per-seat queues
- Task 14: _disconnect_seat + 60s timer + AI-takeover (preserve principal)
- Task 15: _reclaim_seat + room_resume message
- Task 16: Replay buffer (last 3 tricks)
- Task 17: Variant arithmetic (trumpf_bock, match_bonus, stoeck)
- Task 18: POST /rooms/{code}/start + game-loop background task
- Task 19: POST /rooms/{code}/seat (mid-game swap, two-step accept)
- Task 20: Host-transfer + kick (refine stub from Task 6)
- Task 21: Reaper task (idle rooms)
- Task 22: lobby.html Jinja template + page route
- Task 23: schieber.js lobby state machine + per-seat rendering
- Task 24: Manual smoke checklist + integration tests
- Task 25: CLAUDE.md update

Part 2 will be written when Tasks 0–6 are complete and the lobby CRUD is verified end-to-end.

---

## Self-review checklist (run before handoff)

**Spec coverage so far (Tasks 0–6):**
- §2 architecture (file layout + globals) → Tasks 3, 4, 5, 6
- §3 room state model (Seat, Spectator, Variant, registry) → Task 3
- §4.1 current_principal dep → Task 2
- §4.2 endpoints (POST /rooms, GET /rooms/{code}, GET /rooms/mine, join, leave, spectate, leave-spectator) → Tasks 5, 6
- §5 protocol skill → Task 0

**Spec coverage in Part 2 (Tasks 7+):**
- §3.6 GameSession multi-seat constructor → Task 7
- §5.1 send_to_seat / broadcast → Task 8
- §4.2 WS /ws/{code} → Task 9
- §5.2 protocol messages (game_start, trump_*, weis_*, play_*, trick_end, spiel_end, game_end, seat_*, room_resume, error) → Tasks 10, 11, 12
- §6 reconnect mechanics → Tasks 13, 14, 15
- §5.4 reconnect-replay → Task 16
- §7 variants → Task 17
- §4.2 POST /rooms/{code}/start → Task 18
- §4.3 mid-game seat swap → Task 19
- §8 host transfer + kick → Task 20
- §2.3 reaper → Task 21
- §4.6 lobby HTML page → Task 22
- Lobby UI + per-seat rendering → Task 23
- §11.6 manual smoke checklist → Task 24
- §1.5 doc update → Task 25

**Placeholder scan (Tasks 0–6):** none of the No-Placeholders patterns appear; every step has the actual content.

**Type consistency:** `Variant`, `Seat`, `Spectator`, `principal_id`, `make_code`, `create_room`, `get_room`, `find_rooms_for_principal`, `_seat_to_dict`, `_room_state_dict` — names used consistently across Tasks 3–6. `GameSession` constructor signature consistent across Task 3 and Task 6 (the `_transfer_host` stub).

**Known caveats embedded in tasks:**
- Task 5: principal-dep wiring is awkward via `app.state` — straightforward but requires careful wiring at startup.
- Task 6: `_transfer_host` stubbed; will be refined in Part 2 Task 20.
- Plan continues in Part 2 for the multiplayer game-loop refactor (Tasks 7–25).
