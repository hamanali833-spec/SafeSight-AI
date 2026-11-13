"""
Tracker: runs detection + ByteTrack on a video.

Detection alone looks at each frame separately.
Tracking links boxes across frames, so the same worker
keeps the same ID for the whole video.
"""
from pathlib import Path

from ultralytics import YOLO

from decision_engine.ppe_rules import Detection

DEFAULT_WEIGHTS = Path("ppe-detection/weights/best.onnx")


class PPETracker:
    def __init__(self, weights=DEFAULT_WEIGHTS, conf=0.4):
        # Load the model once and reuse it for every frame
        self.model = YOLO(str(weights), task="detect")
        self.conf = conf

    def track_video(self, source, vid_stride=1):
        """
        Yields (frame, detections) for each processed frame.
        vid_stride=2 processes every 2nd frame (faster on a slow laptop).
        """
        results = self.model.track(
            source,
            conf=self.conf,
            tracker="bytetrack.yaml",  # the tracking algorithm
            persist=True,              # keep IDs between frames
            stream=True,               # one frame at a time -> low memory use
            vid_stride=vid_stride,
            verbose=False,
        )

        for r in results:
            ids = r.boxes.id  # None if the tracker has no IDs yet in this frame
            detections = []
            for j, box in enumerate(r.boxes):
                detections.append(Detection(
                    name=self.model.names[int(box.cls)],
                    conf=float(box.conf),
                    box=tuple(float(v) for v in box.xyxy[0].tolist()),
                    track_id=int(ids[j]) if ids is not None else None,
                ))
            yield r.orig_img, detections   # orig_img = the original frame (BGR)

