import secrets
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

from fastapi import FastAPI, Depends, Form, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from frontend.auth.users import make_fastapi_users, make_manager_dep
from frontend.auth.schemas import UserRead, UserCreate, UserUpdate
from frontend.auth.email import MailBackend
from frontend.auth.settings import Settings
from frontend.auth.models import AccessToken
from frontend.auth.lockout import is_locked_out, record_attempt, clear_email_streak


TTL_NORMAL = timedelta(hours=2)
TTL_REMEMBER = timedelta(days=30)


def build_app(*, get_session, settings: Settings, mail: MailBackend) -> FastAPI:
    app = FastAPI()
    fapi_users = make_fastapi_users(get_session, settings, mail)
    get_user_manager = make_manager_dep(get_session, settings, mail)

    # Only mount the register router from fastapi-users.
    # /auth/login and /auth/logout are custom (Tasks 12 / 13) — needed for lockout
    # and remember-me. We deliberately skip get_auth_router to avoid duplicate-route
    # registration conflicts.
    app.include_router(
        fapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
    )
    # Users router (PATCH /users/{id}, GET /users/me) — useful for admin/account UI later.
    app.include_router(
        fapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
    )

    @app.post("/auth/login", status_code=204)
    async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        remember: str = Form(default=""),
        db: AsyncSession = Depends(get_session),
        manager=Depends(get_user_manager),
    ):
        email = username
        ip = (request.client.host if request.client else None) or "127.0.0.1"
        remember_me = remember.lower() in ("1", "true", "on", "yes")

        # Check lockout before any authentication attempt
        if await is_locked_out(db, email=email, ip=ip):
            return JSONResponse(status_code=429, content={"detail": "Too many failed attempts"})

        # Authenticate: returns None for bad credentials (no exception in fapi-users 13)
        creds = SimpleNamespace(username=email, password=password)
        user = await manager.authenticate(creds)

        if user is None or not user.is_active:
            await record_attempt(db, email=email, ip=ip, success=False)
            return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

        # Mint access token
        ttl = TTL_REMEMBER if remember_me else TTL_NORMAL
        now = datetime.now(timezone.utc)
        token = secrets.token_urlsafe(32)
        db.add(AccessToken(
            token=token,
            user_id=user.id,
            created_at=now,
            expires_at=now + ttl,
        ))

        # Update last_login_at
        user.last_login_at = now
        db.add(user)

        await db.commit()

        # Record successful attempt and clear failed streak
        await record_attempt(db, email=email, ip=ip, success=True)
        await clear_email_streak(db, email=email)

        response = Response(status_code=204)
        response.set_cookie(
            key="schieber_session",
            value=token,
            max_age=int(ttl.total_seconds()),
            httponly=True,
            secure=settings.secure_cookie,
            samesite="lax",
        )
        return response

    return app
