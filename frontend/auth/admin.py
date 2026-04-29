from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from frontend.auth.models import User, AccessToken, AdminAudit


def make_admin_router(get_session, require_admin):
    router = APIRouter(prefix="/admin")

    async def audit(session, *, admin_id, action, target_id, reason, ip):
        session.add(AdminAudit(
            admin_id=admin_id, action=action, target_id=target_id,
            reason=reason, ip=ip, created_at=datetime.now(timezone.utc),
        ))
        await session.commit()

    @router.get("/users")
    async def list_users(
        page: int = 1, q: str = "",
        admin: User = Depends(require_admin),
        session: AsyncSession = Depends(get_session),
    ):
        limit = 50
        offset = (page - 1) * limit
        base = select(User)
        if q:
            base = base.where(
                (User.email.ilike(f"%{q}%")) | (User.username.ilike(f"%{q}%"))
            )
        base = base.order_by(User.created_at.desc()).limit(limit).offset(offset)
        users = (await session.execute(base)).scalars().all()
        return [{
            "id": u.id, "email": u.email, "username": u.username,
            "is_active": u.is_active, "is_verified": u.is_verified,
            "is_superuser": u.is_superuser,
            "created_at": u.created_at.isoformat(),
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        } for u in users]

    @router.post("/users/{user_id}/ban")
    async def ban(
        user_id: str, request: Request, payload: Optional[dict] = None,
        admin: User = Depends(require_admin),
        session: AsyncSession = Depends(get_session),
    ):
        u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if u is None:
            raise HTTPException(404)
        u.is_active = False
        await session.execute(delete(AccessToken).where(AccessToken.user_id == u.id))
        await session.commit()
        await audit(session, admin_id=admin.id, action="ban", target_id=u.id,
                    reason=(payload or {}).get("reason"),
                    ip=request.client.host if request.client else "?")
        return {"status": "banned"}

    @router.post("/users/{user_id}/unban")
    async def unban(
        user_id: str, request: Request,
        admin: User = Depends(require_admin),
        session: AsyncSession = Depends(get_session),
    ):
        u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if u is None:
            raise HTTPException(404)
        u.is_active = True
        await session.commit()
        await audit(session, admin_id=admin.id, action="unban", target_id=u.id,
                    reason=None, ip=request.client.host if request.client else "?")
        return {"status": "unbanned"}

    @router.post("/users/{user_id}/promote")
    async def promote(
        user_id: str, request: Request,
        admin: User = Depends(require_admin),
        session: AsyncSession = Depends(get_session),
    ):
        u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if u is None:
            raise HTTPException(404)
        u.is_superuser = True
        await session.commit()
        await audit(session, admin_id=admin.id, action="promote", target_id=u.id,
                    reason=None, ip=request.client.host if request.client else "?")
        return {"status": "promoted"}

    @router.post("/users/{user_id}/demote")
    async def demote(
        user_id: str, request: Request,
        admin: User = Depends(require_admin),
        session: AsyncSession = Depends(get_session),
    ):
        if user_id == admin.id:
            raise HTTPException(409, "cannot demote self")
        u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if u is None:
            raise HTTPException(404)
        u.is_superuser = False
        await session.commit()
        await audit(session, admin_id=admin.id, action="demote", target_id=u.id,
                    reason=None, ip=request.client.host if request.client else "?")
        return {"status": "demoted"}

    @router.post("/users/{user_id}/force-verify")
    async def force_verify(
        user_id: str, request: Request,
        admin: User = Depends(require_admin),
        session: AsyncSession = Depends(get_session),
    ):
        u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if u is None:
            raise HTTPException(404)
        u.is_verified = True
        await session.commit()
        await audit(session, admin_id=admin.id, action="force_verify", target_id=u.id,
                    reason=None, ip=request.client.host if request.client else "?")
        return {"status": "verified"}

    @router.get("/audit")
    async def audit_log(
        admin: User = Depends(require_admin),
        session: AsyncSession = Depends(get_session),
    ):
        rows = (await session.execute(
            select(AdminAudit).order_by(desc(AdminAudit.created_at)).limit(200)
        )).scalars().all()
        return [{
            "admin_id": r.admin_id, "action": r.action, "target_id": r.target_id,
            "reason": r.reason, "created_at": r.created_at.isoformat(), "ip": r.ip,
        } for r in rows]

    return router
