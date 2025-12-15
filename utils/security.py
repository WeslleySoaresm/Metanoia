import bcrypt
from typing import Optional

BCRYPT_PREFIXES = ("$2b$", "$2a$", "$2y$")

def hash_password(plain_password: str, rounds: int = 12) -> str:
    if not plain_password or not isinstance(plain_password, str):
        raise ValueError("Senha inválida")
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def is_probably_bcrypt_hash(s: Optional[str]) -> bool:
    return isinstance(s, str) and any(s.startswith(p) for p in BCRYPT_PREFIXES)