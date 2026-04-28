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
    validate_password("correct horse battery staple", username="alice", email="x@example.com")


def test_long_password_no_truncation_at_72_bytes():
    # Long passwords should be hashable; we don't enforce a max
    validate_password("b" * 200, username="alice", email="x@example.com")
