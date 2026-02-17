import bcrypt
import hashlib


def _password_bytes(password):
    if isinstance(password, str):
        password = password.encode('utf-8')
    password = hashlib.sha256(password).hexdigest().encode('utf-8')
    return password


def hash_password(password):
    password = _password_bytes(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt)


def check_password(password, pw_hash):
    password = _password_bytes(password)
    if isinstance(pw_hash, str):
        pw_hash = pw_hash.encode('utf-8')
    return bcrypt.checkpw(password, pw_hash)
