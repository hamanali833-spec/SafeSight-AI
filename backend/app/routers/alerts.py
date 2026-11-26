"""
Router layer: HTTP endpoints for alerts. Only reads the request and returns
the response; all logic lives in the service layer.
"""
from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import current_user, require_roles, require_roles_or_pipeline
from app.core.database import get_db
from app.schemas.alert import AlertCreate, AlertOut
from app.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut], dependencies=[Depends(current_user)])
def list_alerts(severity: Literal["REVIEW", "PARTIAL", "HIGH"] | None = None,
                resolved: bool | None = None,
                db: Session = Depends(get_db)):
    """Newest alerts first. Optional filters: ?severity=HIGH&resolved=false"""
    return alert_service.list_alerts(db, severity=severity, resolved=resolved)


@router.post("", response_model=AlertOut, status_code=201,
             dependencies=[Depends(require_roles_or_pipeline("admin", "supervisor"))])
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    """Called by the video pipeline when it raises an alert."""
    return alert_service.create_alert(db, payload)


@router.patch("/{alert_id}/resolve", response_model=AlertOut, dependencies=[Depends(require_roles("admin", "supervisor"))])
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """A supervisor marks an alert as handled."""
    return alert_service.resolve_alert(db, alert_id)
