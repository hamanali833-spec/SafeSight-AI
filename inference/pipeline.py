"""
The full SafeSight video pipeline for ONE camera, as one reusable function.

    video -> crop black bars -> tracker (ONNX + ByteTrack) -> PPE rules + restricted zones
          -> alert engines -> annotated frames

Used by the command-line script (scripts/run_video.py) and by the backend,
which runs one process_video() per camera, side by side. What happens to
alerts, frames and progress is decided by the caller through callbacks.
"""
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np

from inference.framing import find_content_x, shift_zones
from inference.tracker import PPETracker
from decision_engine.ppe_rules import evaluate, drop_small_people, HIGH
from decision_engine.alerts import AlertEngine
from decision_engine.zones import load_zones, zone_statuses, feet_point
from scripts.run_rules import draw   # same drawing code as for images

VID_STRIDE = 2          # process every 2nd frame to keep the laptop fast
MIN_PERSON_RATIO = 0.2  # PPE is only judged for people at least 20% of the frame height


def draw_zones(frame, zones, occupied):
    """Draw each zone: red fill if someone is inside, yellow outline if empty."""
    overlay = frame.copy()
    for z in zones:
        pts = np.array(z["points"], np.int32)
        if occupied:
            cv2.fillPoly(overlay, [pts], (0, 0, 255))
        cv2.polylines(frame, [pts], True, (0, 0, 255) if occupied else (0, 220, 220), 3)
        x, y = z["points"][0]
        cv2.putText(frame, z["name"], (x + 5, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    return cv2.addWeighted(overlay, 0.25, frame, 0.75, 0)


def draw_people(frame, statuses):
    """Cameras where PPE is not required: a plain white box and the person's ID."""
    for s in statuses:
        x1, y1, x2, y2 = map(int, s.person.box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (235, 235, 235), 2)
        if s.person.track_id is not None:
            cv2.putText(frame, f"ID {s.person.track_id}", (x1 + 4, max(20, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (235, 235, 235), 2)
    return frame


def process_video(video_path, zones_path=None, output_path=None, ppe_required=True,
                  vid_stride=VID_STRIDE, on_alert=None, on_frame=None, on_progress=None):
    """
    Run the pipeline on one camera's video.

    zones_path:    JSON file with this camera's restricted zone (optional)
    ppe_required:  False for cameras where helmets and vests are not needed (no PPE alerts)
    vid_stride:    process every n-th frame (3 when several cameras run at once)
    on_alert(alert, kind):     called for every confirmed alert ("PPE" or "ZONE")
    on_frame(frame):           called with each drawn frame (live preview)
    on_progress(done, total):  called after each processed frame
    Returns a summary dict.
    """
    video_path = Path(video_path)
    zones = load_zones(zones_path) if zones_path else []

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path.name}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) // vid_stride)

    tracker = PPETracker()           # one tracker per camera: IDs never mix between cameras
    ppe_engine = AlertEngine(min_track_s=1.0, confirm_s=2.0, cooldown_s=30.0)
    zone_engine = AlertEngine(min_track_s=1.0, confirm_s=1.0, cooldown_s=30.0)
    history = defaultdict(Counter)   # track_id -> how many frames in each PPE status
    counts = {"PPE": 0, "ZONE": 0}
    writer, crop, frame_index, done = None, None, 0, 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index % vid_stride:            # skip frames we don't process
            frame_index += 1
            continue

        # 1. Crop black bars (found once, on the first frame) and move the zones to match
        if crop is None:
            crop = find_content_x(frame)
            zones = shift_zones(zones, crop[0])
        frame = np.ascontiguousarray(frame[:, crop[0]:crop[1]])
        now = frame_index / fps                  # time of this frame in seconds
        frame_index += 1

        # 2. Detect + track, then decide
        detections = tracker.track(frame)
        all_statuses = evaluate(detections)      # everyone, even far away: for zones
        statuses = evaluate(drop_small_people(detections, frame.shape[0], MIN_PERSON_RATIO))

        new_alerts = []
        if ppe_required:
            new_alerts += [(a, "PPE") for a in ppe_engine.update(statuses, now)]
        in_zone = zone_statuses(all_statuses, zones) if zones else []
        new_alerts += [(a, "ZONE") for a in zone_engine.update(in_zone, now)]
        for alert, kind in new_alerts:
            counts[kind] += 1
            if on_alert:
                on_alert(alert, kind)

        for s in statuses:
            if s.person.track_id is not None:
                history[s.person.track_id][s.severity] += 1

        # 3. Draw zones, people, and a marker on anyone inside a zone
        occupied = any(z.severity == HIGH for z in in_zone)
        if zones:
            frame = draw_zones(frame, zones, occupied)
        frame = draw(frame, statuses) if ppe_required else draw_people(frame, all_statuses)
        for z in in_zone:
            if z.severity == HIGH:
                fx, fy = map(int, feet_point(z.person.box))
                cv2.circle(frame, (fx, fy), 10, (0, 0, 255), -1)
                cv2.putText(frame, "UNAUTHORIZED", (fx - 70, fy + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # 4. Save / share the drawn frame
        if output_path:
            if writer is None:
                h, w = frame.shape[:2]
                writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"),
                                         fps / vid_stride, (w, h))
            writer.write(frame)
        if on_frame:
            on_frame(frame)
        done += 1
        if on_progress:
            on_progress(done, max(total, done))

    cap.release()
    if writer:
        writer.release()   # finish the file, otherwise the video may not open

    return {
        "frames": done,
        "seconds": round(frame_index / fps, 1),
        "people": {tid: dict(c) for tid, c in history.items()},
        "ppe_alerts": counts["PPE"],
        "zone_alerts": counts["ZONE"],
    }
