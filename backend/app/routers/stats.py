"""Analytics endpoint for the dashboard's charts."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import current_user
from app.core.database import get_db
from app.schemas.stats import Stats
from app.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=Stats, dependencies=[Depends(current_user)])
def get_stats(db: Session = Depends(get_db)):
    return stats_service.get_stats(db)
