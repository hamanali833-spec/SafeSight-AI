"""
Restricted zone endpoints: the dashboard draws a zone on a camera image and saves it here.
Each camera (video name) has one JSON file in zones/, the same format scripts/draw_zone.py writes.
"""
import json
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.auth import current_user, require_roles

router = APIRouter(prefix="/api/zones", tags=["zones"])

ZONES_DIR = Path(__file__).resolve().parents[3] / "zones"
# Only letters, digits, _ and - : stops names like "../../secret" (path traversal)
CAMERA_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class ZoneIn(BaseModel):
    name: str = Field("Restricted zone", max_length=50)
    points: list[tuple[int, int]] = Field(min_length=3, max_length=50)   # a polygon needs 3+ corners


def zone_path(camera_id: str) -> Path:
    if not CAMERA_ID.match(camera_id):
        raise HTTPException(400, "Camera ID may only contain letters, digits, _ and -")
    return ZONES_DIR / f"{camera_id}.json"


@router.get("", dependencies=[Depends(current_user)])
def list_zones():
    """Every camera that has a zone, with its polygons."""
    if not ZONES_DIR.exists():
        return []
    return [{"cameraId": f.stem, "zones": json.loads(f.read_text())}
            for f in sorted(ZONES_DIR.glob("*.json"))]


@router.get("/{camera_id}", dependencies=[Depends(current_user)])
def get_zone(camera_id: str):
    path = zone_path(camera_id)
    if not path.exists():
        raise HTTPException(404, "No zone for this camera")
    return {"cameraId": camera_id, "zones": json.loads(path.read_text())}


@router.put("/{camera_id}", dependencies=[Depends(require_roles("admin"))])
def save_zone(camera_id: str, zone: ZoneIn):
    """Create or replace the restricted zone for one camera."""
    path = zone_path(camera_id)
    ZONES_DIR.mkdir(exist_ok=True)
    data = [{"name": zone.name, "points": [list(p) for p in zone.points]}]
    path.write_text(json.dumps(data, indent=2))
    return {"cameraId": camera_id, "zones": data}


@router.delete("/{camera_id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_zone(camera_id: str):
    path = zone_path(camera_id)
    if not path.exists():
        raise HTTPException(404, "No zone for this camera")
    path.unlink()
