"""
Service layer: business rules for alerts.
Routers call services; services call repositories.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import alert_repository as repo
from app.schemas.alert import AlertCreate


def list_alerts(db: Session, severity=None, resolved=None):
    return repo.list_alerts(db, severity=severity, resolved=resolved)


def create_alert(db: Session, payload: AlertCreate):
    return repo.create_alert(db, payload.model_dump())   # snake_case dict -> table columns


def resolve_alert(db: Session, alert_id: int):
    alert = repo.get_alert(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved = True
    return repo.save(db, alert)
