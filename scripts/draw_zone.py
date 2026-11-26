"""
Draw a restricted zone on the first frame of a video and save it.

Run from the project root:
    python -m scripts.draw_zone samples/site_cropped.mp4

Controls (click on the image window first):
    Left click  -> add a corner
    Z           -> undo the last corner
    R           -> reset (start again)
    S           -> save and exit (needs at least 3 corners)
    Q           -> quit without saving

The zone is saved to zones/<video name>.json, in ORIGINAL video pixels.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ZONES_DIR = Path("zones")
MAX_SCREEN_HEIGHT = 800   # shrink big videos so the window fits on a laptop screen


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.draw_zone <video_path>")
        return
    path = Path(sys.argv[1])

    # 1. Grab the first frame of the video
    cap = cv2.VideoCapture(str(path))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        print("Could not read video:", path)
        return

    # 2. Scale for display only; clicks are converted back to original pixels
    scale = min(1.0, MAX_SCREEN_HEIGHT / frame.shape[0])
    shown = cv2.resize(frame, None, fx=scale, fy=scale)
    points = []   # corners in ORIGINAL pixels

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((int(x / scale), int(y / scale)))

    window = "Draw restricted zone  |  click corners, S = save, Z = undo, R = reset, Q = quit"
    cv2.namedWindow(window)
    cv2.setMouseCallback(window, on_mouse)

    # 3. Redraw the picture with the current corners until the user saves or quits
    while True:
        canvas = shown.copy()
        pts = np.array([(int(px * scale), int(py * scale)) for px, py in points], np.int32)
        if len(points) >= 3:
            overlay = canvas.copy()
            cv2.fillPoly(overlay, [pts], (0, 0, 255))
            canvas = cv2.addWeighted(overlay, 0.3, canvas, 0.7, 0)   # 30% transparent red
        if len(points) >= 2:
            cv2.polylines(canvas, [pts], isClosed=len(points) >= 3, color=(0, 0, 255), thickness=2)
        for p in pts:
            cv2.circle(canvas, tuple(int(v) for v in p), 5, (0, 255, 255), -1)

        cv2.imshow(window, canvas)
        key = cv2.waitKey(30) & 0xFF

        if key == ord("z") and points:
            points.pop()
        elif key == ord("r"):
            points.clear()
        elif key == ord("q"):
            print("Quit without saving.")
            break
        elif key == ord("s"):
            if len(points) < 3:
                print("A zone needs at least 3 corners.")
                continue
            ZONES_DIR.mkdir(exist_ok=True)
            out = ZONES_DIR / f"{path.stem}.json"
            zones = [{"name": "Restricted zone", "points": points}]
            out.write_text(json.dumps(zones, indent=2))
            print(f"Saved zone with {len(points)} corners to: {out}")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

