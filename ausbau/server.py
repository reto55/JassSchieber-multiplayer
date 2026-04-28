# ausbau/server.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import secrets
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from frontend.auth.guest import read_guest_cookie, GuestCookieError, Guest
from frontend.auth.models import User as AuthUser, AccessToken
from frontend.auth.db import make_engine, make_session_factory
from frontend.auth.settings import load_settings
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


async def _resolve_user_from_cookie(token: str):
    """Return the User row for a valid session cookie, else None."""
    _ensure_auth_initialised()
    async with _auth_factory() as session:
        q = select(AccessToken).where(
            AccessToken.token == token,
            AccessToken.expires_at > datetime.now(timezone.utc),
        )
        at = (await session.execute(q)).scalar_one_or_none()
        if at is None:
            return None
        u = (await session.execute(
            select(AuthUser).where(AuthUser.id == at.user_id)
        )).scalar_one_or_none()
        if u is None or not u.is_active:
            return None
        return u


async def resolve_principal(ws):
    """Resolve the WS connection to either an AuthUser or a Guest.

    Priority: schieber_session cookie → AuthUser; schieber_guest cookie → Guest;
    fall back to a fresh transient Guest (for programmatic clients that bypassed
    /auth/whoami).
    """
    _ensure_auth_initialised()
    sess = ws.cookies.get("schieber_session")
    if sess:
        u = await _resolve_user_from_cookie(sess)
        if u is not None:
            return u
    guest_cookie = ws.cookies.get("schieber_guest")
    if guest_cookie:
        try:
            return read_guest_cookie(guest_cookie, _auth_settings.secret_key)
        except Exception:
            # Covers GuestCookieError (bad signature), TypeError (non-string
            # value) and any other unexpected error from a malformed cookie.
            pass
    return Guest(guest_id=secrets.token_hex(16))


_BASE = os.path.dirname(os.path.abspath(__file__))
_HTML5 = os.path.join(_BASE, "html5")

app.mount("/static", StaticFiles(directory=_HTML5), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(_HTML5, "game.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    principal = await resolve_principal(websocket)
    await websocket.accept()
    session = GameSession(end_game=1000, principal=principal)
    try:
        await session.run(websocket)
    except WebSocketDisconnect:
        # Clean client-drop — socket is already gone, nothing to send.
        pass
    except Exception as exc:
        # Per the schieber-protocol skill invariant §5 ("No silent failures;
        # server responds with `error` …"), a bare close on an unexpected
        # backend exception is a contract violation. Send one last-ditch
        # protocol-shaped error payload before closing. If that send itself
        # fails (e.g. the socket is already half-closed), swallow the
        # secondary failure — the client is already unreachable.
        print(f"[ws error] {exc!r}", file=sys.stderr)
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Interner Serverfehler. Bitte neu laden.",
            })
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
