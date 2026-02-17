import hashlib

from ppf.webref.passwords import _password_bytes, hash_password, check_password


def test_password_bytes_from_str():
    result = _password_bytes("password")
    expected = hashlib.sha256(b"password").hexdigest().encode("utf-8")
    assert result == expected
    assert isinstance(result, bytes)
    assert len(result) == 64


def test_password_bytes_from_bytes():
    raw = b"password"
    result = _password_bytes(raw)
    expected = hashlib.sha256(raw).hexdigest().encode("utf-8")
    assert result == expected


def test_hash_password_length():
    pw_hash = hash_password("password")
    assert isinstance(pw_hash, bytes)
    assert len(pw_hash) == 60


def test_check_password_true():
    pw_hash = hash_password("password")
    assert check_password("password", pw_hash) is True


def test_check_password_str_hash():
    pw_hash = hash_password("password").decode("utf-8")
    assert check_password("password", pw_hash) is True


def test_check_password_false():
    pw_hash = hash_password("password")
    assert check_password("not-password", pw_hash) is False
