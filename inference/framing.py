"""
Frame helpers used before the model sees a frame.

Many CCTV exports have black bars on the left and right. YOLO shrinks every
frame to 640 px wide, so bars make people smaller and harder to detect.
We find the real picture once, crop every frame to it, and move the
restricted-zone corners by the same offset so they still line up.
"""
import numpy as np

BLACK_LEVEL = 16   # a column darker than this (on average) counts as black bar


def find_content_x(frame):
    """Return (x_start, x_end) of the non-black part of a frame (BGR image)."""
    gray = frame.mean(axis=2)                    # rough brightness per pixel
    column_brightness = gray.mean(axis=0)        # one number per column
    bright = np.where(column_brightness > BLACK_LEVEL)[0]
    if len(bright) == 0:                         # an all-black frame: keep it whole
        return 0, frame.shape[1]
    return int(bright[0]), int(bright[-1]) + 1


def shift_zones(zones, dx):
    """Move every zone corner left by dx pixels (the width cut off on the left)."""
    return [{**z, "points": [[x - dx, y] for x, y in z["points"]]} for z in zones]
