# ausbau/server.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import secrets
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from frontend.auth.guest import read_guest_cookie, GuestCookieError, Guest
from frontend.auth.models import User as AuthUser, AccessToken
from frontend.auth.db import make_engine, make_session_factory, init_db
from frontend.auth.settings import load_settings
from frontend.auth.app import build_app
from frontend.auth.email import ConsoleMailBackend, SmtpMailBackend
from ausbau.game_session import GameSession

app = FastAPI()

# Initialise auth engine for principal lookup. Done lazily so that running tests
# that don't use /ws don't require auth env vars to be set.
_auth_settings = None
_auth_engine = None
_auth_factory = None


def _ensure_auth_initialised():
    global _auth_settings, _auth_engine, _auth_factory
    if _auth_settings is None:
        _auth_settings = load_settings()
        _auth_engine = make_engine(_auth_settings.auth_db_url)
        _auth_factory = make_session_factory(_auth_engine)


def _build_auth_app():
    """Construct the auth sub-app and return its FastAPI instance.

    Uses the global _auth_factory created by _ensure_auth_initialised, so
    /auth/* and /ws share the same engine/session factory.
    """
    _ensure_auth_initialised()
    if _auth_settings.mail_backend == "console":
        mail = ConsoleMailBackend()
    else:
        mail = SmtpMailBackend(
            host=_auth_settings.smtp_host,
            port=_auth_settings.smtp_port,
            user=_auth_settings.smtp_user,
            password=_auth_settings.smtp_app_password,
        )

    async def get_session():
        async with _auth_factory() as s:
            yield s

    return build_app(
        get_session=get_session,
        settings=_auth_settings,
        mail=mail,
    )



_BASE = os.path.dirname(os.path.abspath(__file__))
_HTML5 = os.path.join(_BASE, "html5")

app.mount("/static", StaticFiles(directory=_HTML5), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(_HTML5, "game.html"))


# ---------------------------------------------------------------------------
# Auth sub-app wiring
# ---------------------------------------------------------------------------
# Routes are mounted lazily inside the startup hook so that importing this
# module during tests (which monkeypatch _auth_settings / _auth_factory after
# import) does NOT call load_settings() at module-load time.

@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        {"detail": "rate limited"},
        status_code=429,
        headers={"Retry-After": "60"},
    )


@app.on_event("startup")
async def _auth_init_db():
    """Mount auth routes and create auth.db tables on first launch.

    Done here (not at module load) so that importing ausbau.server during
    tests does not require real auth env vars to be set.
    """
    _ensure_auth_initialised()
    # Build auth sub-app and copy its routes onto the main app so that
    # /auth/*, /admin/*, /login, /signup etc. are all reachable on the same
    # uvicorn process without path-prefix games.  Middleware (slowapi) doesn't
    # carry over via this mechanism — the RateLimitExceeded handler above
    # covers it on the main app.
    _auth_app = _build_auth_app()
    for route in _auth_app.routes:
        app.router.routes.append(route)
    await init_db(_auth_engine)


# ---------------------------------------------------------------------------
# Room CRUD helpers
# ---------------------------------------------------------------------------

async def _get_principal(request: Request, response: Response):
    """Resolve the current principal (User or Guest) for the current request."""
    _ensure_auth_initialised()
    async with _auth_factory() as session:
        sess_token = request.cookies.get("schieber_session")
        if sess_token:
            from sqlalchemy import select as _select
            from frontend.auth.models import AccessToken as _AccessToken, User as _User
            from datetime import datetime as _dt, timezone as _tz
            q = _select(_AccessToken).where(
                _AccessToken.token == sess_token,
                _AccessToken.expires_at > _dt.now(_tz.utc),
            )
            at = (await session.execute(q)).scalar_one_or_none()
            if at is not None:
                u = (await session.execute(
                    _select(_User).where(_User.id == at.user_id)
                )).scalar_one_or_none()
                if u is not None and u.is_active:
                    return u

        guest_cookie = request.cookies.get("schieber_guest")
        if guest_cookie:
            from frontend.auth.guest import read_guest_cookie, GuestCookieError
            try:
                return read_guest_cookie(guest_cookie, _auth_settings.secret_key)
            except GuestCookieError:
                pass

        from frontend.auth.guest import issue_guest_cookie
        new_cookie, guest = issue_guest_cookie(_auth_settings.secret_key)
        secure = getattr(_auth_settings, "secure_cookie", False)
        response.set_cookie(
            key="schieber_guest",
            value=new_cookie,
            max_age=30 * 24 * 60 * 60,
            httponly=True,
            secure=secure,
            samesite="lax",
        )
        return guest


def _seat_to_dict(seat, room) -> dict:
    from ausbau.room import principal_id
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
    request: Request,
    response: Response,
    payload: Optional[dict] = Body(default={}),
):
    from ausbau.room import create_room, Variant
    principal = await _get_principal(request, response)
    variant_data = (payload or {}).get("variant", {}) or {}
    variant = Variant(
        trumpf_bock=variant_data.get("trumpf_bock", False),
        match_bonus=variant_data.get("match_bonus", True),
        stoeck=variant_data.get("stoeck", True),
    )
    room = create_room(host=principal, variant=variant)
    return _room_state_dict(room)


@app.get("/rooms/mine")
async def rooms_mine_endpoint(request: Request, response: Response):
    from ausbau.room import find_rooms_for_principal
    principal = await _get_principal(request, response)
    return find_rooms_for_principal(principal)


@app.get("/rooms/{code}")
async def get_room_endpoint(code: str):
    from ausbau.room import get_room
    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    return _room_state_dict(room)


# ---------------------------------------------------------------------------
# Join / leave / spectate helpers
# ---------------------------------------------------------------------------

def _seat_for_principal(room, principal):
    from ausbau.room import principal_id
    pid = principal_id(principal)
    for seat in room.seats:
        if seat.principal is not None and principal_id(seat.principal) == pid:
            return seat
    return None


def _spectator_for_principal(room, principal):
    from ausbau.room import principal_id
    pid = principal_id(principal)
    for spec in room.spectators:
        if principal_id(spec.principal) == pid:
            return spec
    return None


# ---------------------------------------------------------------------------
# Join / leave / spectate endpoints
# ---------------------------------------------------------------------------

@app.post("/rooms/{code}/join")
async def join_endpoint(
    code: str,
    payload: Optional[dict] = Body(default={}),
    request: Request = None,
    response: Response = None,
):
    from ausbau.room import get_room, principal_id
    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    if room.state != "lobby":
        raise HTTPException(409, "game already started")
    principal = await _get_principal(request, response)

    # Already seated? Idempotent return.
    existing = _seat_for_principal(room, principal)
    if existing is not None:
        return {"seat": room.seats.index(existing), "room_state": _room_state_dict(room)}

    # Pick seat
    target_idx = (payload or {}).get("seat")
    if target_idx is None:
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
    payload: Optional[dict] = Body(default={}),
    request: Request = None,
    response: Response = None,
):
    from ausbau.room import get_room, principal_id
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
            was_host = principal_id(principal) == room.host_principal_id
            seat.principal = None
            seat.is_ai = True
            seat.websocket = None
            if was_host:
                await room._transfer_host()
        else:
            # Mid-game: AI takeover, NO 60s grace (explicit leave)
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
    from ausbau.room import get_room, Spectator, SPECTATOR_CAP_PER_ROOM
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
    from ausbau.room import get_room
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


# ---------------------------------------------------------------------------
# Game start endpoint
# ---------------------------------------------------------------------------

@app.post("/rooms/{code}/start", status_code=204)
async def start_room_endpoint(
    code: str,
    request: Request,
    response: Response,
):
    """Host-only: lock seats and kick off the game-loop background task.

    - 404 if room does not exist.
    - 403 if caller is not the room host.
    - 409 if room is not in lobby state.
    Otherwise spawns ``GameSession.start_game`` as a background task,
    flips ``room.state`` to ``"playing"`` (the loop also sets this on
    entry), and returns 204.
    """
    from ausbau.room import get_room, principal_id

    room = get_room(code)
    if room is None:
        raise HTTPException(404, "room not found")
    principal = await _get_principal(request, response)
    if principal_id(principal) != room.host_principal_id:
        raise HTTPException(403, "not host")
    if room.state != "lobby":
        raise HTTPException(409, f"room state is {room.state}")

    # Flip state synchronously so a fast follow-up GET sees "playing"
    # even before the loop's first await yields. start_game() also sets
    # this idempotently on entry.
    room.state = "playing"
    room._game_task = asyncio.create_task(
        room.start_game(),
        name=f"game_loop:{room.code}",
    )
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# WebSocket game endpoint
# ---------------------------------------------------------------------------

@app.websocket("/ws/{code}")
async def websocket_endpoint(websocket: WebSocket, code: str):
    """Multi-WS endpoint per room. Resolves principal, attaches as seat or spectator."""
    from ausbau.room import get_room

    await websocket.accept()

    # Resolve principal from cookies (manual — FastAPI Depends doesn't apply to WS)
    _ensure_auth_initialised()
    sess_token = websocket.cookies.get("schieber_session")
    principal = None
    if sess_token:
        from sqlalchemy import select
        from frontend.auth.models import AccessToken, User as AuthUser
        from datetime import datetime, timezone
        async with _auth_factory() as session:
            q = select(AccessToken).where(
                AccessToken.token == sess_token,
                AccessToken.expires_at > datetime.now(timezone.utc),
            )
            at = (await session.execute(q)).scalar_one_or_none()
            if at is not None:
                u = (await session.execute(
                    select(AuthUser).where(AuthUser.id == at.user_id)
                )).scalar_one_or_none()
                if u is not None and u.is_active:
                    principal = u

    if principal is None:
        guest_cookie = websocket.cookies.get("schieber_guest")
        if guest_cookie:
            from frontend.auth.guest import read_guest_cookie, GuestCookieError
            try:
                principal = read_guest_cookie(guest_cookie, _auth_settings.secret_key)
            except GuestCookieError:
                pass

    if principal is None:
        await websocket.close(code=1008, reason="no auth cookie")
        return

    # Find room
    room = get_room(code)
    if room is None:
        await websocket.close(code=1008, reason="room not found")
        return

    # Attach as seat or spectator
    seat = room._seat_for_principal(principal)
    spec = room._spectator_for_principal(principal)

    if seat is not None:
        await room._reclaim_seat(seat.position, websocket, principal)
    elif spec is not None:
        spec.websocket = websocket
        await websocket.send_json(room._room_resume_message_for(None))
    else:
        await websocket.close(code=1008, reason="no seat or spectator slot")
        return

    # WS reader loop: dequeue and route to seat's queue
    try:
        while True:
            msg = await websocket.receive_json()
            if seat is not None:
                # Re-resolve seat in case position changed (mid-game swap)
                current_seat = room._seat_for_principal(principal)
                if current_seat is not None:
                    current_seat.incoming.put_nowait(msg)
            else:
                # Spectator sent a message — error reply, don't break
                try:
                    await websocket.send_json({"type": "error",
                                               "message": "spectators are read-only"})
                except Exception:
                    break
    except WebSocketDisconnect:
        if seat is not None:
            await room._disconnect_seat(seat.position)
        elif spec is not None and spec in room.spectators:
            room.spectators.remove(spec)
