"""
Camera endpoints: list the cameras and change their settings
(display name, and whether helmets and vests are required there).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import current_user, require_roles
from app.core.database import get_db
from app.repositories import camera_repository as repo
from app.routers.zones import zone_path
from app.schemas.camera import CameraIn, CameraOut

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


def _out(cam) -> CameraOut:
    return CameraOut(id=cam.id, name=cam.name, ppe_required=cam.ppe_required,
                     has_zone=zone_path(cam.id).exists())


@router.get("", response_model=list[CameraOut], dependencies=[Depends(current_user)])
def list_cameras(db: Session = Depends(get_db)):
    return [_out(c) for c in repo.list_cameras(db)]


@router.put("/{camera_id}", response_model=CameraOut, dependencies=[Depends(require_roles("admin"))])
def save_camera(camera_id: str, camera: CameraIn, db: Session = Depends(get_db)):
    zone_path(camera_id)          # checks the id is safe (letters, digits, _ and -)
    return _out(repo.upsert_camera(db, camera_id, camera.name, camera.ppe_required))
