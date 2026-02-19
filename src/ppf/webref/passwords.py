from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password):
    if not isinstance(password, str):
        raise TypeError('password must be a string')
    return generate_password_hash(password, method='scrypt', salt_length=16)


def check_password(password, pw_hash):
    if not pw_hash:
        return False
    if not isinstance(password, str):
        return False
    if not isinstance(pw_hash, str):
        return False
    return check_password_hash(pw_hash, password)
