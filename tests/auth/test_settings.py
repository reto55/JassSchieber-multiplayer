import os
import pytest

from frontend.auth.settings import Settings, load_settings


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    """Suppress .env loading (both `load_dotenv` and pydantic-settings'
    own env_file reader) and clear auth env vars so each test sees only
    what it explicitly sets via monkeypatch.setenv."""
    from pydantic_settings import SettingsConfigDict
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: None)
    monkeypatch.setattr(
        Settings, "model_config",
        SettingsConfigDict(env_file=None, extra="ignore"),
    )
    for var in (
        "SECRET_KEY", "BASE_URL", "SMTP_HOST", "SMTP_PORT",
        "SMTP_USER", "SMTP_APP_PASSWORD", "MAIL_BACKEND",
        "ADMIN_BOOTSTRAP_EMAIL", "AUTH_DB_URL",
    ):
        monkeypatch.delenv(var, raising=False)


def test_settings_required_fields(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "k" * 32)
    monkeypatch.setenv("BASE_URL", "https://example.test")
    monkeypatch.setenv("SMTP_USER", "bot@example.test")
    monkeypatch.setenv("SMTP_APP_PASSWORD", "abcd efgh ijkl mnop")
    monkeypatch.setenv("ADMIN_BOOTSTRAP_EMAIL", "admin@example.test")
    s = load_settings()
    assert s.secret_key == "k" * 32
    assert s.base_url == "https://example.test"
    assert s.mail_backend == "smtp"  # default
    assert s.smtp_host == "smtp.gmail.com"  # default
    assert s.smtp_port == 587  # default


def test_settings_missing_admin_bootstrap_raises(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "k" * 32)
    monkeypatch.setenv("BASE_URL", "https://example.test")
    monkeypatch.setenv("SMTP_USER", "bot@example.test")
    monkeypatch.setenv("SMTP_APP_PASSWORD", "x")
    with pytest.raises(RuntimeError, match="ADMIN_BOOTSTRAP_EMAIL"):
        load_settings()


def test_settings_secure_cookie_inferred_from_https(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "k" * 32)
    monkeypatch.setenv("SMTP_USER", "bot@x")
    monkeypatch.setenv("SMTP_APP_PASSWORD", "x")
    monkeypatch.setenv("ADMIN_BOOTSTRAP_EMAIL", "a@x")

    monkeypatch.setenv("BASE_URL", "https://x")
    assert load_settings().secure_cookie is True

    monkeypatch.setenv("BASE_URL", "http://localhost:8765")
    assert load_settings().secure_cookie is False
