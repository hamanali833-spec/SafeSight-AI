"""
Restricted zones: is a person standing inside a forbidden area?

A zone is a polygon (a list of corner points) drawn on the camera image.
We use the person's FEET (bottom-center of their box), not the box center,
because feet show where a person is actually standing on the floor.
"""
import json
from dataclasses import replace
from pathlib import Path

from decision_engine.ppe_rules import SAFE, HIGH


def feet_point(box):
    """Bottom-center of a box: where the person stands."""
    x1, y1, x2, y2 = box
    return (x1 + x2) / 2, y2


def point_in_polygon(point, polygon):
    """
    Ray casting: draw a line from the point to the right and count how many
    polygon edges it crosses. Odd number of crossings = inside, even = outside.
    """
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]          # next corner (wraps around to the first)
        crosses = (y1 > y) != (y2 > y)         # this edge goes across the point's height
        if crosses:
            # x position where the edge crosses that height
            x_cross = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < x_cross:
                inside = not inside
    return inside


def zone_statuses(statuses, zones):
    """
    Turn PPE statuses into ZONE statuses for the alert engine:
    HIGH if the person's feet are inside any restricted zone, otherwise SAFE.
    Returns copies; the original PPE statuses are not changed.
    """
    result = []
    for s in statuses:
        feet = feet_point(s.person.box)
        inside = any(point_in_polygon(feet, z["points"]) for z in zones)
        result.append(replace(s, severity=HIGH if inside else SAFE))
    return result


def load_zones(path):
    """Read zones saved by scripts/draw_zone.py. Returns [] if there is no file."""
    path = Path(path)
    if not path.exists():
        return []
    return json.loads(path.read_text())

