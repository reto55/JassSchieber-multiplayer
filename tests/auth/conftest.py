import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from frontend.auth.models import Base
from frontend.auth.email import ConsoleMailBackend
from frontend.auth.settings import Settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest_asyncio.fixture
async def db(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "k" * 32)
    monkeypatch.setenv("BASE_URL", "http://test")
    monkeypatch.setenv("SMTP_USER", "bot@test")
    monkeypatch.setenv("SMTP_APP_PASSWORD", "pw")
    monkeypatch.setenv("MAIL_BACKEND", "console")
    monkeypatch.setenv("ADMIN_BOOTSTRAP_EMAIL", "admin@test")
    return Settings()


@pytest.fixture
def mail():
    return ConsoleMailBackend()


@pytest_asyncio.fixture
async def app(engine, settings, mail):
    from frontend.auth.app import build_app  # implemented in Task 11
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session():
        async with factory() as s:
            yield s

    return build_app(get_session=get_session, settings=settings, mail=mail)


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
