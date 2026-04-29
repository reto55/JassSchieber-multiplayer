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
