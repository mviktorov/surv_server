import random
import string

import bcrypt

from surv_server.settings import settings

UID_CHARS = string.ascii_letters + string.digits


def gen_uid(length: int) -> str:
    return "".join(random.SystemRandom().choice(UID_CHARS) for _ in range(length))


def hash_password(password: str) -> str:
    salt = settings.POSTGRES_PASSWORD_SALT
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8"))
    return password_hash.decode("utf-8")
