from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from frontend.auth.models import User, AccessToken


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
