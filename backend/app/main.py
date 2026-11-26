"""
SafeSight AI backend (FastAPI).

Easiest: from the project root run   python main.py
(or by hand: uvicorn app.main:app --reload --app-dir backend)
API docs: http://localhost:8000/docs
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, SessionLocal, engine
from app.models import alert, camera, user  # noqa: F401  (import so SQLAlchemy knows the tables)
from app.repositories.camera_repository import seed_defaults
from app.repositories.user_repository import seed_demo_users
from app.routers import alerts, auth, cameras, stats, videos, zones

# Create tables that don't exist yet (simple setup; production would use migrations)
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_defaults(db)      # three example cameras on the first start
    seed_demo_users(db)    # admin / supervisor / guard demo accounts on the first start

app = FastAPI(title="SafeSight AI API", version="0.1.0")
app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(cameras.router)
app.include_router(stats.router)
app.include_router(videos.router)
app.include_router(zones.router)


@app.get("/api/health")
def health():
    """Quick check that the server is running."""
    return {"status": "ok"}


# The built React app (frontend/dist, made by "npm run build") is served by this
# same server, so ONE command and ONE port run the whole website.
# Mounted last: every /api/... route above is matched first.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if (FRONTEND_DIST / "index.html").exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
