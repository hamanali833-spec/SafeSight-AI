"""Shapes of login data (camelCase JSON)."""
from typing import Literal

from app.schemas.alert import CamelModel

Role = Literal["admin", "supervisor", "guard"]


class LoginIn(CamelModel):
    email: str
    password: str


class RefreshIn(CamelModel):
    refresh_token: str


class UserOut(CamelModel):
    id: int
    email: str
    name: str
    role: Role


class TokenOut(CamelModel):
    access_token: str
    refresh_token: str
    user: UserOut
