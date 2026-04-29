from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from frontend.auth.models import LockoutAttempt


WINDOW = timedelta(minutes=15)
EMAIL_THRESHOLD = 5
IP_THRESHOLD = 10
LOCKOUT_DURATION = timedelta(minutes=15)


async def is_locked_out(db: AsyncSession, *, email: str, ip: str) -> bool:
    cutoff = datetime.now(timezone.utc) - WINDOW
    q_email = select(func.count()).select_from(LockoutAttempt).where(
        LockoutAttempt.email == email,
        LockoutAttempt.attempted_at >= cutoff,
        LockoutAttempt.success == False,  # noqa: E712
    )
    q_ip = select(func.count()).select_from(LockoutAttempt).where(
        LockoutAttempt.ip == ip,
        LockoutAttempt.attempted_at >= cutoff,
        LockoutAttempt.success == False,  # noqa: E712
    )
    fails_email = (await db.execute(q_email)).scalar_one()
    fails_ip = (await db.execute(q_ip)).scalar_one()
    return fails_email >= EMAIL_THRESHOLD or fails_ip >= IP_THRESHOLD


async def record_attempt(db: AsyncSession, *, email: str, ip: str, success: bool) -> None:
    db.add(LockoutAttempt(
        email=email, ip=ip,
        attempted_at=datetime.now(timezone.utc),
        success=success,
    ))
    await db.commit()


async def clear_email_streak(db: AsyncSession, *, email: str) -> None:
    """Mark a recent successful login: deletes failed attempts for that email."""
    await db.execute(delete(LockoutAttempt).where(
        LockoutAttempt.email == email,
        LockoutAttempt.success == False,  # noqa: E712
    ))
    await db.commit()
