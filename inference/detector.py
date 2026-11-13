"""
Detector: wraps the YOLO model and returns plain Detection objects.

The rest of the system (rule engine, backend) never talks to Ultralytics
directly. If we change the model or the format later (PyTorch, ONNX,
a newer YOLO), only this file changes.
"""
from pathlib import Path

from ultralytics import YOLO

from decision_engine.ppe_rules import Detection

# We use ONNX because our benchmark showed it is faster on this CPU (33 ms vs 39 ms)
DEFAULT_WEIGHTS = Path("ppe-detection/weights/best.onnx")


class PPEDetector:
    def __init__(self, weights=DEFAULT_WEIGHTS, conf=0.4):
        # Load the model once. Loading is slow, so we never reload it per image.
        self.model = YOLO(str(weights), task="detect")
        self.conf = conf  # minimum confidence to keep a box

    def detect(self, image):
        """
        image: a file path or an image already loaded with OpenCV
        returns: list of Detection(name, conf, box)
        """
        result = self.model.predict(image, conf=self.conf, verbose=False)[0]

        detections = []
        for box in result.boxes:
            detections.append(Detection(
                name=self.model.names[int(box.cls)],                  # class number -> name
                conf=float(box.conf),                                 # tensor -> plain number
                box=tuple(float(v) for v in box.xyxy[0].tolist()),    # (x1, y1, x2, y2)
            ))
        return detections


