"""Shapes of camera data going in and out of the API (camelCase JSON)."""
from pydantic import Field

from app.schemas.alert import CamelModel


class CameraIn(CamelModel):
    name: str = Field(min_length=1, max_length=60)
    ppe_required: bool = True


class CameraOut(CameraIn):
    id: str
    has_zone: bool = False   # filled in by the router from zones/<id>.json
