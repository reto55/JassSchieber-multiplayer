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
