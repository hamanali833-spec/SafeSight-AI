import os
import requests
API_URL = os.getenv("SAFESIGHT_API", "http://localhost:8000/api/alerts")
# The pipeline is a program, not a person: it proves who it is with an API key, not a login.
API_KEY = os.getenv("SAFESIGHT_PIPELINE_KEY", "dev-pipeline-key")
MESSAGES = {("PPE", "HIGH"): "Helmet and vest missing", ("PPE", "PARTIAL"): "Helmet or vest missing",
            ("PPE", "REVIEW"): "PPE not clearly visible", ("ZONE", "HIGH"): "Entered restricted zone"}


def send_alert(alert, kind, camera_id):
    payload = {"cameraId": camera_id, "trackId": alert.track_id, "kind": kind,
               "severity": alert.severity, "message": MESSAGES.get((kind, alert.severity), kind + " alert")}
    try:
        requests.post(API_URL, json=payload, headers={"X-API-Key": API_KEY}, timeout=2).raise_for_status()
        return True
    except requests.RequestException as error:
        print(f"    (backend not reachable, alert not saved: {error.__class__.__name__})")
        return False
