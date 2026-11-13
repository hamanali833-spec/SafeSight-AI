"""
Remove the black bars on the left and right of a video.

Why: YOLO shrinks every frame to 640 pixels wide. If half the frame is
black bars, the workers become tiny and helmets/vests are often missed.
Cropping the bars makes the people about twice as big for the model.

Run from the project root:
    python -m scripts.crop_video samples/site.mp4
"""
import sys
from pathlib import Path

import cv2
import numpy as np

BLACK_LEVEL = 16   # a column darker than this (on average) counts as black bar


def find_content(frame):
    """Return (x_start, x_end) of the part of the frame that is not black."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    column_brightness = gray.mean(axis=0)              # one number per column
    bright = np.where(column_brightness > BLACK_LEVEL)[0]
    return int(bright[0]), int(bright[-1]) + 1         # first and last real column


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.crop_video <video_path>")
        return
    path = Path(sys.argv[1])

    cap = cv2.VideoCapture(str(path))
    ok, first = cap.read()
    if not ok:
        print("Could not read video:", path)
        return

    # 1. Find the black bars using the first frame
    x1, x2 = find_content(first)
    h, w = first.shape[:2]
    print(f"Original: {w}x{h}  ->  content: x={x1}..{x2} ({x2 - x1}x{h})")

    # 2. Write every frame, cropped, to a new video
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    out_path = path.with_name(path.stem + "_cropped.mp4")
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"),
                             fps, (x2 - x1, h))

    frame, count = first, 0
    while ok:
        writer.write(frame[:, x1:x2])    # NumPy slicing: all rows, only the content columns
        count += 1
        ok, frame = cap.read()

    cap.release()
    writer.release()
    print(f"Frames written: {count}")
    print("Saved to:", out_path)


if __name__ == "__main__":
    main()

