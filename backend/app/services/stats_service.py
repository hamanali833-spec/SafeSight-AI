"""
Analytics for the dashboard: counts of alerts by type, severity, camera and hour.
"""
from collections import Counter

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.repositories import alert_repository as repo


def get_stats(db: Session) -> dict:
    # Alerts per hour of the day, e.g. "20:00" -> 4 (works on SQLite and PostgreSQL)
    hours = Counter(t.strftime("%H:00") for t in repo.created_times(db))
    return {
        "total": repo.count_where(db),
        "open": repo.count_where(db, Alert.resolved.is_(False)),
        "open_high": repo.count_where(db, Alert.resolved.is_(False), Alert.severity == "HIGH"),
        "by_kind": repo.count_by(db, Alert.kind),
        "by_severity": repo.count_by(db, Alert.severity),
        "by_camera": repo.count_by(db, Alert.camera_id),
        "by_hour": dict(sorted(hours.items())),
    }
