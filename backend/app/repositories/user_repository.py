"""The only place that reads and writes the users table."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User

# Demo accounts created on the first start. Change these passwords in production!
DEMO_USERS = [
    ("admin@safesight.ai", "Ayesha Admin", "admin", "admin123"),
    ("supervisor@safesight.ai", "Saad Supervisor", "supervisor", "super123"),
    ("guard@safesight.ai", "Gul Guard", "guard", "guard123"),
]


def seed_demo_users(db: Session):
    if db.scalar(select(User).limit(1)) is None:
        db.add_all(User(email=e, name=n, role=r, password_hash=hash_password(p)) for e, n, r, p in DEMO_USERS)
        db.commit()


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.strip().lower()))


def get(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)
