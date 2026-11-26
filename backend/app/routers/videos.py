"""
Video endpoints: upload a video for one camera, follow its progress,
and get the latest processed frame for the live preview.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.auth import current_user, require_roles
from app.core.database import get_db
from app.repositories import camera_repository as cameras
from app.services import video_service

router = APIRouter(prefix="/api/videos", tags=["videos"])

ALLOWED = (".mp4", ".avi", ".mov", ".mkv", ".webm")
MAX_MB = 200


@router.post("", status_code=202, dependencies=[Depends(require_roles("admin", "supervisor"))])
async def upload_video(file: UploadFile, background: BackgroundTasks,
                       camera_id: str = Form(...), db: Session = Depends(get_db)):
    """Save the video and start processing it for this camera (202 = accepted, still working)."""
    camera = cameras.get_camera(db, camera_id)
    if camera is None:
        raise HTTPException(404, "Unknown camera")
    if not file.filename or not file.filename.lower().endswith(ALLOWED):
        raise HTTPException(400, f"Please upload a video file: {', '.join(ALLOWED)}")
    reason = video_service.busy_reason(camera_id)
    if reason:
        raise HTTPException(409, reason)
    data = await file.read()
    if len(data) > MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"Video is larger than {MAX_MB} MB")
    job = video_service.create_job(camera_id, file.filename, data, camera.ppe_required)
    background.add_task(video_service.run_job, job["id"])   # runs in its own thread
    return job


@router.get("/{job_id}", dependencies=[Depends(current_user)])
def job_status(job_id: str):
    job = video_service.get_job(job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/{job_id}/frame", dependencies=[Depends(current_user)])
def latest_frame(job_id: str):
    """The most recent processed frame, with boxes and zones drawn on it."""
    path = video_service.preview_path(job_id)
    if not path.exists():
        raise HTTPException(404, "No preview yet")
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "no-store"})
