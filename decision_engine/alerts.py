"""
Alert engine: decides WHEN a violation becomes a real alert.

The rule engine judges every frame on its own, and single frames are noisy:
a vest can be missed for one frame because of blur or a bad angle.
Alerting on every frame would flood the dashboard with false alarms.

So an alert is raised only when:
  1. the person has been tracked long enough to be real   (min_track_s)
  2. the violation has lasted without a break             (confirm_s)
  3. we have not already alerted for this person recently (cooldown_s)

Time is passed in by the caller (seconds), so this file can be tested
without a camera or a real clock.
"""
from dataclasses import dataclass

from decision_engine.ppe_rules import PARTIAL, HIGH, REVIEW

# Statuses that count as a problem. REVIEW alerts go to a human to check.
ALERT_LEVELS = {PARTIAL, HIGH, REVIEW}
RANK = {REVIEW: 1, PARTIAL: 2, HIGH: 3}


@dataclass
class Alert:
    """One confirmed alert."""
    track_id: int
    severity: str
    time_s: float      # when the alert was raised (seconds into the video)
    duration_s: float  # how long the violation had lasted at that moment


class AlertEngine:
    def __init__(self, min_track_s=1.0, confirm_s=2.0, cooldown_s=30.0):
        self.min_track_s = min_track_s
        self.confirm_s = confirm_s
        self.cooldown_s = cooldown_s

        # Memory per person ID (track_id -> time in seconds)
        self.first_seen = {}       # when we first saw this person
        self.violation_start = {}  # when their current violation began
        self.last_alert = {}       # when we last alerted for them
        self.last_severity = {}    # severity of that last alert

    def update(self, statuses, now):
        """
        statuses: list of PersonStatus for the current frame
        now:      current time in seconds
        returns:  list of new Alerts raised in this frame (usually empty)
        """
        alerts = []
        for s in statuses:
            tid = s.person.track_id
            if tid is None:
                continue                         # no ID -> can't follow over time

            self.first_seen.setdefault(tid, now)

            # 1. Person is fine -> any running violation timer is reset
            if s.severity not in ALERT_LEVELS:
                self.violation_start.pop(tid, None)
                continue

            # 2. Person has a problem -> start the timer if it isn't running
            start = self.violation_start.setdefault(tid, now)

            # 3. Check the three conditions
            is_real_person = now - self.first_seen[tid] >= self.min_track_s
            is_confirmed = now - start >= self.confirm_s
            is_cooled_down = now - self.last_alert.get(tid, float("-inf")) >= self.cooldown_s
            # Escalation: the problem got worse than what we last reported
            # (e.g. PARTIAL -> HIGH). That must be reported even during the cooldown.
            is_escalation = RANK[s.severity] > RANK.get(self.last_severity.get(tid), 0)

            if is_real_person and is_confirmed and (is_cooled_down or is_escalation):
                self.last_alert[tid] = now
                self.last_severity[tid] = s.severity
                alerts.append(Alert(tid, s.severity, round(now, 2), round(now - start, 2)))

        return alerts