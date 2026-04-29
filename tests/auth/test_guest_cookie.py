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
