"""
Unit tests for restricted zones (no model, no video).
Run with:  python -m pytest -v
"""
from decision_engine.ppe_rules import Detection, PersonStatus, SAFE, HIGH
from decision_engine.zones import feet_point, point_in_polygon, zone_statuses

# A square zone from (100, 100) to (300, 300)
SQUARE = [(100, 100), (300, 100), (300, 300), (100, 300)]
ZONES = [{"name": "Machine area", "points": SQUARE}]


def person(box):
    return PersonStatus(person=Detection("person", 0.9, box, track_id=1), severity=SAFE)


def test_feet_point_is_bottom_center():
    assert feet_point((100, 50, 200, 250)) == (150, 250)


def test_point_inside_square():
    assert point_in_polygon((200, 200), SQUARE)


def test_point_outside_square():
    assert not point_in_polygon((50, 200), SQUARE)
    assert not point_in_polygon((200, 400), SQUARE)


def test_point_inside_l_shaped_zone():
    # An L shape: the corner area (250, 250) is outside, (150, 250) is inside
    l_shape = [(100, 100), (200, 100), (200, 200), (300, 200), (300, 300), (100, 300)]
    assert point_in_polygon((150, 250), l_shape)
    assert not point_in_polygon((250, 150), l_shape)


def test_person_with_feet_in_zone_is_high():
    # Head outside the zone, feet inside -> counts as inside
    s = zone_statuses([person((180, 20, 220, 200))], ZONES)[0]
    assert s.severity == HIGH


def test_person_outside_zone_is_safe():
    s = zone_statuses([person((400, 100, 450, 250))], ZONES)[0]
    assert s.severity == SAFE
