"""
Split a 2x2 CCTV grid video (4 cameras on one screen) into 4 separate videos.

Why: an NVR/DVR screen shows several cameras at once. If we run the model on
the whole grid, the same person appears in several tiles, gets several IDs,
and every person is 4x smaller. Real systems process each camera stream
separately, so we do the same.

Run from the project root:
    python -m scripts.split_grid samples/shop_grid.mp4
Output: samples/shop_grid_cam1.mp4 ... cam4.mp4
    cam1 = top-left, cam2 = top-right, cam3 = bottom-left, cam4 = bottom-right
"""
import sys
from pathlib import Path

import cv2
import numpy as np


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.split_grid <video_path>")
        return
    path = Path(sys.argv[1])

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():                     # file missing or not a video -> stop early
        print("Could not open video:", path)
        return

    # Read the first frame and take the size from the REAL frame,
    # not from the file's metadata (screen recordings sometimes report it wrong)
    ok, frame = cap.read()
    if not ok:
        print("Video has no frames:", path)
        return
    h, w = frame.shape[:2]

    # Tile size, rounded down to an even number (video encoders prefer even sizes)
    half_w = (w // 2) // 2 * 2
    half_h = (h // 2) // 2 * 2

    # (x, y) of each tile's top-left corner
    tiles = {
        "cam1": (0, 0),
        "cam2": (half_w, 0),
        "cam3": (0, half_h),
        "cam4": (half_w, half_h),
    }

    # One video writer per tile
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writers = {
        name: cv2.VideoWriter(str(path.with_name(f"{path.stem}_{name}.mp4")),
                              fourcc, fps, (half_w, half_h))
        for name in tiles
    }

    count = 0
    while ok:
        for name, (x, y) in tiles.items():
            tile = frame[y:y + half_h, x:x + half_w]          # cut out one tile
            writers[name].write(np.ascontiguousarray(tile))   # give OpenCV one solid block of memory
        count += 1
        ok, frame = cap.read()

    cap.release()
    for writer in writers.values():
        writer.release()

    print(f"Original: {w}x{h}  ->  4 tiles of {half_w}x{half_h}, {count} frames each")
    for name in tiles:
        print("Saved:", path.with_name(f"{path.stem}_{name}.mp4"))


if __name__ == "__main__":
    main()