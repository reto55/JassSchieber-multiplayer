"""
tests/conftest.py — shared pytest fixtures for the top-level test suite.

Provides an autouse fixture that stubs out the auth globals in ausbau.server
so that tests which exercise the WebSocket endpoint do not require real env
vars or a real database.  The fixture pre-populates:

  * ``_auth_settings`` — lightweight stub with ``secret_key`` attribute.
  * ``_auth_factory``  — async context-manager factory that always returns
                         zero rows (no valid session token).

This keeps the existing server-level tests (E4.x) green after the principal-
injection changes introduced in Task 23.
"""
import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock


class _StubAuthSettings:
    secret_key = "k" * 32
    auth_db_url = "sqlite+aiosqlite:///:memory:"


def _make_null_factory():
    """Return an async session factory whose sessions always find nothing."""

    @asynccontextmanager
    async def _factory():
        session = AsyncMock()
        # scalar_one_or_none always returns None → no token, no user
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)
        yield session

    return _factory


@pytest.fixture(autouse=True)
def _patch_server_auth_settings(monkeypatch):
    """Ensure ausbau.server auth globals are pre-populated so _ensure_auth_initialised()
    never calls load_settings() (which requires env vars) during tests."""
    try:
        import ausbau.server as srv
    except Exception:
        # If ausbau.server can't be imported (e.g. missing dependency in some env),
        # skip the patch gracefully.
        return
    monkeypatch.setattr(srv, "_auth_settings", _StubAuthSettings())
    monkeypatch.setattr(srv, "_auth_factory", _make_null_factory())
