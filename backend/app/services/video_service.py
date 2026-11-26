"""
Video jobs, one per camera: save the uploaded file, run the SafeSight pipeline
in the background, and keep track of progress so the dashboard can show it.

Several cameras can run at the same time (one thread each, at most MAX_PARALLEL).
Jobs are kept in memory, which is fine for one laptop; a production system
would use a job queue (e.g. Celery + Redis) and store jobs in the database.
"""
import sys
import threading
import uuid
from pathlib import Path

import cv2

# The ML code (inference/, decision_engine/, scripts/) lives in the project root,
# one level above backend/. Make it importable from here.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference.pipeline import process_video            # noqa: E402
from scripts.alert_client import MESSAGES                # noqa: E402

from app.core.database import SessionLocal               # noqa: E402
from app.repositories import alert_repository as alerts  # noqa: E402

JOBS_DIR = PROJECT_ROOT / "outputs" / "jobs"
ZONES_DIR = PROJECT_ROOT / "zones"
MAX_PARALLEL = 3    # cameras processed at the same time on one laptop
STRIDE = 3          # every 3rd frame per camera, so three cameras fit on one CPU
PREVIEW_EVERY = 3   # save a preview image every 3 processed frames

_jobs: dict[str, dict] = {}
_lock = threading.Lock()   # pipeline threads and API requests all touch _jobs


def get_job(job_id: str) -> dict | None:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def _running(job) -> bool:
    return job["status"] in ("queued", "processing")


def busy_reason(camera_id: str) -> str | None:
    """Why a new job can't start now, or None if it can."""
    with _lock:
        running = [j for j in _jobs.values() if _running(j)]
    if any(j["cameraId"] == camera_id for j in running):
        return "This camera is already processing a video."
    if len(running) >= MAX_PARALLEL:
        return f"{MAX_PARALLEL} cameras are already processing. Please wait."
    return None


def create_job(camera_id: str, filename: str, data: bytes, ppe_required: bool) -> dict:
    """Save the upload in its own folder and register a new job for this camera."""
    job_id = uuid.uuid4().hex[:8]
    folder = JOBS_DIR / job_id
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name or "upload.mp4"   # drop any folder parts from the name
    (folder / safe_name).write_bytes(data)
    job = {"id": job_id, "cameraId": camera_id, "filename": safe_name, "status": "queued",
           "progress": 0, "ppeAlerts": 0, "zoneAlerts": 0, "ppeRequired": ppe_required,
           "hasZones": (ZONES_DIR / f"{camera_id}.json").exists(), "error": None}
    with _lock:
        _jobs[job_id] = job
    return dict(job)


def _update(job_id: str, **fields):
    with _lock:
        _jobs[job_id].update(fields)


def _increment(job_id: str, key: str):
    with _lock:
        _jobs[job_id][key] += 1


def run_job(job_id: str):
    """Runs in its own background thread after the upload request has returned."""
    job = get_job(job_id)
    folder = JOBS_DIR / job_id
    camera_id = job["cameraId"]
    zones_path = ZONES_DIR / f"{camera_id}.json"     # this camera's restricted zone
    preview = folder / "latest.jpg"
    _update(job_id, status="processing")

    def on_alert(alert, kind):
        # Save straight into the database (we are inside the backend, no HTTP needed)
        db = SessionLocal()
        try:
            alerts.create_alert(db, {
                "camera_id": camera_id, "track_id": alert.track_id, "kind": kind,
                "severity": alert.severity,
                "message": MESSAGES.get((kind, alert.severity), kind + " alert"),
            })
        finally:
            db.close()
        _increment(job_id, "zoneAlerts" if kind == "ZONE" else "ppeAlerts")

    frame_no = {"n": 0}

    def on_frame(frame):
        frame_no["n"] += 1
        if frame_no["n"] % PREVIEW_EVERY:
            return
        # Smaller preview image, written to a temp file then swapped in,
        # so the browser never reads a half-written picture
        scale = 640 / frame.shape[1]
        small = cv2.resize(frame, None, fx=scale, fy=scale)
        tmp = folder / "latest_tmp.jpg"
        cv2.imwrite(str(tmp), small)
        try:
            tmp.replace(preview)
        except PermissionError:
            pass   # Windows: the browser is reading the old image right now; skip this one

    def on_progress(done, total):
        _update(job_id, progress=round(100 * done / total))

    try:
        process_video(folder / job["filename"],
                      zones_path=zones_path if zones_path.exists() else None,
                      ppe_required=job["ppeRequired"], vid_stride=STRIDE,
                      on_alert=on_alert, on_frame=on_frame, on_progress=on_progress)
        _update(job_id, status="done", progress=100)
    except Exception as error:   # report any failure to the dashboard instead of crashing
        _update(job_id, status="failed", error=str(error))


def preview_path(job_id: str) -> Path:
    return JOBS_DIR / job_id / "latest.jpg"
