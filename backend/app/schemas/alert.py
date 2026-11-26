"""
Pydantic schemas: the shape of data going IN and OUT of the API.
They validate input (wrong severity -> 422 error) and hide database details.
JSON keys are camelCase for the React frontend (cameraId, createdAt ...).
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    # Accept snake_case or camelCase on input, send camelCase on output
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class AlertCreate(CamelModel):
    """What the video pipeline sends when it raises an alert."""
    camera_id: str
    track_id: int
    kind: Literal["PPE", "ZONE"]
    severity: Literal["REVIEW", "PARTIAL", "HIGH"]
    message: str


class AlertOut(AlertCreate):
    """What the API returns: the input plus fields the server adds."""
    id: int
    created_at: datetime
    resolved: bool
