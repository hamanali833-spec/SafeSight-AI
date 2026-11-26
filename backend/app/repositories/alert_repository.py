"""
Repository layer: the ONLY place that talks to the database for alerts.
If we move to PostgreSQL, nothing above this layer changes.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert import Alert


def list_alerts(db: Session, severity: str | None = None, resolved: bool | None = None,
                limit: int = 100) -> list[Alert]:
    query = select(Alert).order_by(Alert.created_at.desc(), Alert.id.desc()).limit(limit)
    if severity:
        query = query.where(Alert.severity == severity)
    if resolved is not None:
        query = query.where(Alert.resolved == resolved)
    return list(db.scalars(query))


def get_alert(db: Session, alert_id: int) -> Alert | None:
    return db.get(Alert, alert_id)


def create_alert(db: Session, data: dict) -> Alert:
    alert = Alert(**data)
    db.add(alert)
    db.commit()
    db.refresh(alert)      # load the id and created_at the database filled in
    return alert


def save(db: Session, alert: Alert) -> Alert:
    db.commit()
    db.refresh(alert)
    return alert


def count_by(db: Session, column) -> dict[str, int]:
    """GROUP BY one column: {value: number of alerts}. The database does the counting."""
    rows = db.execute(select(column, func.count()).group_by(column)).all()
    return {str(value): n for value, n in rows}


def count_where(db: Session, *conditions) -> int:
    return db.scalar(select(func.count()).select_from(Alert).where(*conditions)) or 0


def created_times(db: Session) -> list:
    return list(db.scalars(select(Alert.created_at)))
