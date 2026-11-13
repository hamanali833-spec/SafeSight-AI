"""
Unit tests for the alert engine.
We simulate frames 0.1 seconds apart with fake statuses (no model, no video).
Run with:  python -m pytest -v
"""
from decision_engine.alerts import AlertEngine
from decision_engine.ppe_rules import Detection, PersonStatus, SAFE, PARTIAL, HIGH



def status(track_id, severity):
    """Build a fake PersonStatus for one person in one frame."""
    person = Detection("person", 0.9, (0, 0, 100, 300), track_id=track_id)
    return PersonStatus(person=person, severity=severity)


def run(engine, severities, track_id=1):
    """Feed one severity per frame (0.1 s apart) and collect all alerts."""
    alerts = []
    for i, sev in enumerate(severities):
        alerts += engine.update([status(track_id, sev)], now=i / 10)
    return alerts


def test_safe_person_never_alerts():
    assert run(AlertEngine(), [SAFE] * 100) == []


def test_one_bad_frame_does_not_alert():
    assert run(AlertEngine(), [SAFE] * 20 + [PARTIAL] + [SAFE] * 20) == []


def test_violation_lasting_long_enough_alerts_once():
    alerts = run(AlertEngine(), [PARTIAL] * 30)    # 3 seconds of violation
    assert len(alerts) == 1
    assert alerts[0].severity == PARTIAL


def test_safe_frame_resets_the_timer():
    # 1.5 s bad, then safe, then 1.5 s bad again: never 2 s in a row
    assert run(AlertEngine(), [PARTIAL] * 15 + [SAFE] + [PARTIAL] * 15) == []


def test_cooldown_prevents_repeated_alerts():
    # 10 s of continuous violation with a 30 s cooldown -> only one alert
    assert len(run(AlertEngine(cooldown_s=30), [PARTIAL] * 100)) == 1


def test_short_lived_track_is_ignored():
    # A "person" seen for only 0.5 s is likely noise
    assert run(AlertEngine(), [PARTIAL] * 5) == []



def test_escalation_alerts_again_during_cooldown():
    # 2.5 s PARTIAL (alert), then it gets worse: HIGH -> a second alert despite the cooldown
    alerts = run(AlertEngine(cooldown_s=30), [PARTIAL] * 25 + [HIGH] * 10)
    assert [a.severity for a in alerts] == [PARTIAL, HIGH]


def test_getting_better_does_not_alert_again():
    # HIGH alert first; dropping back to PARTIAL during the cooldown is not news
    alerts = run(AlertEngine(cooldown_s=30), [HIGH] * 25 + [PARTIAL] * 10)
    assert [a.severity for a in alerts] == [HIGH]