"""Run the trained PPE detector on one image and save the result."""
import sys
from pathlib import Path

import cv2
from ultralytics import YOLO

WEIGHTS = Path("ppe-detection/weights/best.pt")
OUTPUT_DIR = Path("outputs/test")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_inference.py <image_path>")
        return

    source = Path(sys.argv[1])
    model = YOLO(WEIGHTS)
    print("Classes:", model.names)

    # save=False: Ultralytics khud kuch save na kare
    results = model.predict(str(source), conf=0.4, save=False, verbose=False)
    result = results[0]

    # Har detection print karo
    for box in result.boxes:
        name = model.names[int(box.cls)]
        print(f"{name:<10} conf={float(box.conf):.2f}")

    # Speed print karo (milliseconds)
    s = result.speed
    print(f"Speed: preprocess {s['preprocess']:.1f} ms, "
          f"inference {s['inference']:.1f} ms, postprocess {s['postprocess']:.1f} ms")

    # Boxes wali image khud save karo
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / source.name
    cv2.imwrite(str(out_path), result.plot())
    print("Saved to:", out_path)


if __name__ == "__main__":
    main()
    