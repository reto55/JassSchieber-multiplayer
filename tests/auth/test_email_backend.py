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
    asyncio.run(backend.send(m))
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
