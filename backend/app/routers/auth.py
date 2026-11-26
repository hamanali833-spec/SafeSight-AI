"""
Login endpoints.

POST /api/auth/login    email + password -> access token (30 min) + refresh token (7 days)
POST /api/auth/refresh  refresh token    -> a new access token, without typing the password again
GET  /api/auth/me       who am I?
"""
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.auth import current_user
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import LoginIn, RefreshIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Rate limit: at most 5 FAILED logins per minute from one address, so nobody can
# try thousands of passwords (brute force). Successful logins are not counted,
# so switching between demo accounts never locks you out.
MAX_FAILURES, WINDOW_S = 5, 60
_attempts: dict[str, deque] = defaultdict(deque)     # ip -> times of recent failures


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _check_rate_limit(ip: str):
    now = time.monotonic()
    failures = _attempts[ip]
    while failures and now - failures[0] > WINDOW_S:   # forget failures older than the window
        failures.popleft()
    if len(failures) >= MAX_FAILURES:
        raise HTTPException(429, "Too many failed logins. Please wait a minute.")


def _tokens(user: User) -> TokenOut:
    return TokenOut(access_token=create_access_token(user.id, user.role),
                    refresh_token=create_refresh_token(user.id, user.role),
                    user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = _client_ip(request)
    _check_rate_limit(ip)
    user = user_repository.get_by_email(db, body.email)
    # Same message for "no such email" and "wrong password": don't reveal which emails exist
    if user is None or not verify_password(body.password, user.password_hash):
        _attempts[ip].append(time.monotonic())
        raise HTTPException(401, "Wrong email or password")
    _attempts.pop(ip, None)          # a correct login clears the failures
    return _tokens(user)


@router.post("/refresh", response_model=TokenOut)
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    data = decode_token(body.refresh_token, "refresh")
    user = user_repository.get(db, int(data["sub"])) if data else None
    if user is None:
        raise HTTPException(401, "Session expired, please log in again")
    return _tokens(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
