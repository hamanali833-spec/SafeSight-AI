"""
FastAPI dependencies that protect endpoints.

    user: User = Depends(current_user)                    -> any logged-in user
    user: User = Depends(require_roles("admin"))          -> only admins
    Depends(require_roles_or_pipeline("admin", ...))      -> those roles, or the pipeline's API key

No token or a bad token -> 401 Unauthorized. Wrong role -> 403 Forbidden.
"""
import hmac

from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import PIPELINE_API_KEY
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repositories import user_repository

UNAUTHORIZED = HTTPException(401, "Please log in", headers={"WWW-Authenticate": "Bearer"})


def _user_from_token(token: str | None, db: Session) -> User | None:
    data = decode_token(token, "access") if token else None
    return user_repository.get(db, int(data["sub"])) if data else None


def _bearer(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:]
    return None


def current_user(authorization: str | None = Header(None),
                 token: str | None = Query(None, include_in_schema=False),
                 db: Session = Depends(get_db)) -> User:
    """
    The logged-in user. The token normally comes in the Authorization header;
    <img> tags can't send headers, so the preview image may pass ?token= instead.
    """
    user = _user_from_token(_bearer(authorization) or token, db)
    if user is None:
        raise UNAUTHORIZED
    return user


def require_roles(*roles: str):
    def check(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(403, "Your role is not allowed to do this")
        return user
    return check


def require_roles_or_pipeline(*roles: str):
    """A user with one of these roles, OR the video pipeline with its API key."""
    def check(authorization: str | None = Header(None),
              x_api_key: str | None = Header(None),
              db: Session = Depends(get_db)):
        # compare_digest: same time for right and wrong keys, so the key can't be guessed by timing
        if x_api_key and hmac.compare_digest(x_api_key, PIPELINE_API_KEY):
            return None
        user = _user_from_token(_bearer(authorization), db)
        if user is None:
            raise UNAUTHORIZED
        if user.role not in roles:
            raise HTTPException(403, "Your role is not allowed to do this")
        return user
    return check
