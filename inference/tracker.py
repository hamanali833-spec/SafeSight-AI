"""
Tracker: runs detection + ByteTrack one frame at a time.

Detection alone looks at each frame separately.
Tracking links boxes across frames, so the same worker keeps the same ID.
Each camera gets its OWN PPETracker, so IDs never mix between cameras.
"""
from pathlib import Path

import cv2
from ultralytics import YOLO

from decision_engine.ppe_rules import Detection

DEFAULT_WEIGHTS = Path("ppe-detection/weights/best.onnx")


class PPETracker:
    def __init__(self, weights=DEFAULT_WEIGHTS, conf=0.4):
        # Load the model once and reuse it for every frame of this camera
        self.model = YOLO(str(weights), task="detect")
        self.conf = conf

    def track(self, frame):
        """
        frame: one image (BGR, from OpenCV)
        returns: list of Detection with a track_id that stays the same across frames
        """
        result = self.model.track(
            frame,
            conf=self.conf,
            tracker="bytetrack.yaml",  # the tracking algorithm
            persist=True,              # remember tracks from the previous call (frame)
            verbose=False,
        )[0]

        ids = result.boxes.id          # None until the tracker has confirmed a track
        detections = []
        for j, box in enumerate(result.boxes):
            detections.append(Detection(
                name=self.model.names[int(box.cls)],
                conf=float(box.conf),
                box=tuple(float(v) for v in box.xyxy[0].tolist()),
                track_id=int(ids[j]) if ids is not None else None,
            ))
        return detections

    def track_video(self, source, vid_stride=1):
        """Older helper: yields (frame, detections) for every vid_stride-th frame of a file."""
        cap = cv2.VideoCapture(str(source))
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % vid_stride == 0:
                yield frame, self.track(frame)
            i += 1
        cap.release()
