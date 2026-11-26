"""The 'users' table: who can log in, and with which role."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(20))           # "admin", "supervisor" or "guard"
    password_hash: Mapped[str] = mapped_column(String(100))  # bcrypt hash, never the password
