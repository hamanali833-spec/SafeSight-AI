"""The only place that reads and writes the cameras table."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.camera import Camera

# Created on first start so the dashboard has three cameras to work with
DEFAULT_CAMERAS = [
    ("warehouse", "Warehouse", True),
    ("office", "Office", True),
    ("site", "Site gate", True),
]


def seed_defaults(db: Session):
    if db.scalar(select(Camera).limit(1)) is None:
        db.add_all(Camera(id=i, name=n, ppe_required=p) for i, n, p in DEFAULT_CAMERAS)
        db.commit()


def list_cameras(db: Session) -> list[Camera]:
    order = {cid: i for i, (cid, _, _) in enumerate(DEFAULT_CAMERAS)}
    return sorted(db.scalars(select(Camera)), key=lambda c: (order.get(c.id, 99), c.id))


def get_camera(db: Session, camera_id: str) -> Camera | None:
    return db.get(Camera, camera_id)


def upsert_camera(db: Session, camera_id: str, name: str, ppe_required: bool) -> Camera:
    cam = db.get(Camera, camera_id) or Camera(id=camera_id)
    cam.name, cam.ppe_required = name, ppe_required
    db.add(cam)
    db.commit()
    db.refresh(cam)
    return cam
