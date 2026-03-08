from ppf.webref.passwords import hash_password, check_password


def test_hash_password_scrypt():
    pw_hash = hash_password("password")
    assert isinstance(pw_hash, str)
    assert pw_hash.startswith("scrypt:")


def test_hash_password_bytes_raises():
    try:
        hash_password(b"password")
        assert False
    except TypeError:
        assert True


def test_check_password_true():
    pw_hash = hash_password("password")
    assert check_password("password", pw_hash) is True


def test_check_password_bytes_password():
    pw_hash = hash_password("password")
    assert check_password(b"password", pw_hash) is False


def test_check_password_bytes_hash():
    pw_hash = hash_password("password").encode("utf-8")
    assert check_password("password", pw_hash) is False


def test_check_password_false():
    pw_hash = hash_password("password")
    assert check_password("not-password", pw_hash) is False


def test_check_password_empty_hash():
    assert check_password("password", None) is False
