"""
PPE rule engine: turns raw model detections into a safety decision per person.

There is NO machine learning in this file.
The model only says "there is a helmet at (x1, y1, x2, y2)".
This file decides WHICH person that helmet belongs to,
and HOW serious each person's violation is.

It does not import Ultralytics, so it can be tested without the model
and reused with any detector (PyTorch, ONNX, or something else).
"""
from dataclasses import dataclass

# ---- Severity levels ----
SAFE = "SAFE"        # helmet and vest both detected
PARTIAL = "PARTIAL"  # one item missing
HIGH = "HIGH"        # both items missing
REVIEW = "REVIEW"    # nothing missing, but something was not visible -> a human should check

# ---- What each PPE class means ----
# class name -> (which slot it fills, what it says about that slot)
ITEM_RULES = {
    "helmet":    ("helmet", "ok"),
    "no_helmet": ("helmet", "missing"),
    "vest":      ("vest", "ok"),
    "no_vest":   ("vest", "missing"),
}


@dataclass
class Detection:
    """One box from the model."""
    name: str    # class name, e.g. "helmet"
    conf: float  # confidence between 0 and 1
    box: tuple   # (x1, y1, x2, y2) in pixels: top-left and bottom-right corners
    track_id: int | None = None  # same number for the same object across frames (None for single images)


@dataclass
class PersonStatus:
    """The final decision for one person."""
    person: Detection
    helmet: str = "unknown"  # "ok", "missing" or "unknown"
    vest: str = "unknown"
    severity: str = REVIEW


def _center(box):
    """Middle point of a box."""
    x1, y1, x2, y2 = box
    return (x1 + x2) / 2, (y1 + y2) / 2


def _contains(person_box, point, margin=0.1):
    """
    Is the point inside the person's box?
    The box is made 10% bigger on each side, because a helmet
    often sticks out a little above the detected person.
    """
    x1, y1, x2, y2 = person_box
    w, h = x2 - x1, y2 - y1
    px, py = point
    return (x1 - margin * w <= px <= x2 + margin * w and
            y1 - margin * h <= py <= y2 + margin * h)


def _owner(item, persons):
    """
    Find the index of the person this PPE item belongs to.
    Rule: the item's center must be inside the person's box.
    If several people qualify (they overlap), pick the person
    whose center is closest to the item.
    Returns None if the item is not on anyone (e.g. a helmet on a table).
    """
    cx, cy = _center(item.box)
    best_index, best_distance = None, float("inf")
    for i, person in enumerate(persons):
        if not _contains(person.box, (cx, cy)):
            continue
        px, py = _center(person.box)
        distance = (cx - px) ** 2 + (cy - py) ** 2
        if distance < best_distance:
            best_index, best_distance = i, distance
    return best_index


def _severity(helmet, vest):
    """Turn the two slot values into one severity level."""
    missing = [helmet, vest].count("missing")
    if missing == 2:
        return HIGH
    if missing == 1:
        return PARTIAL
    if "unknown" in (helmet, vest):
        return REVIEW
    return SAFE


def evaluate(detections):
    """
    Main function: list of Detection -> list of PersonStatus (one per person).
    """
    # 1. Separate people from PPE items
    persons = [d for d in detections if d.name == "person"]
    results = [PersonStatus(person=p) for p in persons]

    # Best confidence seen so far for each person's helmet and vest slot.
    # If the model sees BOTH "helmet" and "no_helmet" on one person,
    # we trust the one with higher confidence.
    best_conf = [{"helmet": 0.0, "vest": 0.0} for _ in persons]

    # 2. Give every PPE item to its owner
    for det in detections:
        if det.name not in ITEM_RULES:
            continue                      # not a PPE class (e.g. "person")
        slot, value = ITEM_RULES[det.name]
        i = _owner(det, persons)
        if i is None:
            continue                      # item not on any person -> ignore
        if det.conf > best_conf[i][slot]:
            best_conf[i][slot] = det.conf
            setattr(results[i], slot, value)

    # 3. Decide severity for each person
    for status in results:
        status.severity = _severity(status.helmet, status.vest)

    return results

def drop_small_people(detections, frame_height, min_ratio=0.2):
    """
    Remove people who are too small (far from the camera).
    At that size helmets and vests can't be seen reliably,
    so judging them would only create false REVIEW alerts.

    min_ratio=0.2 -> a person must be at least 20% of the frame height.
    PPE items are kept; they simply won't match a removed person.
    """
    kept = []
    for d in detections:
        if d.name == "person":
            x1, y1, x2, y2 = d.box
            if (y2 - y1) < min_ratio * frame_height:
                continue          # too small -> skip this person
        kept.append(d)
    return kept



