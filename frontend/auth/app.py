import secrets
import uuid as _uuid
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

from fastapi import FastAPI, Depends, Form, Request, Response, HTTPException, Body
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi_users import exceptions as fapi_exceptions
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from frontend.auth.users import make_fastapi_users, make_manager_dep
from frontend.auth.schemas import UserRead, UserCreate, UserUpdate
from frontend.auth.email import (
    MailBackend, Mail, render_verification, render_reset,
    render_change_email_confirm, render_change_email_notice, mask_email,
)
from frontend.auth.settings import Settings
from frontend.auth.models import AccessToken, User, EmailToken, Tombstone
from frontend.auth.tombstone import hash_email, hash_email as _he, hash_username as _hu
from frontend.auth.lockout import is_locked_out, record_attempt, clear_email_streak
from frontend.auth.deps import make_current_user_dep, make_require_admin_dep
from frontend.auth.passwords import validate_password
from frontend.auth.ratelimit import make_limiter, LIMITS


TTL_NORMAL = timedelta(hours=2)
TTL_REMEMBER = timedelta(days=30)

pwd_ctx = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")


def build_app(*, get_session, settings: Settings, mail: MailBackend) -> FastAPI:
    app = FastAPI()

    # Rate limiter — instantiated inside build_app so each app instance has its
    # own in-memory storage (avoids state leaking between tests).
    limiter = make_limiter()
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            {"detail": "rate limited"},
            status_code=429,
            headers={"Retry-After": "60"},
        )

    fapi_users = make_fastapi_users(get_session, settings, mail)
    get_user_manager = make_manager_dep(get_session, settings, mail)
    settings_obj = settings
    mail_obj = mail

    current_user_dep = make_current_user_dep(get_session)
    require_admin_dep = make_require_admin_dep(current_user_dep)

    # Users router (PATCH /users/{id}, GET /users/me) — useful for admin/account UI later.
    # NOTE: We do NOT mount the fastapi-users register router here because we need
    # to apply a rate limit on POST /auth/register. Instead we implement a thin
    # wrapper below that delegates to the UserManager directly.
    app.include_router(
        fapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
    )

    @app.post("/auth/register", response_model=UserRead, status_code=201)
    @limiter.limit(LIMITS["signup"])
    async def register(
        request: Request,
        user_create: UserCreate,
        manager=Depends(get_user_manager),
    ):
        try:
            created = await manager.create(user_create, safe=True, request=request)
        except fapi_exceptions.UserAlreadyExists:
            raise HTTPException(status_code=400, detail="REGISTER_USER_ALREADY_EXISTS")
        except fapi_exceptions.InvalidPasswordException as e:
            raise HTTPException(status_code=422, detail=str(e.reason))
        return UserRead.model_validate(created)

    @app.post("/auth/login", status_code=204)
    @limiter.limit(LIMITS["login"])
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

    @app.post("/auth/logout", status_code=204)
    async def logout(request: Request,
                     session: AsyncSession = Depends(get_session)):
        token = request.cookies.get("schieber_session")
        if token:
            await session.execute(delete(AccessToken).where(AccessToken.token == token))
            await session.commit()
        response = Response(status_code=204)
        response.delete_cookie(
            key="schieber_session",
            secure=settings_obj.secure_cookie,
            samesite="lax",
            httponly=True,
        )
        return response

    @app.get("/auth/me")
    async def me(user: User = Depends(current_user_dep)):
        return {
            "id": user.id, "email": user.email, "username": user.username,
            "is_verified": user.is_verified, "is_superuser": user.is_superuser,
        }

    @app.get("/auth/export")
    async def export_account(
        user: User = Depends(current_user_dep),
        session: AsyncSession = Depends(get_session),
    ):
        access_q = await session.execute(
            select(AccessToken).where(AccessToken.user_id == user.id)
        )
        email_q = await session.execute(
            select(EmailToken).where(EmailToken.user_id == user.id)
        )
        return {
            "user": {
                "id": user.id, "email": user.email, "username": user.username,
                "is_active": user.is_active, "is_verified": user.is_verified,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            },
            "access_tokens": [
                {"created_at": at.created_at.isoformat(),
                 "expires_at": at.expires_at.isoformat()}
                for at in access_q.scalars()
            ],
            "email_tokens": [
                {"purpose": et.purpose, "expires_at": et.expires_at.isoformat(),
                 "used_at": et.used_at.isoformat() if et.used_at else None}
                for et in email_q.scalars()
            ],
        }

    @app.get("/auth/verify", response_class=HTMLResponse)
    async def verify(token: str, session: AsyncSession = Depends(get_session)):
        q = select(EmailToken).where(
            EmailToken.token == token, EmailToken.purpose == "verify"
        )
        et = (await session.execute(q)).scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if et is None or et.used_at is not None:
            return HTMLResponse("<h1>Link expired or already used.</h1>", status_code=410)
        # Handle both naive and aware datetimes from database
        expires_at = et.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            return HTMLResponse("<h1>Link expired or already used.</h1>", status_code=410)
        et.used_at = now
        await session.execute(
            update(User).where(User.id == et.user_id).values(is_verified=True)
        )
        await session.commit()
        return HTMLResponse("<h1>Email verified. You can close this tab.</h1>")

    @app.post("/auth/resend-verification", status_code=202)
    async def resend_verification(
        user: User = Depends(current_user_dep),
        session: AsyncSession = Depends(get_session),
    ):
        token = secrets.token_urlsafe(32)
        session.add(EmailToken(
            token=token,
            user_id=user.id,
            purpose="verify",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        ))
        await session.commit()
        body = render_verification(
            username=user.username, base_url=settings_obj.base_url, token=token,
        )
        await mail_obj.send(Mail(
            to=user.email,
            subject="Confirm your Schieber account",
            body=body,
        ))
        return {"status": "sent"}

    @app.post("/auth/forgot", status_code=202)
    @limiter.limit(LIMITS["forgot"])
    @limiter.limit(LIMITS["forgot_day"])
    async def forgot(request: Request, payload: dict, session: AsyncSession = Depends(get_session)):
        email = payload.get("email", "").lower()
        u = (await session.execute(
            select(User).where(User.email == email, User.is_active == True)
        )).scalar_one_or_none()
        if u is None:
            return {"status": "ok"}
        token = secrets.token_urlsafe(32)
        session.add(EmailToken(
            token=token,
            user_id=u.id,
            purpose="reset",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        await session.commit()
        body = render_reset(username=u.username, base_url=settings_obj.base_url, token=token)
        await mail_obj.send(Mail(to=u.email, subject="Reset your Schieber password", body=body))
        return {"status": "ok"}

    @app.post("/auth/reset")
    @limiter.limit(LIMITS["reset"])
    async def reset(request: Request, payload: dict, session: AsyncSession = Depends(get_session)):
        token = payload.get("token", "")
        new_password = payload.get("new_password", "")
        et = (await session.execute(
            select(EmailToken).where(
                EmailToken.token == token, EmailToken.purpose == "reset"
            )
        )).scalar_one_or_none()
        now = datetime.now(timezone.utc)
        # Handle both naive and aware datetimes from database
        expires_at = et.expires_at if et else None
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if et is None or et.used_at is not None or (expires_at and expires_at < now):
            raise HTTPException(410, "link expired or used")
        u = (await session.execute(select(User).where(User.id == et.user_id))).scalar_one()
        validate_password(new_password, username=u.username, email=u.email)
        u.hashed_password = pwd_ctx.hash(new_password)
        et.used_at = datetime.now(timezone.utc)
        await session.execute(delete(AccessToken).where(AccessToken.user_id == u.id))
        await session.commit()
        return {"status": "ok"}

    @app.post("/auth/change-password")
    async def change_password(
        payload: dict,
        request: Request,
        user: User = Depends(current_user_dep),
        session: AsyncSession = Depends(get_session),
    ):
        current = payload.get("current_password", "")
        new = payload.get("new_password", "")
        u = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
        if not pwd_ctx.verify(current, u.hashed_password):
            raise HTTPException(401, "wrong current password")
        validate_password(new, username=u.username, email=u.email)
        u.hashed_password = pwd_ctx.hash(new)
        cur_token = request.cookies.get("schieber_session")
        await session.execute(delete(AccessToken).where(
            AccessToken.user_id == u.id, AccessToken.token != cur_token
        ))
        await session.commit()
        return {"status": "ok"}

    @app.post("/auth/change-email", status_code=202)
    async def change_email(
        payload: dict,
        request: Request,
        user: User = Depends(current_user_dep),
        session: AsyncSession = Depends(get_session),
    ):
        new_email = payload.get("new_email", "").lower()
        current = payload.get("current_password", "")
        u = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
        if not pwd_ctx.verify(current, u.hashed_password):
            raise HTTPException(401, "wrong current password")

        # collision check (live + tombstone <30d)
        existing = (await session.execute(
            select(User).where(User.email == new_email)
        )).scalar_one_or_none()
        if existing:
            raise HTTPException(409, "email already in use")

        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        if (await session.execute(
            select(Tombstone).where(
                Tombstone.email_hash == hash_email(new_email),
                Tombstone.deleted_at >= cutoff,
            )
        )).scalars().first():
            raise HTTPException(409, "email recently used")

        token = secrets.token_urlsafe(32)
        session.add(EmailToken(
            token=token,
            user_id=u.id,
            purpose="change_email",
            new_value=new_email,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        await session.commit()

        await mail_obj.send(Mail(
            to=new_email,
            subject="Confirm new email for Schieber",
            body=render_change_email_confirm(base_url=settings_obj.base_url, token=token),
        ))
        await mail_obj.send(Mail(
            to=u.email,
            subject="Email change requested on your Schieber account",
            body=render_change_email_notice(masked_new_email=mask_email(new_email)),
        ))
        return {"status": "sent"}

    @app.get("/auth/confirm-email")
    async def confirm_email(token: str, session: AsyncSession = Depends(get_session)):
        et = (await session.execute(
            select(EmailToken).where(
                EmailToken.token == token, EmailToken.purpose == "change_email"
            )
        )).scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if et is None or et.used_at is not None:
            raise HTTPException(410, "link expired or used")
        # Handle both naive and aware datetimes from database
        expires_at = et.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise HTTPException(410, "link expired or used")
        u = (await session.execute(select(User).where(User.id == et.user_id))).scalar_one()
        u.email = et.new_value
        et.used_at = now
        await session.commit()
        return {"status": "ok"}

    @app.delete("/auth/account")
    async def delete_account(
        payload: dict = Body(...),
        user: User = Depends(current_user_dep),
        session: AsyncSession = Depends(get_session),
    ):
        current = payload.get("current_password", "")
        u = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
        if not pwd_ctx.verify(current, u.hashed_password):
            raise HTTPException(401, "wrong current password")
        # Tombstone first (preserves original hashes)
        session.add(Tombstone(
            id=u.id,
            email_hash=_he(u.email),
            username_hash=_hu(u.username),
            deleted_at=datetime.now(timezone.utc),
        ))
        # Anonymise
        u.email = f"deleted-{_uuid.uuid4()}@invalid"
        u.username = f"deleted-{u.id[:8]}"
        u.hashed_password = ""
        u.is_active = False
        # Revoke
        await session.execute(delete(AccessToken).where(AccessToken.user_id == u.id))
        await session.commit()
        resp = JSONResponse({"status": "ok"})
        resp.delete_cookie(
            key="schieber_session",
            secure=settings_obj.secure_cookie,
            samesite="lax",
            httponly=True,
        )
        return resp

    return app
