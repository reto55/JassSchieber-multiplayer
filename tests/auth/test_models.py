import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from frontend.auth.models import (
    User,
    AccessToken,
    EmailToken,
    LockoutAttempt,
    Tombstone,
    AdminAudit,
)


pytestmark = pytest.mark.asyncio


async def test_create_user(db):
    u = User(
        id="11111111-1111-1111-1111-111111111111",
        email="a@b.c",
        username="alice",
        hashed_password="$2b$12$dummy",
        is_active=True,
        is_superuser=False,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(u)
    await db.commit()


async def test_email_token_unused_when_used_at_null(db):
    u = User(
        id="22222222-2222-2222-2222-222222222222",
        email="b@b.c",
        username="bob",
        hashed_password="x",
        is_active=True,
        is_superuser=False,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
    )
    db.add(u)
    t = EmailToken(
        token="t" * 43,
        user_id=u.id,
        purpose="verify",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(t)
    await db.commit()
    assert t.used_at is None


async def test_tombstone_unique_id(db):
    t = Tombstone(
        id="33333333-3333-3333-3333-333333333333",
        email_hash="a" * 64,
        username_hash="b" * 64,
        deleted_at=datetime.now(timezone.utc),
    )
    db.add(t)
    await db.commit()
