"""
Unit tests for the PPE rule engine.
Each test builds fake detections (no model needed) and checks the decision.
Run with:  python -m pytest -v
"""
from decision_engine.ppe_rules import Detection, evaluate, SAFE, PARTIAL, HIGH, REVIEW
from decision_engine.ppe_rules import Detection, evaluate, drop_small_people, SAFE, PARTIAL, HIGH, REVIEW

# A person standing at x=100..200, y=100..400
PERSON = Detection("person", 0.90, (100, 100, 200, 400))
HELMET = Detection("helmet", 0.85, (130, 90, 170, 130))     # on the head
VEST = Detection("vest", 0.85, (110, 180, 190, 300))        # on the body
NO_HELMET = Detection("no_helmet", 0.80, (130, 90, 170, 130))
NO_VEST = Detection("no_vest", 0.80, (110, 180, 190, 300))


def test_safe_when_helmet_and_vest():
    assert evaluate([PERSON, HELMET, VEST])[0].severity == SAFE


def test_partial_when_one_item_missing():
    assert evaluate([PERSON, NO_HELMET, VEST])[0].severity == PARTIAL


def test_high_when_both_missing():
    assert evaluate([PERSON, NO_HELMET, NO_VEST])[0].severity == HIGH


def test_review_when_vest_not_visible():
    # Helmet seen, vest neither seen nor reported missing
    assert evaluate([PERSON, HELMET])[0].severity == REVIEW


def test_helmet_on_table_is_ignored():
    table_helmet = Detection("helmet", 0.90, (500, 500, 540, 540))  # far from the person
    assert evaluate([PERSON, table_helmet, VEST])[0].helmet == "unknown"


def test_two_people_get_their_own_items():
    person2 = Detection("person", 0.90, (300, 100, 400, 400))
    no_helmet2 = Detection("no_helmet", 0.80, (330, 90, 370, 130))
    vest2 = Detection("vest", 0.85, (310, 180, 390, 300))
    results = evaluate([PERSON, HELMET, VEST, person2, no_helmet2, vest2])
    assert results[0].severity == SAFE
    assert results[1].severity == PARTIAL


def test_higher_confidence_wins_on_conflict():
    weak_no_helmet = Detection("no_helmet", 0.40, (130, 90, 170, 130))
    assert evaluate([PERSON, HELMET, weak_no_helmet, VEST])[0].helmet == "ok"


def test_far_away_person_is_dropped():
    # Frame is 1000 px tall. PERSON is 300 px tall (kept); this one is 100 px (dropped).
    far_person = Detection("person", 0.80, (600, 100, 640, 200))
    kept = drop_small_people([PERSON, far_person, HELMET, VEST], frame_height=1000)
    statuses = evaluate(kept)
    assert len(statuses) == 1
    assert statuses[0].severity == SAFE


