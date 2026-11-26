"""
The 'cameras' table: one row per CCTV camera and its settings.
The camera id is also the name of its zone file (zones/<id>.json).
"""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)   # e.g. "warehouse"
    name: Mapped[str] = mapped_column(String(60))                    # shown on the dashboard
    ppe_required: Mapped[bool] = mapped_column(Boolean, default=True)  # check helmets and vests here?
