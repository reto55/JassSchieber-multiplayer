from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from frontend.auth.models import User, AccessToken
from frontend.auth.guest import (
    Guest,
    issue_guest_cookie,
    read_guest_cookie,
    GuestCookieError,
)


def make_current_user_dep(get_session):
    async def current_user(request: Request,
                           session: AsyncSession = Depends(get_session)) -> User:
        token = request.cookies.get("schieber_session")
        if not token:
            raise HTTPException(401, "not authenticated")
        q = select(AccessToken).where(
            AccessToken.token == token,
            AccessToken.expires_at > datetime.now(timezone.utc),
        )
        at = (await session.execute(q)).scalar_one_or_none()
        if at is None:
            raise HTTPException(401, "session expired or revoked")
        u = (await session.execute(
            select(User).where(User.id == at.user_id)
        )).scalar_one_or_none()
        if u is None or not u.is_active:
            await session.execute(delete(AccessToken).where(AccessToken.token == token))
            await session.commit()
            raise HTTPException(401, "user inactive")
        return u
    return current_user


def make_require_admin_dep(current_user_dep):
    async def require_admin(user: User = Depends(current_user_dep)) -> User:
        if not user.is_superuser:
            raise HTTPException(403, "admin required")
        return user
    return require_admin


def make_current_principal_dep(get_session, secret_key, secure_cookie):
    """Yield current User or Guest. Mints a guest cookie when neither cookie present."""

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
