"""
Run the full pipeline on one image:
    image -> detector (ONNX) -> rule engine -> picture with a decision on each person

Run from the project root:
    python -m scripts.run_rules samples/helmet_worker.jpg
"""
import sys
from pathlib import Path

import cv2

from inference.detector import PPEDetector
from decision_engine.ppe_rules import evaluate, SAFE, PARTIAL, HIGH, REVIEW

# Box colors per severity. OpenCV uses BGR order, not RGB!
COLORS = {
    SAFE:    (0, 200, 0),     # green
    PARTIAL: (0, 165, 255),   # orange
    HIGH:    (0, 0, 255),     # red
    REVIEW:  (0, 220, 220),   # yellow
}
OUTPUT_DIR = Path("outputs/rules")


def draw(image, statuses):
    """Draw one colored box and a label on each person."""
    for s in statuses:
        x1, y1, x2, y2 = map(int, s.person.box)
        color = COLORS[s.severity]

        # Person box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)

        # Label with a filled background so it's readable
        # Show the track ID when we have one (videos), nothing for single images
        prefix = f"ID {s.person.track_id} | " if s.person.track_id is not None else ""
        label = f"{prefix}{s.severity} | helmet:{s.helmet} vest:{s.vest}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(y1, th + 8)   # keep the label inside the image at the top edge
        cv2.rectangle(image, (x1, top - th - 8), (x1 + tw + 6, top), color, -1)
        cv2.putText(image, label, (x1 + 3, top - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    return image


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_rules <image_path>")
        return

    path = Path(sys.argv[1])
    image = cv2.imread(str(path))           # load the image as a NumPy array (BGR)
    if image is None:
        print("Could not read image:", path)
        return

    # 1. Detect objects
    detector = PPEDetector()
    detections = detector.detect(image)

    # 2. Apply the rules
    statuses = evaluate(detections)

    # 3. Print the decision for each person
    print(f"People found: {len(statuses)}")
    for i, s in enumerate(statuses, start=1):
        print(f"  Person {i}: {s.severity:<8} helmet={s.helmet:<8} vest={s.vest}")

    # 4. Save the picture
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / path.name
    cv2.imwrite(str(out_path), draw(image, statuses))
    print("Saved to:", out_path)


if __name__ == "__main__":
    main()


