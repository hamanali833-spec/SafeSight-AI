"""
API tests: start the FastAPI app in memory and call its endpoints.
The test database is set up in conftest.py, so real alerts are not touched.
Run with:  python -m pytest -v
"""
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login

# Most tests act as the admin (allowed to do everything); role rules are tested in test_auth.py
client = TestClient(app)
client.headers.update(login(client, "admin@safesight.ai", "admin123"))

ALERT = {"cameraId": "warehouse", "trackId": 1, "kind": "ZONE",
         "severity": "HIGH", "message": "Entered restricted zone"}


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_create_and_list_alert():
    created = client.post("/api/alerts", json=ALERT)
    assert created.status_code == 201
    body = created.json()
    assert body["cameraId"] == "warehouse" and body["resolved"] is False
    ids = [a["id"] for a in client.get("/api/alerts").json()]
    assert body["id"] in ids


def test_invalid_severity_is_rejected():
    bad = {**ALERT, "severity": "MEDIUM"}
    assert client.post("/api/alerts", json=bad).status_code == 422


def test_resolve_alert():
    alert_id = client.post("/api/alerts", json=ALERT).json()["id"]
    resolved = client.patch(f"/api/alerts/{alert_id}/resolve").json()
    assert resolved["resolved"] is True
    open_ids = [a["id"] for a in client.get("/api/alerts?resolved=false").json()]
    assert alert_id not in open_ids


def test_resolve_missing_alert_returns_404():
    assert client.patch("/api/alerts/999999/resolve").status_code == 404


def test_stats_counts_alerts():
    client.post("/api/alerts", json={**ALERT, "kind": "PPE", "severity": "PARTIAL", "cameraId": "cam2"})
    stats = client.get("/api/stats").json()
    assert stats["total"] >= 1
    assert stats["byCamera"]["cam2"] >= 1
    assert "PPE" in stats["byKind"]
    assert sum(stats["byHour"].values()) == stats["total"]


def test_upload_rejects_non_video():
    files = {"file": ("notes.txt", b"hello", "text/plain")}
    assert client.post("/api/videos", files=files, data={"camera_id": "warehouse"}).status_code == 400


def test_upload_rejects_unknown_camera():
    files = {"file": ("a.mp4", b"x", "video/mp4")}
    assert client.post("/api/videos", files=files, data={"camera_id": "nope"}).status_code == 404


def test_default_cameras_exist():
    ids = [c["id"] for c in client.get("/api/cameras").json()]
    assert ids[:3] == ["warehouse", "office", "site"]


def test_turn_off_ppe_for_a_camera():
    saved = client.put("/api/cameras/office", json={"name": "Office", "ppeRequired": False}).json()
    assert saved["ppeRequired"] is False
    client.put("/api/cameras/office", json={"name": "Office", "ppeRequired": True})


def test_unknown_job_returns_404():
    assert client.get("/api/videos/nope").status_code == 404


def test_save_and_read_zone():
    points = [[10, 10], [200, 10], [200, 150]]
    saved = client.put("/api/zones/test_cam", json={"points": points})
    assert saved.status_code == 200
    assert client.get("/api/zones/test_cam").json()["zones"][0]["points"] == points
    assert client.delete("/api/zones/test_cam").status_code == 204


def test_zone_needs_three_points():
    assert client.put("/api/zones/test_cam", json={"points": [[0, 0], [1, 1]]}).status_code == 422


def test_zone_rejects_unsafe_camera_name():
    assert client.put("/api/zones/bad.name", json={"points": [[0, 0], [5, 0], [5, 5]]}).status_code == 400
