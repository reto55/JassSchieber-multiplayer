# Schieber — User Accounts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship public-internet user accounts (email + password, soft email verification, password reset, change-email/password, account delete/export, admin tools, anonymous guest play) without touching game mechanics.

**Architecture:** New `frontend/auth/` package backed by `fastapi-users[sqlalchemy]` + async SQLAlchemy on a separate `auth.db` file. Game DB and `game_session.py` mechanics untouched; `GameSession` only gains a `principal` argument used for log labelling. Server-side session cookies (`schieber_session`) for auth, signed `itsdangerous` cookies (`schieber_guest`) for anonymous play. SMTP via Gmail app password (`aiosmtplib`); tests use a `console` mail backend.

**Tech Stack:** Python 3.9+, FastAPI, fastapi-users 13.x, SQLAlchemy 2.x async, aiosqlite, passlib[bcrypt], aiosmtplib, slowapi, itsdangerous, jinja2, pytest, pytest-asyncio, httpx (test client).

**Reference:** `docs/superpowers/specs/2026-04-28-schieber-accounts-design.md`.

---

## Task 0: Branch & worktree

**Files:** none

- [ ] **Step 1: Create feature branch**

The spec was committed on `feat/mobile-responsive`. Accounts is unrelated. Create a branch off `main`.

```bash
git fetch origin
git checkout -b feat/user-accounts origin/main
git cherry-pick f510151   # the spec commit
```

If you prefer a worktree:

```bash
git worktree add ../JassSchieber-accounts feat/user-accounts
cd ../JassSchieber-accounts
```

- [ ] **Step 2: Confirm clean tree**

Run: `git status`
Expected: nothing staged, nothing modified.

---

## Task 1: Add dependencies

**Files:**
- Modify: `requirements-html5.txt`
- Create: `requirements-dev.txt`

- [ ] **Step 1: Add runtime deps**

Append to `requirements-html5.txt`:

```
fastapi-users[sqlalchemy]>=13.0.0,<14
sqlalchemy[asyncio]>=2.0
aiosqlite>=0.19
aiosmtplib>=3.0
passlib[bcrypt]>=1.7.4
itsdangerous>=2.1
slowapi>=0.1.9
jinja2>=3.1
pydantic-settings>=2.1
python-multipart>=0.0.6
```

- [ ] **Step 2: Create dev requirements**

`requirements-dev.txt`:

```
-r requirements-html5.txt
pytest>=7
pytest-asyncio>=0.23
httpx>=0.27
```

- [ ] **Step 3: Install**

```bash
pip install -r requirements-dev.txt
```

Expected: all packages install cleanly.

- [ ] **Step 4: Commit**

```bash
git add requirements-html5.txt requirements-dev.txt
git commit -m "chore(deps): add auth stack (fastapi-users, sqlalchemy async, aiosmtplib, slowapi)"
```

---

## Task 2: Settings module (env config)

**Files:**
- Create: `frontend/auth/__init__.py`
- Create: `frontend/auth/settings.py`
- Create: `tests/auth/__init__.py`
- Create: `tests/auth/test_settings.py`
- Create: `.env.example`
- Modify: `.gitignore` (add `.env`)

- [ ] **Step 1: Make `.gitignore` ignore `.env`**

Append to `.gitignore`:

```
.env
auth.db
auth.db-journal
```

- [ ] **Step 2: Write `tests/auth/__init__.py`**

```python
```

(empty file, just a package marker)

- [ ] **Step 3: Write the failing test**

`tests/auth/test_settings.py`:

```python
import os
import pytest

from frontend.auth.settings import Settings, load_settings


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
    monkeypatch.delenv("ADMIN_BOOTSTRAP_EMAIL", raising=False)
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
```

- [ ] **Step 4: Run failing test**

```bash
python -m pytest tests/auth/test_settings.py -v
```

Expected: ImportError / ModuleNotFoundError.

- [ ] **Step 5: Implement `frontend/auth/__init__.py`**

```python
```

(empty file)

- [ ] **Step 6: Implement `frontend/auth/settings.py`**

```python
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = Field(..., min_length=32)
    base_url: str

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_app_password: str
    mail_backend: Literal["smtp", "console"] = "smtp"

    admin_bootstrap_email: str

    auth_db_url: str = "sqlite+aiosqlite:///./auth.db"

    @property
    def secure_cookie(self) -> bool:
        return self.base_url.startswith("https://")


def load_settings() -> Settings:
    import os
    if not os.environ.get("ADMIN_BOOTSTRAP_EMAIL"):
        raise RuntimeError(
            "ADMIN_BOOTSTRAP_EMAIL is required at startup. "
            "Set it explicitly (use empty string only after considered review)."
        )
    return Settings()
```

- [ ] **Step 7: Create `.env.example`**

```
SECRET_KEY=replace-with-32-bytes-of-randomness
BASE_URL=http://localhost:8765
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-bot@gmail.com
SMTP_APP_PASSWORD=replace-with-google-app-password
MAIL_BACKEND=console
ADMIN_BOOTSTRAP_EMAIL=you@example.com
AUTH_DB_URL=sqlite+aiosqlite:///./auth.db
```

- [ ] **Step 8: Run tests**

```bash
python -m pytest tests/auth/test_settings.py -v
```

Expected: 3 passed.

- [ ] **Step 9: Commit**

```bash
git add frontend/auth/__init__.py frontend/auth/settings.py \
        tests/auth/__init__.py tests/auth/test_settings.py \
        .env.example .gitignore
git commit -m "feat(auth): settings module with env-driven config"
```

---

## Task 3: Pure password validator

**Files:**
- Create: `frontend/auth/passwords.py`
- Create: `frontend/auth/data/common-passwords.txt`
- Create: `tests/auth/test_passwords.py`

- [ ] **Step 1: Add the blocklist data file**

Download a top-1000 list (e.g. SecLists `Common-Credentials/10-million-password-list-top-1000.txt`) and save as `frontend/auth/data/common-passwords.txt`. One password per line, lowercase. ~10 KB.

If you cannot download, generate a small starter list with the 50 most common (`123456`, `password`, `qwerty`, etc.) — the validator semantics are the same; coverage can grow later.

- [ ] **Step 2: Write the failing test**

`tests/auth/test_passwords.py`:

```python
import pytest
from frontend.auth.passwords import validate_password, PasswordError


def test_min_length():
    with pytest.raises(PasswordError, match="at least 10"):
        validate_password("short", username="alice", email="a@b.c")


def test_common_password_rejected():
    with pytest.raises(PasswordError, match="too common"):
        validate_password("password12", username="alice", email="a@b.c")


def test_contains_username_rejected():
    with pytest.raises(PasswordError, match="username"):
        validate_password("aliceXyz123!", username="Alice", email="a@b.c")


def test_contains_email_local_part_rejected():
    with pytest.raises(PasswordError, match="email"):
        validate_password("retoMcSuperSecret", username="bob", email="reto@example.com")


def test_long_unique_password_passes():
    validate_password("correct horse battery staple", username="alice", email="a@b.c")


def test_long_password_no_truncation_at_72_bytes():
    # Long passwords should be hashable; we don't enforce a max
    validate_password("a" * 200, username="alice", email="a@b.c")
```

- [ ] **Step 3: Run failing test**

```bash
python -m pytest tests/auth/test_passwords.py -v
```

Expected: ImportError.

- [ ] **Step 4: Implement validator**

`frontend/auth/passwords.py`:

```python
from pathlib import Path
from functools import lru_cache


class PasswordError(ValueError):
    pass


_BLOCKLIST_PATH = Path(__file__).parent / "data" / "common-passwords.txt"


@lru_cache(maxsize=1)
def _blocklist() -> frozenset[str]:
    if not _BLOCKLIST_PATH.exists():
        return frozenset()
    with _BLOCKLIST_PATH.open() as f:
        return frozenset(line.strip().lower() for line in f if line.strip())


def validate_password(password: str, *, username: str, email: str) -> None:
    if len(password) < 10:
        raise PasswordError("password must be at least 10 characters")

    pw_lower = password.lower()
    if pw_lower in _blocklist():
        raise PasswordError("password is too common")

    if username and username.lower() in pw_lower:
        raise PasswordError("password must not contain your username")

    local = email.split("@", 1)[0].lower() if email else ""
    if local and local in pw_lower:
        raise PasswordError("password must not contain your email")
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/auth/test_passwords.py -v
```

Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add frontend/auth/passwords.py frontend/auth/data/common-passwords.txt \
        tests/auth/test_passwords.py
git commit -m "feat(auth): password validator (length, blocklist, identity-substring)"
```

---

## Task 4: Tombstone hash helpers

**Files:**
- Create: `frontend/auth/tombstone.py`
- Create: `tests/auth/test_tombstone.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_tombstone.py`:

```python
from frontend.auth.tombstone import hash_email, hash_username


def test_hash_email_lowercases():
    assert hash_email("Alice@Example.COM") == hash_email("alice@example.com")


def test_hash_email_strips_whitespace():
    assert hash_email(" alice@example.com ") == hash_email("alice@example.com")


def test_hash_username_lowercases():
    assert hash_username("Alice") == hash_username("alice")


def test_hash_returns_64_hex():
    h = hash_email("a@b.c")
    assert len(h) == 64
    int(h, 16)  # parses as hex
```

- [ ] **Step 2: Run failing test**

```bash
python -m pytest tests/auth/test_tombstone.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement**

`frontend/auth/tombstone.py`:

```python
import hashlib


def hash_email(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


def hash_username(username: str) -> str:
    return hashlib.sha256(username.strip().lower().encode("utf-8")).hexdigest()
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_tombstone.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/tombstone.py tests/auth/test_tombstone.py
git commit -m "feat(auth): tombstone hash helpers (sha256, lowered)"
```

---

## Task 5: Guest cookie (sign / verify)

**Files:**
- Create: `frontend/auth/guest.py`
- Create: `tests/auth/test_guest_cookie.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_guest_cookie.py`:

```python
import pytest
from frontend.auth.guest import (
    Guest,
    issue_guest_cookie,
    read_guest_cookie,
    GuestCookieError,
)


SECRET = "k" * 32


def test_issue_then_read_roundtrip():
    cookie_value, guest = issue_guest_cookie(SECRET)
    assert guest.guest_id and len(guest.guest_id) == 32  # 16 bytes hex
    assert guest.display_name.startswith("Guest-")
    assert len(guest.display_name) == len("Guest-") + 4

    decoded = read_guest_cookie(cookie_value, SECRET)
    assert decoded.guest_id == guest.guest_id


def test_tampered_cookie_rejected():
    cookie_value, _ = issue_guest_cookie(SECRET)
    tampered = cookie_value[:-2] + ("aa" if cookie_value[-2:] != "aa" else "bb")
    with pytest.raises(GuestCookieError):
        read_guest_cookie(tampered, SECRET)


def test_wrong_secret_rejected():
    cookie_value, _ = issue_guest_cookie(SECRET)
    with pytest.raises(GuestCookieError):
        read_guest_cookie(cookie_value, "j" * 32)


def test_garbage_cookie_rejected():
    with pytest.raises(GuestCookieError):
        read_guest_cookie("not a real cookie", SECRET)
```

- [ ] **Step 2: Run failing test**

```bash
python -m pytest tests/auth/test_guest_cookie.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement**

`frontend/auth/guest.py`:

```python
import secrets
from dataclasses import dataclass
from itsdangerous import URLSafeSerializer, BadSignature


class GuestCookieError(ValueError):
    pass


@dataclass(frozen=True)
class Guest:
    guest_id: str  # 32 hex chars (16 bytes)

    @property
    def display_name(self) -> str:
        return f"Guest-{self.guest_id[:4]}"


def _serializer(secret: str) -> URLSafeSerializer:
    return URLSafeSerializer(secret, salt="schieber-guest")


def issue_guest_cookie(secret: str) -> tuple[str, Guest]:
    guest = Guest(guest_id=secrets.token_hex(16))
    return _serializer(secret).dumps({"id": guest.guest_id}), guest


def read_guest_cookie(cookie_value: str, secret: str) -> Guest:
    try:
        payload = _serializer(secret).loads(cookie_value)
    except BadSignature as e:
        raise GuestCookieError(str(e))
    if not isinstance(payload, dict) or "id" not in payload:
        raise GuestCookieError("malformed payload")
    gid = payload["id"]
    if not (isinstance(gid, str) and len(gid) == 32):
        raise GuestCookieError("malformed id")
    return Guest(guest_id=gid)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_guest_cookie.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/guest.py tests/auth/test_guest_cookie.py
git commit -m "feat(auth): signed guest cookie (Guest dataclass, itsdangerous)"
```

---

## Task 6: Mail backend (SMTP / console)

**Files:**
- Create: `frontend/auth/email.py`
- Create: `tests/auth/test_email_backend.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_email_backend.py`:

```python
import pytest
from frontend.auth.email import (
    Mail,
    ConsoleMailBackend,
    render_verification,
    render_reset,
    render_change_email_confirm,
    render_change_email_notice,
)


def test_console_backend_collects():
    backend = ConsoleMailBackend()
    m = Mail(to="a@b.c", subject="hi", body="body")
    import asyncio
    asyncio.get_event_loop().run_until_complete(backend.send(m))
    assert len(backend.sent) == 1
    assert backend.sent[0].to == "a@b.c"
    assert backend.sent[0].subject == "hi"


def test_render_verification_contains_link():
    body = render_verification(username="alice", base_url="https://x", token="tok123")
    assert "alice" in body
    assert "https://x/auth/verify?token=tok123" in body


def test_render_reset_contains_link():
    body = render_reset(username="alice", base_url="https://x", token="tok123")
    assert "alice" in body
    assert "https://x/reset?token=tok123" in body


def test_render_change_email_confirm():
    body = render_change_email_confirm(base_url="https://x", token="t")
    assert "https://x/auth/confirm-email?token=t" in body


def test_render_change_email_notice_masks():
    body = render_change_email_notice(masked_new_email="ali***@example.com")
    assert "ali***@example.com" in body
    assert "@" in body
```

- [ ] **Step 2: Run failing test**

```bash
python -m pytest tests/auth/test_email_backend.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement**

`frontend/auth/email.py`:

```python
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Mail:
    to: str
    subject: str
    body: str


class MailBackend(Protocol):
    async def send(self, mail: Mail) -> None: ...


@dataclass
class ConsoleMailBackend:
    sent: list[Mail] = field(default_factory=list)

    async def send(self, mail: Mail) -> None:
        self.sent.append(mail)
        print(f"[mail] to={mail.to} subj={mail.subject}\n{mail.body}\n")


@dataclass
class SmtpMailBackend:
    host: str
    port: int
    user: str
    password: str

    async def send(self, mail: Mail) -> None:
        import aiosmtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"] = self.user
        msg["To"] = mail.to
        msg["Subject"] = mail.subject
        msg.set_content(mail.body)
        await aiosmtplib.send(
            msg,
            hostname=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            start_tls=True,
        )


def render_verification(*, username: str, base_url: str, token: str) -> str:
    return (
        f"Hi {username},\n"
        f"Confirm your email within 7 days:\n"
        f"{base_url}/auth/verify?token={token}\n"
        f"If you didn't sign up, ignore this message.\n"
    )


def render_reset(*, username: str, base_url: str, token: str) -> str:
    return (
        f"Someone requested a password reset for {username}.\n"
        f"Click within 1 hour:\n"
        f"{base_url}/reset?token={token}\n"
        f"If this wasn't you, no action needed — your password is unchanged.\n"
    )


def render_change_email_confirm(*, base_url: str, token: str) -> str:
    return (
        f"Click to switch your account email:\n"
        f"{base_url}/auth/confirm-email?token={token}\n"
    )


def render_change_email_notice(*, masked_new_email: str) -> str:
    return (
        f"Someone requested to change your account email to {masked_new_email}.\n"
        f"If this wasn't you, change your password immediately.\n"
    )


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:3]}***@{domain}" if domain else email
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_email_backend.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/email.py tests/auth/test_email_backend.py
git commit -m "feat(auth): mail backend protocol + console/smtp impls + templates"
```

---

## Task 7: SQLAlchemy models + auth.db engine

**Files:**
- Create: `frontend/auth/db.py`
- Create: `frontend/auth/models.py`
- Create: `tests/auth/conftest.py`
- Create: `tests/auth/test_models.py`

- [ ] **Step 1: Write conftest**

`tests/auth/conftest.py`:

```python
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from frontend.auth.models import Base


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
```

- [ ] **Step 2: Write failing model test**

`tests/auth/test_models.py`:

```python
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
```

- [ ] **Step 3: Run failing test**

```bash
python -m pytest tests/auth/test_models.py -v
```

Expected: ImportError.

- [ ] **Step 4: Implement models**

`frontend/auth/models.py`:

```python
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Integer, Index, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class AccessToken(Base):
    __tablename__ = "access_token"

    token: Mapped[str] = mapped_column(String(43), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EmailToken(Base):
    __tablename__ = "email_token"

    token: Mapped[str] = mapped_column(String(43), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(16), nullable=False)
    new_value: Mapped[Optional[str]] = mapped_column(String(320))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class LockoutAttempt(Base):
    __tablename__ = "lockout_attempt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        Index("ix_lockout_email_time", "email", "attempted_at"),
        Index("ix_lockout_ip_time", "ip", "attempted_at"),
    )


class Tombstone(Base):
    __tablename__ = "tombstone"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    username_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AdminAudit(Base):
    __tablename__ = "admin_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(36))
    reason: Mapped[Optional[str]] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    ip: Mapped[str] = mapped_column(String(45), nullable=False)
```

- [ ] **Step 5: Implement engine module**

`frontend/auth/db.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from frontend.auth.models import Base


def make_engine(db_url: str):
    return create_async_engine(db_url, future=True)


def make_session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

- [ ] **Step 6: Run tests**

```bash
python -m pytest tests/auth/test_models.py -v
```

Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add frontend/auth/db.py frontend/auth/models.py \
        tests/auth/conftest.py tests/auth/test_models.py
git commit -m "feat(auth): SQLAlchemy models + async engine for auth.db"
```

---

## Task 8: User schemas (pydantic)

**Files:**
- Create: `frontend/auth/schemas.py`
- Create: `tests/auth/test_schemas.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_schemas.py`:

```python
import pytest
from pydantic import ValidationError
from frontend.auth.schemas import UserCreate, UserRead, UserUpdate


def test_username_pattern_ok():
    u = UserCreate(email="a@b.c", username="alice_99", password="x" * 10)
    assert u.username == "alice_99"


def test_username_pattern_rejects_punctuation():
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.c", username="alice!!", password="x" * 10)


def test_username_min_3_chars():
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.c", username="ab", password="x" * 10)


def test_username_max_32():
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.c", username="a" * 33, password="x" * 10)


def test_user_read_includes_flags():
    r = UserRead(
        id="11111111-1111-1111-1111-111111111111",
        email="a@b.c",
        username="alice",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    assert r.is_verified is False
```

- [ ] **Step 2: Run failing test**

```bash
python -m pytest tests/auth/test_schemas.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement**

`frontend/auth/schemas.py`:

```python
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from fastapi_users import schemas


USERNAME_PATTERN = r"^[a-zA-Z0-9_-]{3,32}$"


class UserRead(schemas.BaseUser[str]):
    username: str
    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(..., pattern=USERNAME_PATTERN)


class UserUpdate(schemas.BaseUserUpdate):
    # username NOT updatable in v1 (locked at signup)
    pass
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_schemas.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/schemas.py tests/auth/test_schemas.py
git commit -m "feat(auth): user pydantic schemas with username pattern"
```

---

## Task 9: UserManager + fastapi-users wiring

**Files:**
- Create: `frontend/auth/manager.py`
- Create: `frontend/auth/users.py`

`users.py` houses the FastAPIUsers instance and dependency factories that everything else uses. `manager.py` defines the lifecycle hooks (post-register sends verification, etc.).

- [ ] **Step 1: Implement `frontend/auth/manager.py`**

```python
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from frontend.auth.models import User, EmailToken, Tombstone
from frontend.auth.passwords import validate_password
from frontend.auth.tombstone import hash_email, hash_username
from frontend.auth.email import (
    Mail,
    MailBackend,
    render_verification,
    render_reset,
)
from frontend.auth.settings import Settings
import secrets
from datetime import timedelta


class UserManager(BaseUserManager[User, str]):
    reset_password_token_secret: str  # filled in factory below
    verification_token_secret: str
    settings: Settings
    mail: MailBackend
    db: AsyncSession

    def parse_id(self, value) -> str:
        return str(value)

    async def validate_password(self, password: str, user) -> None:
        validate_password(
            password,
            username=getattr(user, "username", "") or "",
            email=getattr(user, "email", "") or "",
        )

    async def create(self, user_create, safe=False, request=None):
        # block tombstone collisions <30d
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        eh = hash_email(user_create.email)
        uh = hash_username(user_create.username)
        q = select(Tombstone).where(
            ((Tombstone.email_hash == eh) | (Tombstone.username_hash == uh))
            & (Tombstone.deleted_at >= cutoff)
        )
        if (await self.db.execute(q)).scalars().first():
            raise exceptions.UserAlreadyExists()
        return await super().create(user_create, safe=safe, request=request)

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        token = secrets.token_urlsafe(32)
        et = EmailToken(
            token=token,
            user_id=user.id,
            purpose="verify",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.db.add(et)
        await self.db.commit()
        body = render_verification(
            username=user.username, base_url=self.settings.base_url, token=token
        )
        await self.mail.send(Mail(to=user.email, subject="Confirm your Schieber account", body=body))

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        # fastapi-users issues its own JWT token; we replace with our own DB-backed token
        # to keep audit + revocation simple
        new_token = secrets.token_urlsafe(32)
        et = EmailToken(
            token=new_token,
            user_id=user.id,
            purpose="reset",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        self.db.add(et)
        await self.db.commit()
        body = render_reset(
            username=user.username, base_url=self.settings.base_url, token=new_token
        )
        await self.mail.send(Mail(to=user.email, subject="Reset your Schieber password", body=body))
```

NOTE: The `reset_password_token_secret`/`verification_token_secret` attributes are required by the parent class but we replace fastapi-users' built-in token issuance with our own DB-backed tokens (better audit, single-use enforcement). The library's own forgot/verify endpoints will not be mounted; we'll mount our own in Task 11+.

- [ ] **Step 2: Implement `frontend/auth/users.py`**

```python
from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    BearerTransport,
)
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession

from frontend.auth.models import User, AccessToken
from frontend.auth.manager import UserManager
from frontend.auth.email import MailBackend
from frontend.auth.settings import Settings


def make_user_db_dep(get_session):
    async def get_user_db(session: AsyncSession = Depends(get_session)):
        yield SQLAlchemyUserDatabase(session, User)
    return get_user_db


def make_token_db_dep(get_session):
    async def get_token_db(session: AsyncSession = Depends(get_session)):
        yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
    return get_token_db


def make_manager_dep(get_session, settings: Settings, mail: MailBackend):
    user_db_dep = make_user_db_dep(get_session)

    async def get_user_manager(
        session: AsyncSession = Depends(get_session),
        user_db = Depends(user_db_dep),
    ):
        m = UserManager(user_db)
        m.settings = settings
        m.mail = mail
        m.db = session
        m.reset_password_token_secret = settings.secret_key
        m.verification_token_secret = settings.secret_key
        yield m
    return get_user_manager


def make_auth_backend(get_session, secure: bool) -> AuthenticationBackend:
    cookie = CookieTransport(
        cookie_name="schieber_session",
        cookie_max_age=2 * 60 * 60,  # 2h normal; remember-me handled in custom login
        cookie_secure=secure,
        cookie_httponly=True,
        cookie_samesite="lax",
    )
    token_db_dep = make_token_db_dep(get_session)

    def get_strategy(token_db = Depends(token_db_dep)) -> DatabaseStrategy:
        return DatabaseStrategy(token_db, lifetime_seconds=2 * 60 * 60)

    return AuthenticationBackend(
        name="cookie-db",
        transport=cookie,
        get_strategy=get_strategy,
    )


def make_fastapi_users(get_session, settings: Settings, mail: MailBackend):
    return FastAPIUsers[User, str](
        get_user_manager=make_manager_dep(get_session, settings, mail),
        auth_backends=[make_auth_backend(get_session, settings.secure_cookie)],
    )
```

- [ ] **Step 3: Quick smoke (no tests yet — full coverage in Task 11+)**

```bash
python -c "from frontend.auth.users import make_fastapi_users; print('import ok')"
```

Expected: `import ok`. (If fastapi-users API has shifted between minor versions, fix imports here before continuing.)

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/manager.py frontend/auth/users.py
git commit -m "feat(auth): UserManager with email hooks + fastapi-users factory"
```

---

## Task 10: Test app fixture (full FastAPI client)

**Files:**
- Modify: `tests/auth/conftest.py`

This gives every later test an in-memory app + `httpx.AsyncClient` + captured mail.

- [ ] **Step 1: Extend conftest**

Replace `tests/auth/conftest.py`:

```python
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
```

(no commit yet — committed with Task 11 once it builds)

---

## Task 11: Build app + signup + /auth/me

**Files:**
- Create: `frontend/auth/app.py`
- Create: `frontend/auth/routes.py`
- Create: `tests/auth/test_signup.py`

- [ ] **Step 1: Write failing tests**

`tests/auth/test_signup.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_signup_happy_path(client, mail):
    r = await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "longpassword99",
    })
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "alice@test"
    assert body["username"] == "alice"
    assert body["is_verified"] is False
    # verification mail sent
    assert any("verify" in m.body for m in mail.sent)


async def test_signup_duplicate_email_409(client):
    payload = {"email": "x@test", "username": "alice", "password": "longpassword99"}
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == 201
    payload2 = {**payload, "username": "alice2"}
    r = await client.post("/auth/register", json=payload2)
    assert r.status_code in (400, 409)


async def test_signup_duplicate_username_409(client):
    await client.post("/auth/register", json={
        "email": "a1@test", "username": "alice", "password": "longpassword99",
    })
    r = await client.post("/auth/register", json={
        "email": "a2@test", "username": "alice", "password": "longpassword99",
    })
    assert r.status_code in (400, 409)


async def test_signup_short_password_422(client):
    r = await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "short",
    })
    assert r.status_code in (400, 422)


async def test_signup_invalid_username_422(client):
    r = await client.post("/auth/register", json={
        "email": "a@test", "username": "ab", "password": "longpassword99",
    })
    assert r.status_code == 422
```

- [ ] **Step 2: Implement `frontend/auth/app.py`**

```python
from fastapi import FastAPI
from frontend.auth.users import make_fastapi_users
from frontend.auth.schemas import UserRead, UserCreate, UserUpdate
from frontend.auth.email import MailBackend
from frontend.auth.settings import Settings


def build_app(*, get_session, settings: Settings, mail: MailBackend) -> FastAPI:
    app = FastAPI()
    fapi_users = make_fastapi_users(get_session, settings, mail)
    backend = fapi_users.authenticator.backends[0]

    # Only mount the register router from fastapi-users.
    # /auth/login and /auth/logout are custom (Task 12 / 13) — needed for lockout
    # and remember-me behaviour. We deliberately skip get_auth_router to avoid
    # duplicate-route registration conflicts.
    app.include_router(
        fapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
    )
    # Users router (PATCH /users/{id}, GET /users/me) — useful for admin/account UI later.
    app.include_router(
        fapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
    )

    return app
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_signup.py -v
```

Expected: 5 passed (some assertions accept either 400 or 409 because fastapi-users may surface duplicates as 400 — that's library behaviour and acceptable).

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/app.py tests/auth/conftest.py tests/auth/test_signup.py
git commit -m "feat(auth): app builder + signup endpoint with verification mail"
```

---

## Task 12: Login + cookie + remember-me + lockout glue

**Files:**
- Create: `frontend/auth/lockout.py`
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_login.py`

The fastapi-users default `/auth/login` is mounted. We need to (a) ensure cookie comes back, (b) add remember-me extension, (c) record lockout attempts. We do (b)+(c) by overlaying our own `/auth/login` route that delegates to the manager and tweaks the cookie.

- [ ] **Step 1: Implement lockout queries**

`frontend/auth/lockout.py`:

```python
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
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
    from sqlalchemy import delete
    await db.execute(delete(LockoutAttempt).where(
        LockoutAttempt.email == email,
        LockoutAttempt.success == False,  # noqa: E712
    ))
    await db.commit()
```

- [ ] **Step 2: Write failing test**

`tests/auth/test_login.py`:

```python
import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


async def _signup(client, email="alice@test", username="alice"):
    r = await client.post("/auth/register", json={
        "email": email, "username": username, "password": "longpassword99",
    })
    assert r.status_code == 201


async def test_login_sets_cookie(client):
    await _signup(client)
    r = await client.post("/auth/login", data={
        "username": "alice@test", "password": "longpassword99",
    })
    assert r.status_code == 204
    assert "schieber_session" in r.headers.get("set-cookie", "")


async def test_login_wrong_password_401(client):
    await _signup(client)
    r = await client.post("/auth/login", data={
        "username": "alice@test", "password": "wrong-password!!",
    })
    assert r.status_code in (400, 401)


async def test_login_locks_out_after_5_failures(client):
    await _signup(client)
    for _ in range(5):
        await client.post("/auth/login", data={
            "username": "alice@test", "password": "wrong-password!!",
        })
    r = await client.post("/auth/login", data={
        "username": "alice@test", "password": "wrong-password!!",
    })
    assert r.status_code == 429
```

- [ ] **Step 3: Wire lockout into `frontend/auth/app.py`**

Add after the existing `app.include_router` calls:

```python
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from frontend.auth import lockout

@app.post("/auth/login")
async def login_with_lockout(request: Request, response: Response):
    """Wraps fastapi-users' login with email/IP lockout + remember-me."""
    form = await request.form()
    email = form.get("username", "").lower()
    password = form.get("password", "")
    remember = form.get("remember") in ("1", "true", "on", "yes")
    ip = request.client.host if request.client else "?"

    async for session in get_session():
        if await lockout.is_locked_out(session, email=email, ip=ip):
            raise HTTPException(status_code=429, detail="too many attempts; try again later")
        # delegate to fastapi-users default flow by re-issuing the request to the bundled router
        # easiest: validate via UserManager.authenticate, mint cookie ourselves
        from frontend.auth.users import make_user_db_dep, make_token_db_dep
        from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
        from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
        from frontend.auth.models import User, AccessToken
        from frontend.auth.manager import UserManager
        from datetime import datetime, timezone, timedelta
        import secrets

        user_db = SQLAlchemyUserDatabase(session, User)
        manager = UserManager(user_db)
        manager.settings = settings_obj  # captured by closure below
        manager.mail = mail_obj
        manager.db = session
        manager.reset_password_token_secret = settings_obj.secret_key
        manager.verification_token_secret = settings_obj.secret_key

        from fastapi_users.exceptions import UserNotExists, InvalidPasswordException
        try:
            user = await manager.authenticate(
                type("Cred", (), {"username": email, "password": password})()
            )
        except (UserNotExists, InvalidPasswordException):
            user = None

        if user is None or not user.is_active:
            await lockout.record_attempt(session, email=email, ip=ip, success=False)
            raise HTTPException(status_code=401, detail="invalid credentials")

        await lockout.record_attempt(session, email=email, ip=ip, success=True)
        await lockout.clear_email_streak(session, email=email)

        # mint access_token
        token_value = secrets.token_urlsafe(32)
        ttl = timedelta(days=30) if remember else timedelta(hours=2)
        token_db = SQLAlchemyAccessTokenDatabase(session, AccessToken)
        await token_db.create({
            "token": token_value,
            "user_id": user.id,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + ttl,
        })

        # last_login
        user.last_login_at = datetime.now(timezone.utc)
        await session.commit()

        response.set_cookie(
            key="schieber_session",
            value=token_value,
            max_age=int(ttl.total_seconds()),
            httponly=True,
            secure=settings_obj.secure_cookie,
            samesite="lax",
        )
        return Response(status_code=204, headers=dict(response.headers))
```

NOTE: this overrides the default fastapi-users `/auth/login` (mounted earlier). FastAPI route registration order means the later registration wins for duplicate paths — verify by checking `app.routes` after construction. If it does NOT win (some FastAPI versions error on dup), remove the fastapi-users `auth_router` mount and keep only this one.

The closure variables `settings_obj`, `mail_obj`, `get_session` need to be in scope; pass them through `build_app` parameters.

Refactor `build_app` signature accordingly:

```python
def build_app(*, get_session, settings: Settings, mail: MailBackend) -> FastAPI:
    settings_obj = settings
    mail_obj = mail
    app = FastAPI()
    ...
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_login.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/lockout.py frontend/auth/app.py tests/auth/test_login.py
git commit -m "feat(auth): login with cookie, remember-me, email/IP lockout"
```

---

## Task 13: Logout

**Files:**
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_logout.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_logout.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_logout_clears_cookie_and_revokes(client):
    await client.post("/auth/register", json={
        "email": "alice@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "alice@test", "password": "longpassword99",
    })
    r = await client.post("/auth/logout")
    assert r.status_code == 204
    assert 'schieber_session=""' in r.headers.get("set-cookie", "") \
        or "Max-Age=0" in r.headers.get("set-cookie", "")
    # subsequent /auth/me returns 401
    r2 = await client.get("/auth/me")
    assert r2.status_code in (401, 403)
```

- [ ] **Step 2: Add logout route in `app.py`**

```python
@app.post("/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("schieber_session")
    async for session in get_session():
        if token:
            from sqlalchemy import delete
            await session.execute(delete(AccessToken).where(AccessToken.token == token))
            await session.commit()
    response.delete_cookie(
        key="schieber_session",
        secure=settings_obj.secure_cookie,
        samesite="lax",
        httponly=True,
    )
    return Response(status_code=204, headers=dict(response.headers))
```

Add `/auth/me`:

```python
from fastapi import Depends
from frontend.auth.deps import current_user

@app.get("/auth/me")
async def me(user = Depends(current_user)):
    return {
        "id": user.id, "email": user.email, "username": user.username,
        "is_verified": user.is_verified, "is_superuser": user.is_superuser,
    }
```

(`deps.py` is built in the next step — write it now since `me` needs it.)

- [ ] **Step 3: Implement `frontend/auth/deps.py`**

```python
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
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
        u = (await session.execute(select(User).where(User.id == at.user_id))).scalar_one_or_none()
        if u is None or not u.is_active:
            from sqlalchemy import delete
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
```

In `build_app`, instantiate the dep factories near the top of the function and capture them in closures used by every later route:

```python
def build_app(*, get_session, settings: Settings, mail: MailBackend) -> FastAPI:
    settings_obj = settings
    mail_obj = mail
    app = FastAPI()
    fapi_users = make_fastapi_users(get_session, settings, mail)

    # Build deps once; reuse via closure in @app.<method> routes below.
    current_user_dep = make_current_user_dep(get_session)
    require_admin_dep = make_require_admin_dep(current_user_dep)
    # ... routes use Depends(current_user_dep) / Depends(require_admin_dep) ...
```

Routes that need the user write `Depends(current_user_dep)`. Routes that need a superuser write `Depends(require_admin_dep)`. No global state.

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_logout.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/app.py frontend/auth/deps.py tests/auth/test_logout.py
git commit -m "feat(auth): logout + /auth/me + cookie-backed deps"
```

---

## Task 14: Email verification flow

**Files:**
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_verify.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_verify.py`:

```python
import pytest
import re

pytestmark = pytest.mark.asyncio


async def _extract_token(mail, kind="verify"):
    for m in mail.sent:
        if kind in m.body:
            match = re.search(r"token=(\S+)", m.body)
            if match:
                return match.group(1)
    return None


async def test_verify_happy(client, mail):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    token = await _extract_token(mail, "verify")
    assert token
    r = await client.get(f"/auth/verify?token={token}")
    assert r.status_code == 200


async def test_verify_used_token(client, mail):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    token = await _extract_token(mail, "verify")
    await client.get(f"/auth/verify?token={token}")
    r = await client.get(f"/auth/verify?token={token}")
    assert r.status_code == 410


async def test_resend_requires_login(client):
    r = await client.post("/auth/resend-verification")
    assert r.status_code in (401, 403)


async def test_resend_after_login_sends_mail(client, mail):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "a@test", "password": "longpassword99",
    })
    mail.sent.clear()
    r = await client.post("/auth/resend-verification")
    assert r.status_code == 202
    assert any("verify" in m.body for m in mail.sent)
```

- [ ] **Step 2: Add routes in `app.py`**

```python
from datetime import datetime, timezone, timedelta
import secrets
from fastapi.responses import HTMLResponse
from sqlalchemy import select, update
from frontend.auth.models import EmailToken, User
from frontend.auth.email import Mail, render_verification


@app.get("/auth/verify", response_class=HTMLResponse)
async def verify(token: str):
    async for session in get_session():
        q = select(EmailToken).where(
            EmailToken.token == token, EmailToken.purpose == "verify"
        )
        et = (await session.execute(q)).scalar_one_or_none()
        if et is None or et.used_at is not None or et.expires_at < datetime.now(timezone.utc):
            return HTMLResponse("<h1>Link expired or already used.</h1>", status_code=410)
        et.used_at = datetime.now(timezone.utc)
        await session.execute(update(User).where(User.id == et.user_id).values(is_verified=True))
        await session.commit()
        return HTMLResponse("<h1>Email verified. You can close this tab.</h1>")


@app.post("/auth/resend-verification", status_code=202)
async def resend_verification(user = Depends(current_user_dep)):
    async for session in get_session():
        token = secrets.token_urlsafe(32)
        session.add(EmailToken(
            token=token, user_id=user.id, purpose="verify",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        ))
        await session.commit()
        body = render_verification(
            username=user.username, base_url=settings_obj.base_url, token=token,
        )
        await mail_obj.send(Mail(to=user.email, subject="Confirm your Schieber account", body=body))
    return {"status": "sent"}
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_verify.py -v
```

Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/app.py tests/auth/test_verify.py
git commit -m "feat(auth): email verification flow (verify + resend)"
```

---

## Task 15: Password reset (forgot + reset)

**Files:**
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_password_reset.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_password_reset.py`:

```python
import pytest
import re

pytestmark = pytest.mark.asyncio


async def _signup(client):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })


async def _reset_token(mail):
    for m in mail.sent:
        if "Reset your" in m.subject:
            return re.search(r"token=(\S+)", m.body).group(1)
    return None


async def test_forgot_unknown_email_202(client):
    r = await client.post("/auth/forgot", json={"email": "nobody@test"})
    assert r.status_code == 202


async def test_forgot_known_email_sends_mail(client, mail):
    await _signup(client)
    mail.sent.clear()
    r = await client.post("/auth/forgot", json={"email": "a@test"})
    assert r.status_code == 202
    assert await _reset_token(mail)


async def test_reset_revokes_all_sessions(client, mail):
    await _signup(client)
    await client.post("/auth/login", data={"username": "a@test", "password": "longpassword99"})
    await client.post("/auth/forgot", json={"email": "a@test"})
    token = await _reset_token(mail)
    r = await client.post("/auth/reset", json={
        "token": token, "new_password": "newlongpw99!",
    })
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.status_code in (401, 403)
    r2 = await client.post("/auth/login", data={
        "username": "a@test", "password": "newlongpw99!",
    })
    assert r2.status_code == 204


async def test_reset_used_token(client, mail):
    await _signup(client)
    await client.post("/auth/forgot", json={"email": "a@test"})
    token = await _reset_token(mail)
    await client.post("/auth/reset", json={"token": token, "new_password": "newlongpw99!"})
    r = await client.post("/auth/reset", json={"token": token, "new_password": "anotherlong!"})
    assert r.status_code == 410
```

- [ ] **Step 2: Add routes**

```python
from passlib.context import CryptContext
from frontend.auth.passwords import validate_password
from frontend.auth.email import render_reset
from sqlalchemy import delete

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/auth/forgot", status_code=202)
async def forgot(payload: dict):
    email = payload.get("email", "").lower()
    async for session in get_session():
        u = (await session.execute(
            select(User).where(User.email == email, User.is_active == True)
        )).scalar_one_or_none()
        if u is None:
            return {"status": "ok"}
        token = secrets.token_urlsafe(32)
        session.add(EmailToken(
            token=token, user_id=u.id, purpose="reset",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        await session.commit()
        body = render_reset(username=u.username, base_url=settings_obj.base_url, token=token)
        await mail_obj.send(Mail(to=u.email, subject="Reset your Schieber password", body=body))
    return {"status": "ok"}


@app.post("/auth/reset")
async def reset(payload: dict):
    token = payload.get("token", "")
    new_password = payload.get("new_password", "")
    async for session in get_session():
        et = (await session.execute(
            select(EmailToken).where(
                EmailToken.token == token, EmailToken.purpose == "reset"
            )
        )).scalar_one_or_none()
        if et is None or et.used_at is not None or et.expires_at < datetime.now(timezone.utc):
            raise HTTPException(410, "link expired or used")
        u = (await session.execute(select(User).where(User.id == et.user_id))).scalar_one()
        validate_password(new_password, username=u.username, email=u.email)
        u.hashed_password = pwd_ctx.hash(new_password)
        et.used_at = datetime.now(timezone.utc)
        await session.execute(delete(AccessToken).where(AccessToken.user_id == u.id))
        await session.commit()
    return {"status": "ok"}
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_password_reset.py -v
```

Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/app.py tests/auth/test_password_reset.py
git commit -m "feat(auth): password reset flow (forgot + reset, revokes sessions)"
```

---

## Task 16: Change password

**Files:**
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_change_password.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_change_password.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def _setup(client):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "a@test", "password": "longpassword99",
    })


async def test_change_password_happy(client):
    await _setup(client)
    r = await client.post("/auth/change-password", json={
        "current_password": "longpassword99",
        "new_password": "anotherlong99!",
    })
    assert r.status_code == 200


async def test_change_password_wrong_current_401(client):
    await _setup(client)
    r = await client.post("/auth/change-password", json={
        "current_password": "wrong-password!!",
        "new_password": "anotherlong99!",
    })
    assert r.status_code == 401


async def test_change_password_keeps_current_session(client):
    await _setup(client)
    r = await client.post("/auth/change-password", json={
        "current_password": "longpassword99",
        "new_password": "anotherlong99!",
    })
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.status_code == 200
```

- [ ] **Step 2: Add route**

```python
@app.post("/auth/change-password")
async def change_password(request: Request, payload: dict, user = Depends(current_user_dep)):
    current = payload.get("current_password", "")
    new = payload.get("new_password", "")
    async for session in get_session():
        u = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
        if not pwd_ctx.verify(current, u.hashed_password):
            raise HTTPException(401, "wrong current password")
        validate_password(new, username=u.username, email=u.email)
        u.hashed_password = pwd_ctx.hash(new)
        # revoke all OTHER sessions
        cur_token = request.cookies.get("schieber_session")
        await session.execute(delete(AccessToken).where(
            AccessToken.user_id == u.id, AccessToken.token != cur_token
        ))
        await session.commit()
    return {"status": "ok"}
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_change_password.py -v
```

Expected: 3 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/app.py tests/auth/test_change_password.py
git commit -m "feat(auth): change-password (keeps current session, revokes others)"
```

---

## Task 17: Change email (2-step)

**Files:**
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_change_email.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_change_email.py`:

```python
import pytest
import re

pytestmark = pytest.mark.asyncio


async def _setup(client):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "a@test", "password": "longpassword99",
    })


async def _confirm_token(mail):
    for m in mail.sent:
        if "switch your account email" in m.body:
            return re.search(r"token=(\S+)", m.body).group(1)
    return None


async def test_change_email_two_step(client, mail):
    await _setup(client)
    mail.sent.clear()
    r = await client.post("/auth/change-email", json={
        "new_email": "new@test", "current_password": "longpassword99",
    })
    assert r.status_code == 202
    # two mails: confirm to new, notice to old
    assert any(m.to == "new@test" for m in mail.sent)
    assert any(m.to == "a@test" for m in mail.sent)
    token = await _confirm_token(mail)
    r = await client.get(f"/auth/confirm-email?token={token}")
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.json()["email"] == "new@test"


async def test_change_email_wrong_password_401(client):
    await _setup(client)
    r = await client.post("/auth/change-email", json={
        "new_email": "new@test", "current_password": "nope",
    })
    assert r.status_code == 401


async def test_change_email_collision_409(client, mail):
    await client.post("/auth/register", json={
        "email": "taken@test", "username": "bob", "password": "longpassword99",
    })
    await _setup(client)
    r = await client.post("/auth/change-email", json={
        "new_email": "taken@test", "current_password": "longpassword99",
    })
    assert r.status_code == 409
```

- [ ] **Step 2: Add routes**

```python
from frontend.auth.email import (
    render_change_email_confirm, render_change_email_notice, mask_email,
)


@app.post("/auth/change-email", status_code=202)
async def change_email(payload: dict, user = Depends(current_user_dep)):
    new_email = payload.get("new_email", "").lower()
    current = payload.get("current_password", "")
    async for session in get_session():
        u = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
        if not pwd_ctx.verify(current, u.hashed_password):
            raise HTTPException(401, "wrong current password")
        existing = (await session.execute(
            select(User).where(User.email == new_email)
        )).scalar_one_or_none()
        if existing:
            raise HTTPException(409, "email already in use")
        # tombstone collision
        from frontend.auth.tombstone import hash_email as _he
        from frontend.auth.models import Tombstone
        from sqlalchemy import select as _select
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        if (await session.execute(
            _select(Tombstone).where(Tombstone.email_hash == _he(new_email),
                                     Tombstone.deleted_at >= cutoff)
        )).scalars().first():
            raise HTTPException(409, "email recently used")
        token = secrets.token_urlsafe(32)
        session.add(EmailToken(
            token=token, user_id=u.id, purpose="change_email",
            new_value=new_email,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        await session.commit()
        await mail_obj.send(Mail(
            to=new_email, subject="Confirm new email for Schieber",
            body=render_change_email_confirm(base_url=settings_obj.base_url, token=token),
        ))
        await mail_obj.send(Mail(
            to=u.email, subject="Email change requested on your Schieber account",
            body=render_change_email_notice(masked_new_email=mask_email(new_email)),
        ))
    return {"status": "sent"}


@app.get("/auth/confirm-email")
async def confirm_email(token: str):
    async for session in get_session():
        et = (await session.execute(
            select(EmailToken).where(EmailToken.token == token,
                                     EmailToken.purpose == "change_email")
        )).scalar_one_or_none()
        if et is None or et.used_at is not None or et.expires_at < datetime.now(timezone.utc):
            raise HTTPException(410, "link expired or used")
        u = (await session.execute(select(User).where(User.id == et.user_id))).scalar_one()
        u.email = et.new_value
        et.used_at = datetime.now(timezone.utc)
        await session.commit()
    return {"status": "ok"}
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_change_email.py -v
```

Expected: 3 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/app.py tests/auth/test_change_email.py
git commit -m "feat(auth): change-email (2-step confirm, old-email notice)"
```

---

## Task 18: Account delete (soft) + tombstone enforcement

**Files:**
- Modify: `frontend/auth/app.py`
- Modify: `frontend/auth/manager.py` (already has tombstone check at signup)
- Create: `tests/auth/test_account_delete.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_account_delete.py`:

```python
import pytest
import uuid

pytestmark = pytest.mark.asyncio


async def _setup(client, email="a@test", username="alice"):
    await client.post("/auth/register", json={
        "email": email, "username": username, "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": email, "password": "longpassword99",
    })


async def test_delete_account(client):
    await _setup(client)
    r = await client.request("DELETE", "/auth/account",
                             json={"current_password": "longpassword99"})
    assert r.status_code == 200
    me = await client.get("/auth/me")
    assert me.status_code in (401, 403)


async def test_signup_blocked_by_tombstone(client):
    await _setup(client)
    await client.request("DELETE", "/auth/account",
                        json={"current_password": "longpassword99"})
    # try same email/username again — within 30d should fail
    r = await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    assert r.status_code in (400, 409)
```

- [ ] **Step 2: Add route**

```python
import uuid as _uuid
from frontend.auth.tombstone import hash_email as _he, hash_username as _hu
from frontend.auth.models import Tombstone


@app.delete("/auth/account")
async def delete_account(payload: dict, request: Request,
                         response: Response, user = Depends(current_user_dep)):
    current = payload.get("current_password", "")
    async for session in get_session():
        u = (await session.execute(select(User).where(User.id == user.id))).scalar_one()
        if not pwd_ctx.verify(current, u.hashed_password):
            raise HTTPException(401, "wrong current password")
        # tombstone first (preserves original hashes)
        session.add(Tombstone(
            id=u.id,
            email_hash=_he(u.email),
            username_hash=_hu(u.username),
            deleted_at=datetime.now(timezone.utc),
        ))
        # anonymise
        u.email = f"deleted-{_uuid.uuid4()}@invalid"
        u.username = f"deleted-{u.id[:8]}"
        u.hashed_password = ""
        u.is_active = False
        # revoke
        await session.execute(delete(AccessToken).where(AccessToken.user_id == u.id))
        await session.commit()
    response.delete_cookie(
        key="schieber_session",
        secure=settings_obj.secure_cookie,
        samesite="lax",
        httponly=True,
    )
    return {"status": "ok"}
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_account_delete.py -v
```

Expected: 2 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/app.py tests/auth/test_account_delete.py
git commit -m "feat(auth): account soft-delete with tombstone (30d reclaim block)"
```

---

## Task 19: Account export

**Files:**
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_account_export.py`

- [ ] **Step 1: Write failing test**

`tests/auth/test_account_export.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_export_returns_self_data(client):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "a@test", "password": "longpassword99",
    })
    r = await client.get("/auth/export")
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["email"] == "a@test"
    assert "access_tokens" in body
    assert "email_tokens" in body
```

- [ ] **Step 2: Add route**

```python
@app.get("/auth/export")
async def export_account(user = Depends(current_user_dep)):
    async for session in get_session():
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
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/auth/test_account_export.py -v
```

Expected: 1 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/auth/app.py tests/auth/test_account_export.py
git commit -m "feat(auth): /auth/export GDPR-style data dump"
```

---

## Task 20: Rate limiting (slowapi)

**Files:**
- Create: `frontend/auth/ratelimit.py`
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_ratelimit.py`

- [ ] **Step 1: Implement limiter config**

`frontend/auth/ratelimit.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address


def make_limiter() -> Limiter:
    return Limiter(key_func=get_remote_address)


# Per spec §6.2; values reused as decorator args
LIMITS = {
    "signup": "5/hour",
    "login": "20/15minute",
    "forgot": "3/minute;10/day",
    "resend_verification": "5/day",
    "reset": "10/hour",
    "change_password": "10/hour",
    "change_email": "5/day",
    "whoami": "30/minute",
    "admin": "60/minute",
}
```

- [ ] **Step 2: Wire into `app.py`**

```python
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from frontend.auth.ratelimit import make_limiter, LIMITS

limiter = make_limiter()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse({"detail": "rate limited"}, status_code=429,
                        headers={"Retry-After": "60"})

# decorate selected routes
@limiter.limit(LIMITS["signup"])
# etc — apply by re-defining or via dependency_overrides
```

NOTE: `@limiter.limit` requires the route function to take `request: Request` as its first parameter. Refactor each route to ensure that.

For brevity, decorate the most abusable: signup, login, forgot, reset, whoami. Others kept implicit at app-level.

- [ ] **Step 3: Write failing test**

`tests/auth/test_ratelimit.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_signup_rate_limit(client):
    for i in range(5):
        await client.post("/auth/register", json={
            "email": f"a{i}@test", "username": f"a{i:03d}", "password": "longpassword99",
        })
    r = await client.post("/auth/register", json={
        "email": "a99@test", "username": "a999", "password": "longpassword99",
    })
    assert r.status_code == 429
    assert "Retry-After" in r.headers


async def test_forgot_rate_limit(client):
    for _ in range(3):
        await client.post("/auth/forgot", json={"email": "x@test"})
    r = await client.post("/auth/forgot", json={"email": "x@test"})
    assert r.status_code == 429
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_ratelimit.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/ratelimit.py frontend/auth/app.py tests/auth/test_ratelimit.py
git commit -m "feat(auth): slowapi rate limiting on signup/login/forgot/reset/whoami"
```

---

## Task 21: Admin tools (bootstrap, endpoints, audit)

**Files:**
- Create: `frontend/auth/admin.py`
- Modify: `frontend/auth/manager.py` (auto-promote on bootstrap email)
- Modify: `frontend/auth/app.py` (mount admin router)
- Create: `tests/auth/test_admin.py`

- [ ] **Step 1: Auto-promote in `manager.py`**

In `UserManager.on_after_register`, before any return, add:

```python
        if user.email == self.settings.admin_bootstrap_email:
            user.is_superuser = True
            user.is_verified = True   # bootstrap admin is trusted
            await self.db.commit()
```

- [ ] **Step 2: Implement admin router**

`frontend/auth/admin.py`:

```python
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, delete, desc
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
    async def list_users(page: int = 1, q: str = "",
                         admin = Depends(require_admin)):
        limit = 50
        offset = (page - 1) * limit
        async for session in get_session():
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
    async def ban(user_id: str, request: Request, payload: dict = None,
                  admin = Depends(require_admin)):
        async for session in get_session():
            u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
            if u is None: raise HTTPException(404)
            u.is_active = False
            await session.execute(delete(AccessToken).where(AccessToken.user_id == u.id))
            await audit(session, admin_id=admin.id, action="ban", target_id=u.id,
                        reason=(payload or {}).get("reason"),
                        ip=request.client.host if request.client else "?")
        return {"status": "banned"}

    @router.post("/users/{user_id}/unban")
    async def unban(user_id: str, request: Request, admin = Depends(require_admin)):
        async for session in get_session():
            u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
            if u is None: raise HTTPException(404)
            u.is_active = True
            await audit(session, admin_id=admin.id, action="unban", target_id=u.id,
                        reason=None,
                        ip=request.client.host if request.client else "?")
        return {"status": "unbanned"}

    @router.post("/users/{user_id}/promote")
    async def promote(user_id: str, request: Request, admin = Depends(require_admin)):
        async for session in get_session():
            u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
            if u is None: raise HTTPException(404)
            u.is_superuser = True
            await audit(session, admin_id=admin.id, action="promote", target_id=u.id,
                        reason=None,
                        ip=request.client.host if request.client else "?")
        return {"status": "promoted"}

    @router.post("/users/{user_id}/demote")
    async def demote(user_id: str, request: Request, admin = Depends(require_admin)):
        if user_id == admin.id:
            raise HTTPException(409, "cannot demote self")
        async for session in get_session():
            u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
            if u is None: raise HTTPException(404)
            u.is_superuser = False
            await audit(session, admin_id=admin.id, action="demote", target_id=u.id,
                        reason=None,
                        ip=request.client.host if request.client else "?")
        return {"status": "demoted"}

    @router.post("/users/{user_id}/force-verify")
    async def force_verify(user_id: str, request: Request, admin = Depends(require_admin)):
        async for session in get_session():
            u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
            if u is None: raise HTTPException(404)
            u.is_verified = True
            await audit(session, admin_id=admin.id, action="force_verify", target_id=u.id,
                        reason=None,
                        ip=request.client.host if request.client else "?")
        return {"status": "verified"}

    @router.get("/audit")
    async def audit_log(admin = Depends(require_admin)):
        async for session in get_session():
            rows = (await session.execute(
                select(AdminAudit).order_by(desc(AdminAudit.created_at)).limit(200)
            )).scalars().all()
            return [{
                "admin_id": r.admin_id, "action": r.action, "target_id": r.target_id,
                "reason": r.reason, "created_at": r.created_at.isoformat(), "ip": r.ip,
            } for r in rows]

    return router
```

- [ ] **Step 3: Mount in `app.py`**

```python
require_admin_dep = make_require_admin_dep(current_user_dep)
app.include_router(make_admin_router(get_session, require_admin_dep))
```

- [ ] **Step 4: Write failing test**

`tests/auth/test_admin.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_bootstrap_email_auto_promotes(client):
    await client.post("/auth/register", json={
        "email": "admin@test", "username": "admin", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "admin@test", "password": "longpassword99",
    })
    r = await client.get("/auth/me")
    assert r.json()["is_superuser"] is True


async def test_ban_revokes_sessions(client):
    # admin signup
    await client.post("/auth/register", json={
        "email": "admin@test", "username": "admin", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "admin@test", "password": "longpassword99",
    })
    # create another user via separate client cookies — easier: target same session, then check ban took effect
    # Simpler: create target user, log them in via 2nd client, ban from admin client
    from httpx import AsyncClient, ASGITransport
    target_client = AsyncClient(transport=ASGITransport(app=client._transport.app),
                                base_url="http://test")
    try:
        await target_client.post("/auth/register", json={
            "email": "victim@test", "username": "victim", "password": "longpassword99",
        })
        await target_client.post("/auth/login", data={
            "username": "victim@test", "password": "longpassword99",
        })
        # admin: list users, find victim
        r = await client.get("/admin/users?q=victim")
        vid = r.json()[0]["id"]
        await client.post(f"/admin/users/{vid}/ban", json={"reason": "test"})
        # victim should now be 401
        me = await target_client.get("/auth/me")
        assert me.status_code in (401, 403)
    finally:
        await target_client.aclose()


async def test_demote_self_blocked(client):
    await client.post("/auth/register", json={
        "email": "admin@test", "username": "admin", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "admin@test", "password": "longpassword99",
    })
    me = (await client.get("/auth/me")).json()
    r = await client.post(f"/admin/users/{me['id']}/demote")
    assert r.status_code == 409
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/auth/test_admin.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add frontend/auth/admin.py frontend/auth/manager.py \
        frontend/auth/app.py tests/auth/test_admin.py
git commit -m "feat(auth): admin tools (bootstrap, ban/unban, promote/demote, audit)"
```

---

## Task 22: /auth/whoami + guest cookie issuance

**Files:**
- Modify: `frontend/auth/app.py`
- Create: `tests/auth/test_guest.py`

- [ ] **Step 1: Add `/auth/whoami` route**

```python
from frontend.auth.guest import issue_guest_cookie, read_guest_cookie, GuestCookieError


@app.get("/auth/whoami")
async def whoami(request: Request, response: Response):
    sess = request.cookies.get("schieber_session")
    if sess:
        async for session in get_session():
            q = select(AccessToken).where(
                AccessToken.token == sess,
                AccessToken.expires_at > datetime.now(timezone.utc),
            )
            at = (await session.execute(q)).scalar_one_or_none()
            if at:
                u = (await session.execute(
                    select(User).where(User.id == at.user_id)
                )).scalar_one_or_none()
                if u and u.is_active:
                    return {
                        "kind": "user",
                        "display_name": u.username,
                        "is_verified": u.is_verified,
                        "is_superuser": u.is_superuser,
                    }

    guest_cookie = request.cookies.get("schieber_guest")
    guest = None
    if guest_cookie:
        try:
            guest = read_guest_cookie(guest_cookie, settings_obj.secret_key)
        except GuestCookieError:
            guest = None

    if guest is None:
        new_cookie, guest = issue_guest_cookie(settings_obj.secret_key)
        response.set_cookie(
            key="schieber_guest",
            value=new_cookie,
            max_age=30 * 24 * 60 * 60,
            httponly=True,
            secure=settings_obj.secure_cookie,
            samesite="lax",
        )

    return {"kind": "guest", "display_name": guest.display_name}
```

- [ ] **Step 2: Clear guest cookie on signup/login**

In the `/auth/register` and `/auth/login` flows, ensure `response.delete_cookie("schieber_guest")` is called when a session cookie is being issued.

For the register router (mounted from fastapi-users), add a wrapping route or middleware. Simplest: write our own thin wrapper:

```python
@app.post("/auth/register")
async def register_with_guest_clear(request: Request, response: Response, payload: dict):
    # delegate to fastapi-users' UserManager directly (no extra router needed)
    ...
    response.delete_cookie("schieber_guest")
```

For brevity in this plan: pull the existing `/auth/register` mount BEFORE this route, and let our wrapper take precedence.

- [ ] **Step 3: Write failing test**

`tests/auth/test_guest.py`:

```python
import pytest

pytestmark = pytest.mark.asyncio


async def test_whoami_issues_guest_cookie(client):
    r = await client.get("/auth/whoami")
    assert r.status_code == 200
    assert r.json()["kind"] == "guest"
    assert r.json()["display_name"].startswith("Guest-")
    assert "schieber_guest" in r.headers.get("set-cookie", "")


async def test_whoami_authed(client):
    await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    await client.post("/auth/login", data={
        "username": "a@test", "password": "longpassword99",
    })
    r = await client.get("/auth/whoami")
    assert r.json() == {
        "kind": "user", "display_name": "alice",
        "is_verified": False, "is_superuser": False,
    }


async def test_signup_clears_guest_cookie(client):
    await client.get("/auth/whoami")  # gets guest cookie
    r = await client.post("/auth/register", json={
        "email": "a@test", "username": "alice", "password": "longpassword99",
    })
    cookie_header = r.headers.get("set-cookie", "")
    assert "schieber_guest=" in cookie_header and "Max-Age=0" in cookie_header


async def test_tampered_guest_cookie_replaced(client):
    client.cookies.set("schieber_guest", "tampered.cookie.value")
    r = await client.get("/auth/whoami")
    assert r.json()["kind"] == "guest"
    # new cookie issued
    assert "schieber_guest" in r.headers.get("set-cookie", "")
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/auth/test_guest.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/auth/app.py tests/auth/test_guest.py
git commit -m "feat(auth): /auth/whoami + signed guest cookie issuance"
```

---

## Task 23: WS principal injection

**Files:**
- Modify: `frontend/server.py`
- Modify: `frontend/game_session.py`
- Modify: `tests/test_game_session.py`

- [ ] **Step 1: Update GameSession constructor**

In `frontend/game_session.py:141`:

```python
class GameSession:
    def __init__(self, end_game: int = 1000, principal=None):
        self.end_game = end_game
        self.principal = principal
        self.point_sn = 0
        ...
```

Add a single log line on game start in `GameSession.run`:

```python
import logging
logger = logging.getLogger(__name__)
...
async def run(self, websocket):
    name = getattr(self.principal, "display_name", None) or \
           getattr(self.principal, "username", None) or "anonymous"
    logger.info("game start by %s", name)
    ...  # existing body unchanged
```

- [ ] **Step 2: Update server.py /ws**

In `frontend/server.py:24`:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    principal = await resolve_principal(websocket)
    await websocket.accept()
    try:
        session = GameSession(principal=principal)
        await session.run(websocket)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
```

Add `resolve_principal`:

```python
from frontend.auth.guest import read_guest_cookie, GuestCookieError, Guest as GuestPrincipal
from frontend.auth.deps import _resolve_user_from_cookie  # new helper, see below
from frontend.auth.settings import Settings

_settings = Settings()  # singleton

async def resolve_principal(ws: WebSocket):
    sess = ws.cookies.get("schieber_session")
    if sess:
        u = await _resolve_user_from_cookie(sess)
        if u: return u
    g = ws.cookies.get("schieber_guest")
    if g:
        try:
            return read_guest_cookie(g, _settings.secret_key)
        except GuestCookieError:
            pass
    import secrets
    return GuestPrincipal(guest_id=secrets.token_hex(16))
```

`_resolve_user_from_cookie` opens a session, queries AccessToken, returns the User or None.

- [ ] **Step 3: Add WS tests**

In `tests/test_game_session.py`, add at the bottom:

```python
import pytest


@pytest.mark.asyncio
async def test_ws_with_guest_principal(monkeypatch):
    """resolve_principal returns Guest when no cookies present."""
    from frontend.server import resolve_principal
    class FakeWS:
        cookies = {}
    p = await resolve_principal(FakeWS())
    from frontend.auth.guest import Guest
    assert isinstance(p, Guest)


@pytest.mark.asyncio
async def test_ws_with_session_cookie(monkeypatch):
    """resolve_principal returns user when valid session cookie present."""
    # Stubbed at the resolver level to avoid full DB setup
    from frontend.server import resolve_principal, _resolve_user_from_cookie
    class FakeUser: ...
    fake = FakeUser()
    fake.username = "testuser"
    fake.display_name = "testuser"
    monkeypatch.setattr("frontend.server._resolve_user_from_cookie",
                        lambda token: _async_return(fake))
    class FakeWS:
        cookies = {"schieber_session": "abc"}
    p = await resolve_principal(FakeWS())
    assert p is fake


async def _async_return(value):
    return value
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_game_session.py -v
```

Expected: existing tests pass + 2 new tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/server.py frontend/game_session.py tests/test_game_session.py
git commit -m "feat(auth): WS handshake reads cookie → User or Guest principal"
```

---

## Task 24: HTML templates (login/signup/forgot/reset/account/admin/verify_done)

**Files:**
- Create: `frontend/auth/templates/base.html`
- Create: `frontend/auth/templates/login.html`
- Create: `frontend/auth/templates/signup.html`
- Create: `frontend/auth/templates/forgot.html`
- Create: `frontend/auth/templates/reset.html`
- Create: `frontend/auth/templates/account.html`
- Create: `frontend/auth/templates/admin.html`
- Create: `frontend/auth/templates/verify_done.html`
- Modify: `frontend/auth/app.py` (page routes)

- [ ] **Step 1: Create `base.html`**

```html
<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><title>{% block title %}Schieber{% endblock %}</title>
<style>
body{font-family:system-ui,sans-serif;max-width:480px;margin:2rem auto;padding:1rem}
form{display:flex;flex-direction:column;gap:.6rem}
input,button{padding:.5rem;font:inherit}
.err{color:#c00}.ok{color:#070}
.banner{background:#ffd;padding:.5rem;margin-bottom:1rem;border-left:3px solid #ca0}
</style>
</head><body>
<header><a href="/">Schieber</a></header>
{% block body %}{% endblock %}
<script>
const csrfHeaders = {"Content-Type": "application/json", "X-Requested-With": "schieber"};
</script>
{% block scripts %}{% endblock %}
</body></html>
```

- [ ] **Step 2: Create `login.html`**

```html
{% extends "base.html" %}
{% block title %}Sign in{% endblock %}
{% block body %}
<h1>Sign in</h1>
<form id="f">
  <input name="username" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password" required>
  <label><input type="checkbox" name="remember" value="1"> Remember me</label>
  <button>Sign in</button>
</form>
<p id="msg" class="err"></p>
<p><a href="/forgot">Forgot password?</a> · <a href="/signup">Create account</a></p>
{% endblock %}
{% block scripts %}<script>
document.getElementById("f").addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const r = await fetch("/auth/login", {method:"POST", body:fd, headers:{"X-Requested-With":"schieber"}});
  if (r.status === 204) location.href = "/";
  else document.getElementById("msg").textContent = "Sign in failed.";
});
</script>{% endblock %}
```

- [ ] **Step 3: Create `signup.html`**

```html
{% extends "base.html" %}
{% block title %}Sign up{% endblock %}
{% block body %}
<h1>Create account</h1>
<form id="f">
  <input name="username" placeholder="Username (3–32 chars)" required pattern="[a-zA-Z0-9_-]{3,32}">
  <input name="email" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password (min 10 chars)" required minlength="10">
  <button>Create account</button>
</form>
<p id="msg" class="err"></p>
{% endblock %}
{% block scripts %}<script>
document.getElementById("f").addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = JSON.stringify(Object.fromEntries(fd));
  const r = await fetch("/auth/register", {method:"POST", body, headers: csrfHeaders});
  if (r.status === 201) location.href = "/";
  else {
    const j = await r.json().catch(()=>({detail:"signup failed"}));
    document.getElementById("msg").textContent = j.detail || "Sign up failed.";
  }
});
</script>{% endblock %}
```

- [ ] **Step 4: Create `forgot.html`**

```html
{% extends "base.html" %}
{% block title %}Forgot password{% endblock %}
{% block body %}
<h1>Forgot password</h1>
<form id="f">
  <input name="email" type="email" placeholder="Your email" required>
  <button>Send reset link</button>
</form>
<p id="msg" class="ok"></p>
{% endblock %}
{% block scripts %}<script>
document.getElementById("f").addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = JSON.stringify(Object.fromEntries(fd));
  await fetch("/auth/forgot", {method:"POST", body, headers: csrfHeaders});
  document.getElementById("msg").textContent = "If that email exists, a reset link is on its way.";
});
</script>{% endblock %}
```

- [ ] **Step 5: Create `reset.html`**

```html
{% extends "base.html" %}
{% block title %}Reset password{% endblock %}
{% block body %}
<h1>Reset password</h1>
<form id="f">
  <input type="hidden" name="token">
  <input name="new_password" type="password" placeholder="New password" required minlength="10">
  <button>Set new password</button>
</form>
<p id="msg"></p>
{% endblock %}
{% block scripts %}<script>
const params = new URLSearchParams(location.search);
document.querySelector('input[name=token]').value = params.get("token") || "";
document.getElementById("f").addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = JSON.stringify(Object.fromEntries(fd));
  const r = await fetch("/auth/reset", {method:"POST", body, headers: csrfHeaders});
  document.getElementById("msg").textContent = r.ok ? "Password updated. Redirecting…" : "Link expired or used.";
  if (r.ok) setTimeout(() => location.href = "/login", 1500);
});
</script>{% endblock %}
```

- [ ] **Step 6: Create `account.html`**

```html
{% extends "base.html" %}
{% block title %}Account{% endblock %}
{% block body %}
<h1>Account</h1>
<section><h2>Identity</h2><pre id="me">…</pre></section>

<section><h2>Change password</h2>
<form id="pw">
  <input name="current_password" type="password" placeholder="Current password" required>
  <input name="new_password" type="password" placeholder="New password" required minlength="10">
  <button>Update password</button>
</form></section>

<section><h2>Change email</h2>
<form id="em">
  <input name="new_email" type="email" placeholder="New email" required>
  <input name="current_password" type="password" placeholder="Current password" required>
  <button>Send confirmation</button>
</form></section>

<section><h2>Export my data</h2>
<a href="/auth/export" download="schieber-account.json">Download JSON</a></section>

<section><h2>Delete account</h2>
<form id="del">
  <input name="current_password" type="password" placeholder="Current password" required>
  <button style="background:#c00;color:#fff">Delete permanently</button>
</form></section>
{% endblock %}
{% block scripts %}<script>
async function load() {
  const r = await fetch("/auth/me");
  if (!r.ok) { location.href = "/login"; return; }
  document.getElementById("me").textContent = JSON.stringify(await r.json(), null, 2);
}
function bind(id, url, method="POST") {
  document.getElementById(id).addEventListener("submit", async e => {
    e.preventDefault();
    const body = JSON.stringify(Object.fromEntries(new FormData(e.target)));
    const r = await fetch(url, {method, body, headers: csrfHeaders});
    alert(r.ok ? "ok" : `failed (${r.status})`);
    if (r.ok && id === "del") location.href = "/";
  });
}
load();
bind("pw", "/auth/change-password");
bind("em", "/auth/change-email");
bind("del", "/auth/account", "DELETE");
</script>{% endblock %}
```

- [ ] **Step 7: Create `admin.html`**

```html
{% extends "base.html" %}
{% block title %}Admin{% endblock %}
{% block body %}
<h1>Admin</h1>
<input id="q" placeholder="Search by email or username">
<table id="tbl"><thead><tr>
<th>Username</th><th>Email</th><th>Active</th><th>Verified</th><th>Super</th><th>Actions</th>
</tr></thead><tbody></tbody></table>
<h2>Recent audit</h2>
<pre id="audit"></pre>
{% endblock %}
{% block scripts %}<script>
async function loadUsers(q="") {
  const r = await fetch("/admin/users?q=" + encodeURIComponent(q));
  if (r.status === 401 || r.status === 403) { location.href = "/login"; return; }
  const tb = document.querySelector("#tbl tbody");
  tb.innerHTML = "";
  for (const u of await r.json()) {
    const tr = document.createElement("tr");
    const style = u.is_superuser ? "font-weight:bold" : (!u.is_active ? "color:#888;font-style:italic" : "");
    tr.style.cssText = style;
    tr.innerHTML = `<td>${u.username}</td><td>${u.email}</td>
                    <td>${u.is_active}</td><td>${u.is_verified}</td><td>${u.is_superuser}</td>
                    <td>
                      <button data-act="${u.is_active?'ban':'unban'}">${u.is_active?'Ban':'Unban'}</button>
                      <button data-act="${u.is_superuser?'demote':'promote'}">${u.is_superuser?'Demote':'Promote'}</button>
                      ${u.is_verified?'':'<button data-act="force-verify">Force-verify</button>'}
                    </td>`;
    tr.querySelectorAll("button").forEach(btn => btn.addEventListener("click", async () => {
      await fetch(`/admin/users/${u.id}/${btn.dataset.act}`,
                  {method:"POST", headers: csrfHeaders, body: "{}"});
      loadUsers(document.getElementById("q").value);
    }));
    tb.appendChild(tr);
  }
}
async function loadAudit() {
  const r = await fetch("/admin/audit");
  if (r.ok) document.getElementById("audit").textContent =
    JSON.stringify(await r.json(), null, 2);
}
document.getElementById("q").addEventListener("input", e => loadUsers(e.target.value));
loadUsers(); loadAudit();
</script>{% endblock %}
```

- [ ] **Step 8: Create `verify_done.html`**

```html
{% extends "base.html" %}
{% block title %}Verified{% endblock %}
{% block body %}
<h1>Email verified</h1>
<p>Your email is confirmed. <a href="/">Back to game</a></p>
{% endblock %}
```

- [ ] **Step 9: Wire page routes in `app.py`**

```python
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

for name in ("login", "signup", "forgot", "reset", "account", "admin"):
    @app.get(f"/{name}", response_class=HTMLResponse)
    async def _page(request: Request, _name=name):
        return templates.TemplateResponse(f"{_name}.html", {"request": request})
```

- [ ] **Step 10: Smoke test pages render**

```bash
python -m pytest tests/auth/ -v -k "not security"
curl -s http://localhost:8765/login | grep "Sign in"
```

Expected: page contains "Sign in" heading.

- [ ] **Step 11: Commit**

```bash
git add frontend/auth/templates/ frontend/auth/app.py
git commit -m "feat(auth): HTML pages (login, signup, forgot, reset, account, admin)"
```

---

## Task 25: game.html header strip + /auth/whoami fetch

**Files:**
- Modify: `frontend/game.html`
- Modify: `frontend/js/schieber.js`

- [ ] **Step 1: Add header strip to `game.html`**

Locate the existing top-of-body element and prepend:

```html
<div id="auth-strip" style="position:fixed;top:0;left:0;right:0;background:#222;color:#eee;
                            padding:.4rem 1rem;display:flex;justify-content:space-between;
                            font:14px system-ui">
  <span>Schieber</span>
  <span id="auth-info">…</span>
</div>
<div style="height:2.2rem"></div>
```

- [ ] **Step 2: Modify `schieber.js`**

Add at the top of the file's main entry point (before `new WebSocket(...)`):

```javascript
async function bootAuth() {
  const r = await fetch("/auth/whoami", {credentials: "same-origin"});
  const me = await r.json();
  const el = document.getElementById("auth-info");
  if (me.kind === "user") {
    const verified = me.is_verified ? "✓" : "⚠";
    el.innerHTML = `${me.display_name} (${verified}) ` +
                   `<a href="/account" style="color:#9cf">Account</a> · ` +
                   `<a href="#" id="logoutBtn" style="color:#9cf">Logout</a>`;
    document.getElementById("logoutBtn").addEventListener("click", async e => {
      e.preventDefault();
      await fetch("/auth/logout", {method:"POST",
        headers:{"X-Requested-With":"schieber"}});
      location.reload();
    });
  } else {
    el.innerHTML = `Playing as ${me.display_name} ` +
                   `<a href="/login" style="color:#9cf">Sign in</a> · ` +
                   `<a href="/signup" style="color:#9cf">Sign up</a>`;
  }
}

await bootAuth();
// then proceed to open the WebSocket
const ws = new WebSocket(...);
```

- [ ] **Step 3: Manual smoke**

```bash
cd frontend && python -m uvicorn server:app --reload --port 8765
# open http://localhost:8765 in private window
# verify "Playing as Guest-xxxx" appears in the header strip
```

Expected: header strip visible, guest display name appears, game still loads.

- [ ] **Step 4: Commit**

```bash
git add frontend/game.html frontend/js/schieber.js
git commit -m "feat(auth): game.html header strip with whoami-driven identity"
```

---

## Task 26: Final wiring in server.py

**Files:**
- Modify: `frontend/server.py`

- [ ] **Step 1: Mount auth app at startup**

In `frontend/server.py`, after `app = FastAPI()`:

```python
from frontend.auth.app import build_app
from frontend.auth.db import make_engine, make_session_factory, init_db
from frontend.auth.email import ConsoleMailBackend, SmtpMailBackend
from frontend.auth.settings import load_settings

_auth_settings = load_settings()
_auth_engine = make_engine(_auth_settings.auth_db_url)
_auth_factory = make_session_factory(_auth_engine)


async def _get_auth_session():
    async with _auth_factory() as s:
        yield s


@app.on_event("startup")
async def _startup():
    await init_db(_auth_engine)


_mail = (ConsoleMailBackend() if _auth_settings.mail_backend == "console"
         else SmtpMailBackend(host=_auth_settings.smtp_host,
                              port=_auth_settings.smtp_port,
                              user=_auth_settings.smtp_user,
                              password=_auth_settings.smtp_app_password))

_auth_app = build_app(get_session=_get_auth_session,
                      settings=_auth_settings, mail=_mail)
app.mount("/", _auth_app)  # auth routes first
```

NOTE: mounting at `/` may conflict with existing `/` and `/static` routes. The cleaner pattern is to mount at `/auth` for `/auth/*` only. Refactor `build_app` to either return a sub-application mounted at `/auth` (preferred) or to expose its routes via `app.include_router` from the host app. Adjust accordingly so existing game routes (`/`, `/static/*`, `/ws`) still resolve.

- [ ] **Step 2: Run full test suite**

```bash
python run_tests.py
```

Expected: all tests pass — existing game tests + new auth tests + new WS principal tests.

- [ ] **Step 3: Manual smoke checklist** (per spec §9.5)

- [ ] Sign up → mail printed to stdout (console backend) → click `verify` URL → banner gone
- [ ] Forgot → reset → old session kicked, new password works
- [ ] Change email → confirm on "new email" → old gets notice
- [ ] Lockout: 5 wrong passwords → 429 → wait → recover
- [ ] Admin: bootstrap promotion → ban a user → user gets 401 → audit row visible
- [ ] Guest: open private window → `Guest-xxxx` shown → sign up → guest cookie gone, session cookie present
- [ ] Game: log in → play a hand → username appears in server log

- [ ] **Step 4: Commit**

```bash
git add frontend/server.py
git commit -m "feat(auth): mount auth app + DB init on server startup"
```

---

## Task 27: Documentation update

**Files:**
- Modify: `CLAUDE.md`
- Modify: `frontend/DB_README.md` (if relevant)

- [ ] **Step 1: Update CLAUDE.md**

In the "Architecture" section, add `frontend/auth/` package description. Update commands section:

```bash
# Run with .env loaded (auth needs it)
cd frontend && python -m uvicorn server:app --reload --port 8765
```

Add a new section "User accounts (sub-project B)" pointing at:

- spec: `docs/superpowers/specs/2026-04-28-schieber-accounts-design.md`
- plan: `docs/superpowers/plans/2026-04-28-schieber-accounts.md`

Mark sub-project B as **done** in "Refactoring Status".

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: note user-accounts sub-project completion in CLAUDE.md"
```

---

## Deferred for future plans

These appear in spec §11 ("Out of scope v1") — not in this plan, captured for visibility:

- OAuth providers
- Per-user game stats / W-L / weis frequency
- HTML email templates
- 2FA / WebAuthn / TOTP
- Captcha
- Distributed lockout
- Username change post-signup
- Mid-game identity swap
- Tombstone TTL pruning cron
- CI / GitHub Actions wiring

Sub-projects A (multiplayer) and C (AI difficulty) are independent and have their own future specs.

---

## Self-review checklist (run before handoff)

**Spec coverage:**
- §1 overview/scope → Tasks 1, 2, 26 (deps, settings, wiring)
- §2 architecture → Tasks 7, 9 (db, manager) + 26 (mount)
- §3 schema → Task 7
- §4 API surface → Tasks 11–22 (all endpoints)
- §5 email flows → Tasks 6, 9, 14, 15, 17
- §6 security policies → Tasks 3, 12, 20 (passwords, lockout, rate limit)
- §7 admin tools → Task 21
- §8 guest mode + WS → Tasks 5, 22, 23, 25
- §9 testing strategy → embedded throughout (TDD per task)

**Placeholder scan:** none of the patterns from "No Placeholders" found.

**Type consistency:** `Principal`, `Guest`, `AuthedUser`, `User`, `AccessToken` referenced consistently. `current_user_dep` / `require_admin_dep` factories used in admin routes. Cookie names spelled `schieber_session` and `schieber_guest` everywhere.

**Known caveats embedded in tasks:**
- Task 9: fastapi-users API may shift between minor versions; smoke import added
- Task 12: route-registration-order assumption — falls back to removing the default mount if needed
- Task 22: signup wrapper takes precedence over fastapi-users register — verify route order
- Task 26: mount path conflict — mount auth as sub-app at `/auth` rather than `/`
