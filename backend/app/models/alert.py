"""
The 'alerts' database table.
Indexes make the dashboard's common queries fast as the table grows.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    camera_id: Mapped[str] = mapped_column(String(50))
    track_id: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(20))        # "PPE" or "ZONE"
    severity: Mapped[str] = mapped_column(String(20))    # "REVIEW", "PARTIAL" or "HIGH"
    message: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        # "latest alerts of camera X" -> camera + time together
        Index("ix_alerts_camera_created", "camera_id", "created_at"),
        # "all open HIGH alerts" -> filter by severity
        Index("ix_alerts_severity", "severity"),
    )
