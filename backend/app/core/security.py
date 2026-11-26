"""
Security helpers: password hashing (bcrypt) and login tokens (JWT).

- Passwords are never stored. Only a bcrypt hash is saved; bcrypt is slow on
  purpose and adds a random salt, so stolen hashes are very hard to crack.
- A JWT is a signed note: {"sub": user id, "role": ..., "exp": expiry}.
  The server can check the signature without a database lookup.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import ACCESS_TOKEN_MINUTES, REFRESH_TOKEN_DAYS, SECRET_KEY

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _token(user_id: int, role: str, kind: str, lifetime: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "role": role, "type": kind, "iat": now, "exp": now + lifetime}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int, role: str) -> str:
    return _token(user_id, role, "access", timedelta(minutes=ACCESS_TOKEN_MINUTES))


def create_refresh_token(user_id: int, role: str) -> str:
    return _token(user_id, role, "refresh", timedelta(days=REFRESH_TOKEN_DAYS))


def decode_token(token: str, expected_type: str) -> dict | None:
    """The token's data if the signature, expiry and type are valid, else None."""
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:          # bad signature, expired, malformed ...
        return None
    return data if data.get("type") == expected_type else None
