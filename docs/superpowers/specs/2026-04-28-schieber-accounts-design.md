# Schieber — User Accounts Design

**Date:** 2026-04-28
**Status:** Draft (pending user review before plan)
**Scope:** Sub-project B of a larger effort. Sub-projects A (networked multiplayer) and C (AI difficulty) are deferred to their own specs.

## 1. Overview & Scope

### 1.1 Goal

Add public-internet-grade user accounts to Schieber. Users can sign up, log in, recover their password, and manage their account. Anonymous "guest" play stays available — accounts gate identity, not gameplay.

### 1.2 Decisions

| Question | Choice |
|---|---|
| Deployment scope | Public internet — real threat model |
| Auth method | Email + password (OAuth deferred) |
| Persistence per account | Identity only — no per-user stats yet |
| Session model | HttpOnly server-side session cookie |
| Email verification | Soft (login allowed, banner if unverified) |
| SMTP transport | Gmail app-password via `aiosmtplib` |
| Login identity | Username (display, unique) + email (login, unique) |
| v1 features | All listed (signup, verify, reset, change-pw/email, delete/export, rate-limit, lockout, admin, guest) |
| Implementation approach | `fastapi-users` library |
| DB layer coexistence | Separate DBs — `auth.db` for accounts, `schieber.db` unchanged |

### 1.3 New stack additions

- `fastapi-users[sqlalchemy]` — signup/login/verify/reset/change/OAuth-ready
- `passlib[bcrypt]` — transitive
- `aiosmtplib` — Gmail SMTP client
- `sqlalchemy[asyncio]` + `aiosqlite`
- `slowapi` — rate-limit
- `itsdangerous` — guest cookie HMAC signing
- `pytest-asyncio` — dev only
- `jinja2` — minimal HTML templates

### 1.4 What stays untouched

- `Cards.py`
- `frontend/game_session.py` mechanics (one new constructor argument: `principal`; existing logic untouched)
- `frontend/database_manager.py` (raw `sqlite3` for game data)
- All of `frontend/utils/`
- `tests/test_card_utils.py`, `test_game_utils.py`, `test_db_utils.py`, `test_integration.py`

`tests/test_game_session.py` gets two new principal-injection cases (see §9.4) but its existing cases stand.

### 1.5 Public surface added

`/signup`, `/login`, `/logout`, `/verify`, `/forgot`, `/reset`, `/account`, `/admin` (HTML pages), plus the matching `/auth/*` and `/admin/*` JSON endpoints. Existing `/` (game) and `/ws` (now reads cookie) keep their paths.

---

## 2. Architecture

### 2.1 Module layout

```
frontend/auth/
  __init__.py
  db.py              ← async SQLAlchemy engine + session factory (auth.db)
  models.py          ← User, AccessToken, EmailToken, LockoutAttempt, Tombstone, AdminAudit
  schemas.py         ← pydantic UserRead/UserCreate/UserUpdate
  manager.py         ← UserManager (fastapi-users hook for verify/reset emails)
  email.py           ← aiosmtplib send_verification, send_reset, send_change_notice
  routes.py          ← signup/login/verify/forgot/reset/change-pw/change-email/delete/export
  admin.py           ← admin endpoints (list, ban, promote, audit)
  ratelimit.py       ← slowapi limiter config + lockout policy
  guest.py           ← Guest dataclass, cookie issuance/verification
  deps.py            ← FastAPI dependencies: current_user, current_principal, require_admin
  templates/
    base.html        ← shared header/footer
    login.html
    signup.html
    forgot.html
    reset.html
    account.html
    admin.html
    verify_done.html
  data/
    common-passwords.txt   ← top-1k blocklist, ~10 KB
```

### 2.2 Request flow

```
Browser → /                        public, served by FastAPI (game.html)
Browser → /signup, /login, ...     HTML forms; vanilla-JS POSTs to /auth/* JSON endpoints
Browser → /auth/whoami             called by game.html on load — issues guest cookie if needed
Browser → /ws                      WebSocket; resolves principal from cookies at handshake
                                   (cookie always present because /auth/whoami ran first)
                                   passes principal into GameSession constructor.
                                   GameSession unchanged in mechanics; uses principal only for
                                   server-side log labelling.
```

### 2.3 Configuration

`.env` (gitignored), loaded via `pydantic-settings`:

```
SECRET_KEY=...                     # 32-byte urlsafe
BASE_URL=https://schieber.example  # used in email links + Secure-cookie inference
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=schieber@example.com     # also used as From
SMTP_APP_PASSWORD=...              # 16-char Google app password
ADMIN_BOOTSTRAP_EMAIL=reto@example.com
MAIL_BACKEND=smtp                  # smtp | console (tests/dev)
```

`ADMIN_BOOTSTRAP_EMAIL` must be present at startup. If unset, server logs a warning and refuses to start.

### 2.4 Admin bootstrap

The first user signing up with `email == ADMIN_BOOTSTRAP_EMAIL` is auto-promoted (`is_superuser=True`). After bootstrap, the env var has no effect; further admins are promoted via `/admin/users/{id}/promote`.

---

## 3. Schema (`auth.db`)

```sql
CREATE TABLE user (
    id              CHAR(36) PRIMARY KEY,           -- UUID
    email           VARCHAR(320) UNIQUE NOT NULL,
    username        VARCHAR(32)  UNIQUE NOT NULL,   -- ^[a-zA-Z0-9_-]{3,32}$
    hashed_password VARCHAR(1024) NOT NULL,         -- bcrypt
    is_active       BOOLEAN NOT NULL DEFAULT 1,     -- false = banned
    is_superuser    BOOLEAN NOT NULL DEFAULT 0,
    is_verified     BOOLEAN NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL,
    last_login_at   TIMESTAMP
);

CREATE TABLE access_token (
    token       VARCHAR(43) PRIMARY KEY,            -- secrets.token_urlsafe(32)
    user_id     CHAR(36) NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at  TIMESTAMP NOT NULL,
    expires_at  TIMESTAMP NOT NULL                  -- 2h normal, 30d remember-me
);
CREATE INDEX ix_access_token_user ON access_token(user_id);

CREATE TABLE email_token (
    token       VARCHAR(43) PRIMARY KEY,
    user_id     CHAR(36) NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    purpose     VARCHAR(16) NOT NULL,               -- 'verify' | 'reset' | 'change_email'
    new_value   TEXT,                               -- proposed new email when purpose='change_email'
    expires_at  TIMESTAMP NOT NULL,                 -- verify=7d, reset=1h, change_email=1h
    used_at     TIMESTAMP                           -- NULL = unused
);

CREATE TABLE lockout_attempt (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       VARCHAR(320) NOT NULL,              -- attempted email (may not match a user)
    ip          VARCHAR(45)  NOT NULL,
    attempted_at TIMESTAMP NOT NULL,
    success     BOOLEAN NOT NULL
);
CREATE INDEX ix_lockout_email_time ON lockout_attempt(email, attempted_at);
CREATE INDEX ix_lockout_ip_time    ON lockout_attempt(ip,    attempted_at);

CREATE TABLE tombstone (
    id              CHAR(36) PRIMARY KEY,           -- copy of deleted user.id
    email_hash      CHAR(64) NOT NULL,              -- sha256(email)
    username_hash   CHAR(64) NOT NULL,              -- sha256(username, lower)
    deleted_at      TIMESTAMP NOT NULL
);
CREATE INDEX ix_tombstone_email_hash ON tombstone(email_hash);
CREATE INDEX ix_tombstone_username_hash ON tombstone(username_hash);

CREATE TABLE admin_audit (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id    CHAR(36) NOT NULL REFERENCES user(id),
    action      VARCHAR(32) NOT NULL,               -- 'ban' | 'unban' | 'promote' | 'demote'
                                                    -- | 'force_verify' | 'delete'
    target_id   CHAR(36),
    reason      TEXT,
    created_at  TIMESTAMP NOT NULL,
    ip          VARCHAR(45) NOT NULL
);
CREATE INDEX ix_admin_audit_created ON admin_audit(created_at);
```

### 3.1 Soft-delete

`DELETE /auth/account` does **not** issue `DROP` on the row; instead it:

1. anonymises the `user` row (email/username overwritten with `deleted-{uuid}@invalid` / `deleted-{first8}` to free uniqueness slots),
2. clears `hashed_password`,
3. sets `is_active=False`,
4. inserts a row in `tombstone` with `sha256(original_email)` and `sha256(original_username.lower())`.

Signup endpoint refuses (`409`) when the proposed email or username matches a tombstone hash newer than 30 days. After 30 days the email/username can be reclaimed (manual prune cron is out of scope; tombstones simply accumulate but are TTL-checked at signup query time).

### 3.2 Username

Locked at signup, **not** changeable in v1 (avoids tombstone churn). Email is changeable via the change-email flow.

---

## 4. API Surface

All `/auth/*` and `/admin/*` routes accept and return JSON. HTML pages are thin Jinja shells that POST to these via vanilla `fetch()` with `X-Requested-With: schieber` header.

### 4.1 Auth routes

```
POST   /auth/signup              {email, username, password}
                                  → 201 + Set-Cookie schieber_session
                                  → 409 if email/username taken (live or tombstoned <30d)
                                  → 422 if password rules / username regex / email format fail

POST   /auth/login               {email, password, remember?}
                                  → 200 + Set-Cookie schieber_session (HttpOnly, Secure*, SameSite=Lax)
                                  → cookie max-age: 2h normal, 30d if remember=true
                                  → 401 on bad creds (logs lockout_attempt row)
                                  → 429 if locked out
                                  (* Secure inferred from BASE_URL https://)

POST   /auth/logout              cookie required
                                  → deletes access_token row + clears cookie

GET    /auth/verify?token=…      one-shot from email
                                  → 200 (HTML "verified") + flips is_verified=True
                                  → 410 expired/used (also HTML)

POST   /auth/resend-verification cookie required
                                  → 202 (sends new mail; rate-limited)

POST   /auth/forgot              {email}
                                  → 202 always (no enumeration). Mail sent if email exists
                                    AND user is_active.

POST   /auth/reset               {token, new_password}
                                  → 200, sets new bcrypt hash, deletes ALL access_tokens
                                    for the user
                                  → 410 expired/used

GET    /auth/me                  cookie required
                                  → {id, email, username, is_verified, is_superuser}

POST   /auth/change-password     cookie required, {current_password, new_password}
                                  → 200, keeps current session, deletes all OTHER access_tokens

POST   /auth/change-email        cookie required, {new_email, current_password}
                                  → 202, sends confirm mail to new_email; notice mail to old
                                  → 409 if new_email is taken or tombstoned <30d

GET    /auth/confirm-email?token=…   one-shot from new-email link
                                      → 200 swaps email column, keeps current session

DELETE /auth/account             cookie required, {current_password}
                                  → 200, soft-deletes user (see 3.1), clears cookie

GET    /auth/export              cookie required
                                  → 200 application/json: {user, access_tokens, email_tokens}
                                    (game data is anonymous; not joined)

GET    /auth/whoami              public
                                  → 200 when authed:
                                       {kind: 'user', display_name, is_verified, is_superuser}
                                    when guest:
                                       {kind: 'guest', display_name}
                                  → side-effect: issues schieber_guest cookie if neither
                                                 schieber_session nor schieber_guest is sent
```

### 4.2 Admin routes (superuser-only)

```
GET    /admin                              HTML, paginated user list
GET    /admin/users?page=1&q=…             JSON list with search by email substring or username
GET    /admin/users/{id}                   JSON single user
POST   /admin/users/{id}/ban               {reason?} → is_active=False, revokes tokens
POST   /admin/users/{id}/unban             → is_active=True
POST   /admin/users/{id}/promote           → is_superuser=True
POST   /admin/users/{id}/demote            → is_superuser=False; 409 if target == self
POST   /admin/users/{id}/force-verify      → is_verified=True (skip email)
DELETE /admin/users/{id}                   → soft-delete (same path as user-self-delete)
GET    /admin/audit                        last 200 admin_audit rows
```

Every state-changing admin endpoint inserts an `admin_audit` row before responding.

### 4.3 HTML pages

Each is a single Jinja template extending `base.html` (~30 LoC each):

- `/login`
- `/signup`
- `/forgot`
- `/reset?token=…` (auto-fills hidden token field)
- `/account` (info + change-pw + change-email + delete forms)
- `/admin` (admin user list, search, audit tab)

`game.html` (existing) gets a small header strip rendered client-side from `/auth/whoami` — no SSR change.

### 4.4 Password rules (signup, reset, change-password)

- Length ≥ 10 chars (bcrypt's 72-byte ceiling sidestepped by passlib's sha256 prehash)
- Reject membership in `auth/data/common-passwords.txt` (top 1000)
- Reject if password contains the username (case-insensitive substring) or the local-part of the email
- No mandatory mixed-case / digit / symbol — length is the requirement (NIST SP 800-63B)

### 4.5 Cookie names

- `schieber_session` — auth, HttpOnly, Secure (when BASE_URL https), SameSite=Lax, Path=/
- `schieber_guest` — guest, HttpOnly, Secure, SameSite=Lax, Path=/, Max-Age=30d, signed via `itsdangerous` HMAC

---

## 5. Email Flows

Plain-text only in v1 (HTML email templates deferred). Sender = `SMTP_USER`. All flows tolerant of SMTP failure: on send error, log it and return success to the user; resend endpoints exist for recovery.

### 5.1 Signup verification (soft)

- Trigger: `POST /auth/signup` succeeds
- Token: `secrets.token_urlsafe(32)`, `purpose='verify'`, expires 7 d
- Email body:

      Subject: Confirm your Schieber account
      Hi {username},
      Confirm your email within 7 days:
      {BASE_URL}/auth/verify?token={token}
      If you didn't sign up, ignore this message.

- Account works immediately. After 7 d the unverified banner stays; no auto-deletion (admins can ban manually).
- Resend: `POST /auth/resend-verification` — rate limit 1/min, 5/day.

### 5.2 Password reset

- Trigger: `POST /auth/forgot {email}`
  - If email matches an active user: issue token, send mail.
  - Always respond `202` (anti-enumeration).
- Token: `purpose='reset'`, expires 1 h, single-use.
- Email body:

      Subject: Reset your Schieber password
      Someone requested a password reset for {username}.
      Click within 1 hour:
      {BASE_URL}/reset?token={token}
      If this wasn't you, no action needed — your password is unchanged.

- Follow-up `POST /auth/reset {token, new_password}` sets new hash, deletes **all** access tokens for the user, marks email_token used.
- Rate limit: 3/min and 10/day per IP; 5/day per email.

### 5.3 Change email

- Trigger: `POST /auth/change-email {new_email, current_password}`
- Token: `purpose='change_email'`, `new_value=<new_email>`, expires 1 h
- Two emails:
  - **Confirm link → new email:**

        Subject: Confirm new email for Schieber
        Click to switch your account email:
        {BASE_URL}/auth/confirm-email?token={token}

  - **Notice → old email** (informational, non-actionable):

        Subject: Email change requested on your Schieber account
        Someone requested to change your account email to {masked_new_email}.
        If this wasn't you, change your password immediately.

  Where `masked_new_email` = first 3 chars of local-part + `***` + `@domain`.
- Follow-up `GET /auth/confirm-email?token=…` swaps the `email` column and keeps the current session.

### 5.4 SMTP failure handling

- Send fails on signup → user is created anyway (soft verify); banner shows "verification mail couldn't be sent — click resend".
- Send fails on forgot/reset/change → log error, return success (privacy + retry).
- Hard SMTP outage: users can still sign up and log in; verification stalls. No alerting in v1.

### 5.5 Local development & tests

- `MAIL_BACKEND=console` writes mails to stdout instead of sending. Tests use this and assert on captured output.
- Optional `MAIL_BACKEND=smtp` with `SMTP_HOST=localhost SMTP_PORT=1025` for `aiosmtpd` / `python -m smtpd` dev sinks.

---

## 6. Security Policies

### 6.1 Password storage
- bcrypt via passlib, cost 12 (fastapi-users default)
- Constant-time compare via passlib

### 6.2 Rate limiting (`slowapi`, in-memory single-instance)

| Endpoint | Per-IP | Per-account |
|---|---|---|
| `POST /auth/signup` | 5 / hour | — |
| `POST /auth/login` | 20 / 15 min | (lockout, see 6.4) |
| `POST /auth/forgot` | 3 / min, 10 / day | 5 / day per email |
| `POST /auth/resend-verification` | 5 / day | 5 / day per user |
| `POST /auth/reset` | 10 / hour | — |
| `POST /auth/change-password` | 10 / hour | 10 / hour per user |
| `POST /auth/change-email` | 5 / day | 3 / day per user |
| `GET /auth/whoami` | 30 / min | — |
| `/admin/*` (state-changing) | 60 / min | (per superuser) |

429 with `Retry-After` header on hit.

### 6.3 Lockout policy

- 5 failed `/auth/login` attempts on the same email **OR** 10 from the same IP within 15 min → 15-min lockout (returns 429).
- Generic message — does not leak which axis triggered.
- Successful login clears the email's failure streak; the IP streak persists (IPs are shared resources).
- State held in `lockout_attempt` table; queried each login attempt.

### 6.4 Session cookie

- `schieber_session` — HttpOnly, Secure*, SameSite=Lax, Path=/
- Token = `secrets.token_urlsafe(32)` (43 chars), random, stored server-side
- Lifetime: 2 h sliding (renewed on use within last 30 min) for normal login; 30 d fixed for `remember=true`
- Server-side row deleted on: logout (this token), password change (all but current), password reset (all), ban, account delete
- *Secure flag set when `BASE_URL` starts with `https://`

### 6.5 Guest cookie

- `schieber_guest` — HttpOnly, Secure*, SameSite=Lax, Max-Age 30 d
- Value = `itsdangerous.URLSafeSerializer(SECRET_KEY).dumps({"id": secrets.token_hex(16)})`
- Signature verified on every read; tampered cookies are dropped (server issues a new one).
- No DB row. Signing up while holding a guest cookie clears it (`Max-Age=0`).

### 6.6 CSRF

- All state-changing routes are POST/DELETE with JSON body and require `X-Requested-With: schieber` header (set by our JS).
- SameSite=Lax cookie blocks classic form-CSRF; the custom header forces a CORS preflight on cross-origin requests, which our server denies (no CORS middleware = no `Access-Control-Allow-Origin`, browser blocks the request).
- No double-submit token in v1; documented limitation. Revisit if exposure widens (e.g., we later add a public API).

### 6.7 Transport
- `BASE_URL` is https in production. uvicorn behind a reverse proxy (nginx/caddy) terminates TLS — out of scope for this design.
- HSTS, cert renewal, SPF/DKIM/DMARC for the SMTP From-domain — operator's responsibility.

### 6.8 Threat model — out of scope (documented, not implemented)
- Captcha / bot mitigation beyond rate limit
- Anomaly-based account-takeover detection
- 2FA / TOTP / WebAuthn
- Distributed lockout (single-instance v1)
- WS-handshake `Origin` header check (accept all matching `BASE_URL` host)

---

## 7. Admin Tools

### 7.1 Bootstrap

`ADMIN_BOOTSTRAP_EMAIL` env var set → first user signing up with that email is auto-promoted. Env var must be present at startup or server refuses to start.

### 7.2 Endpoints

See §4.2.

### 7.3 Audit log

Every state-changing admin endpoint writes an `admin_audit` row (admin_id, action, target_id, reason, created_at, ip) before responding.

### 7.4 UI

Single Jinja template `admin.html` — table of users with action buttons, search box, pagination, audit-log tab. Vanilla `fetch()` against the JSON endpoints; no JS framework. ~150 LoC HTML+JS.

Banned users: greyed italic. Superusers: bold.

### 7.5 Out of scope
- Multi-tier permissions (just superuser/normal in v1)
- Email-based admin invites
- Admin-initiated password reset (admins can ban + force-verify; users self-reset)
- Bulk operations
- IP-based ban

---

## 8. Guest Mode & WebSocket Integration

### 8.1 Principal model

```python
@dataclass(frozen=True)
class AuthedUser:
    user_id: str
    username: str
    is_superuser: bool
    is_verified: bool

@dataclass(frozen=True)
class Guest:
    guest_id: str          # 16-byte hex from itsdangerous payload
    display_name: str      # f"Guest-{guest_id[:4]}"

Principal = Union[AuthedUser, Guest]
```

### 8.2 Cookie issuance

WebSocket handshake **does not** issue cookies (`Set-Cookie` on a 101 response is unreliable across browsers). Instead:

- `game.html` calls `GET /auth/whoami` on page load **before** opening the WebSocket.
- `/auth/whoami` issues `schieber_guest` cookie via Set-Cookie on its 200 response when neither `schieber_session` nor `schieber_guest` was sent.
- WS handshake then always has a usable cookie.

### 8.3 WS handshake

```python
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    principal = await resolve_principal(ws)   # reads ws.cookies (FastAPI exposes them)
    await ws.accept()
    session = GameSession(principal=principal)
    await session.run(ws)
```

`resolve_principal` priority:

1. `schieber_session` present and matches a non-expired `access_token` row whose user has `is_active=True` → `AuthedUser`.
2. `schieber_session` present but user is banned (`is_active=False`) → treat as no session: server deletes the stale `access_token` row (defence-in-depth; ban already deletes them) and falls through.
3. `schieber_guest` present and HMAC-valid → `Guest` from cookie payload.
4. Neither cookie present (programmatic WS client that bypassed `/auth/whoami`) → mint a transient `Guest` with a fresh random id, no cookie sent.

### 8.4 GameSession changes

```python
class GameSession:
    def __init__(self, end_game: int = 1000, principal: Principal | None = None):
        self.principal = principal
        ...
```

- Used **only** for log labelling (`logger.info("game start by %s", principal.display_name)`).
- **Not** persisted into game DB. `spieler` table keeps its 4 fixed seats — game data stays anonymous (Q4 = identity-only).
- Game mechanics, scoring, message protocol, all unchanged.

### 8.5 game.html header strip

Rendered client-side from `/auth/whoami` response, ~40 LoC HTML+CSS+JS:

```
[Schieber]                            [Sign in] [Sign up]
[Schieber]    Playing as Guest-3f9a   [Sign in] [Sign up]
[Schieber]    reto (✓ verified)       [Account] [Logout]
[Schieber]    reto (⚠ verify email)   [Resend] [Account] …
```

### 8.6 Transitions

- **Authed → guest** (logout): `schieber_session` cookie cleared. Browser still has `schieber_guest`? Unlikely (it was deleted at signup), so next `/auth/whoami` issues a fresh one.
- **Guest → authed** (signup or login): `schieber_guest` cookie cleared (`Max-Age=0`); `schieber_session` issued. Any in-flight WS game continues with its old `principal` until disconnect — acceptable, identity-only.

### 8.7 Out of scope
- Mid-game identity swap (guest → authed during an open WS)
- Custom guest nicknames (only `Guest-xxxx`)
- Anti-abuse on guest cookie issuance beyond `/auth/whoami` rate limit (30/min/IP)

---

## 9. Testing Strategy

### 9.1 New test layout

```
tests/auth/
  __init__.py
  conftest.py                       fixtures: in-memory auth.db, async client, mail capture
  test_signup.py
  test_login.py
  test_logout.py
  test_verify.py
  test_password_reset.py
  test_change_password.py
  test_change_email.py
  test_account_delete.py
  test_account_export.py
  test_admin.py
  test_guest.py
  test_ratelimit.py
  test_security.py
  test_email_render.py
```

Adds `pytest-asyncio` to dev deps. Existing `tests/test_*.py` untouched.

### 9.2 Coverage targets per file

- **test_signup** — happy path; dup email; dup username; weak password; invalid email format; tombstone collision <30d; tombstone >30d allowed; rate limit
- **test_login** — happy; wrong password; banned user (401); locked out (429); remember-me cookie length; IP lockout vs email lockout; success clears email streak
- **test_logout** — single session deleted; other sessions live
- **test_verify** — verify success; expired token (410); used token (410); resend-verification rate limit
- **test_password_reset** — `/forgot` 202 for unknown email (anti-enumeration); reset token expiry; single-use; reset deletes all access tokens
- **test_change_password** — happy; wrong current_password (401); other sessions deleted, current session kept
- **test_change_email** — happy 2-step; old-email notice sent; confirm link expiry; new-email collision (409)
- **test_account_delete** — soft delete; tombstone row written; cookie cleared; email/username locked at signup for 30 d
- **test_account_export** — JSON shape; only own user's data
- **test_admin** — bootstrap email auto-promotes first signup; ban revokes all access tokens; promote/demote; demote-self blocked (409); audit row written
- **test_guest** — `/auth/whoami` issues cookie; signup clears guest cookie; logout → next `/auth/whoami` re-issues; tampered cookie HMAC rejected
- **test_ratelimit** — signup, login, forgot, whoami all 429 at threshold; `Retry-After` header present
- **test_security** — Set-Cookie flags (HttpOnly, SameSite, Secure inferred from BASE_URL); CSRF requires `X-Requested-With`
- **test_email_render** — verify/reset/change templates render expected fields; reset link contains the token

### 9.3 Fixtures (tests/auth/conftest.py)

```python
@pytest.fixture
async def auth_db(): ...                  # aiosqlite :memory: + create_all
@pytest.fixture
async def app(auth_db): ...               # FastAPI app with overridden DB dep
@pytest.fixture
async def client(app): ...                # httpx.AsyncClient(transport=ASGITransport(app))
@pytest.fixture
def captured_mail(monkeypatch): ...       # MAIL_BACKEND=console; collects mails into list
@pytest.fixture
async def user(client, captured_mail): ...  # signed-up + verified
@pytest.fixture
async def admin(client, captured_mail): ... # bootstrap-promoted admin
```

### 9.4 Existing-suite extension

`tests/test_game_session.py` adds two cases:

- `test_ws_with_user_principal` — WS receives a logged-in cookie; principal is `AuthedUser`; game runs normally; log includes username
- `test_ws_with_guest_principal` — WS without auth cookie; principal is `Guest`; game runs normally

### 9.5 Manual smoke checklist (run before each deploy)

- Sign up → mail arrives → click verify → banner gone
- Forgot → reset → old session kicked, new password works
- Change email → confirm on new address → old gets notice
- Lockout: 5 wrong passwords → 429 → wait → recover
- Admin: bootstrap promotion → ban a user → user gets 401 → audit row visible
- Guest: open private window → `Guest-xxxx` shown → sign up → guest cookie gone, session cookie present
- Game: log in → play a hand → username appears in server log

### 9.6 Out of scope for v1

- Real Gmail SMTP delivery test (uses MAIL_BACKEND=console)
- bcrypt / SQLAlchemy / fastapi-users built-ins (trusted libs)
- Real browser cookie behaviour (manual smoke)
- CI wiring — `python run_tests.py` runs everything in-process

---

## 10. Open follow-ups for sub-projects A and C

These are NOT in this spec; they're noted so the implementation plan doesn't bake in assumptions that block them.

- **Sub-project A (multiplayer):** identity-only model means `principal` is the only handle a multi-player matchmaking layer needs. No schema change here will block A.
- **Sub-project C (AI difficulty):** orthogonal to auth. Note: CLAUDE.md's reference to `max_game()` is stale (deleted in E6); current AI is `frontend/game_session.py:ai_select_card`. Sub-project C will need to clarify whether to resurrect `max_game` from git history or build difficulty levels on top of `ai_select_card`.

---

## 11. Out of scope (v1) — quick reference

- OAuth providers (deferred per Q3=d)
- Per-user stats / W-L / weis frequency (deferred per Q4=a)
- HTML email templates (plain text only)
- 2FA / WebAuthn / TOTP
- Captcha
- Distributed lockout (single instance)
- Username change post-signup
- Mid-game identity swap
- Tombstone TTL pruning cron
- CI / GitHub Actions wiring
