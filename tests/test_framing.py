"""Tests for black-bar cropping and zone shifting (no model needed)."""
import numpy as np

from inference.framing import find_content_x, shift_zones


def test_finds_picture_between_black_bars():
    frame = np.zeros((100, 300, 3), dtype=np.uint8)
    frame[:, 80:220] = 120                         # the real picture
    assert find_content_x(frame) == (80, 220)


def test_frame_without_bars_is_kept_whole():
    frame = np.full((50, 200, 3), 90, dtype=np.uint8)
    assert find_content_x(frame) == (0, 200)


def test_zone_moves_with_the_crop():
    zones = [{"name": "Z", "points": [[600, 100], [700, 100], [700, 200]]}]
    assert shift_zones(zones, 510)[0]["points"] == [[90, 100], [190, 100], [190, 200]]
