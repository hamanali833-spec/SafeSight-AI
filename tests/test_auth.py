"""
Login and role tests: who may do what.

    guard       -> can only look (alerts, stats, cameras, zones)
    supervisor  -> can also resolve alerts and upload videos
    admin       -> can also change cameras and zones
    pipeline    -> may only post alerts, with its API key
"""
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from tests.conftest import login

client = TestClient(app)
ADMIN = ("admin@safesight.ai", "admin123")
SUPERVISOR = ("supervisor@safesight.ai", "super123")
GUARD = ("guard@safesight.ai", "guard123")
ALERT = {"cameraId": "site", "trackId": 7, "kind": "PPE", "severity": "HIGH", "message": "Helmet and vest missing"}
ZONE = {"points": [[0, 0], [5, 0], [5, 5]]}


def test_login_returns_tokens_and_user():
    from app.routers import auth
    auth._attempts.clear()
    body = client.post("/api/auth/login", json={"email": GUARD[0], "password": GUARD[1]}).json()
    assert body["user"]["role"] == "guard"
    assert body["accessToken"] and body["refreshToken"]
    assert "passwordHash" not in body["user"]          # the hash must never leave the server


def test_wrong_password_is_rejected():
    from app.routers import auth
    auth._attempts.clear()
    res = client.post("/api/auth/login", json={"email": GUARD[0], "password": "nope"})
    assert res.status_code == 401


def test_email_is_case_insensitive():
    from app.routers import auth
    auth._attempts.clear()
    res = client.post("/api/auth/login", json={"email": " Admin@SafeSight.ai ", "password": ADMIN[1]})
    assert res.status_code == 200


def test_too_many_failed_logins_are_blocked():
    from app.routers import auth
    auth._attempts.clear()
    codes = [client.post("/api/auth/login", json={"email": GUARD[0], "password": "x"}).status_code for _ in range(6)]
    assert codes[:5] == [401] * 5 and codes[5] == 429
    auth._attempts.clear()


def test_no_token_means_401():
    assert client.get("/api/alerts").status_code == 401
    assert client.get("/api/stats").status_code == 401


def test_fake_token_means_401():
    assert client.get("/api/alerts", headers={"Authorization": "Bearer abc.def.ghi"}).status_code == 401


def test_refresh_token_cannot_be_used_as_access_token():
    from app.routers import auth
    auth._attempts.clear()
    refresh = client.post("/api/auth/login", json={"email": GUARD[0], "password": GUARD[1]}).json()["refreshToken"]
    assert client.get("/api/alerts", headers={"Authorization": f"Bearer {refresh}"}).status_code == 401


def test_refresh_gives_new_access_token():
    from app.routers import auth
    auth._attempts.clear()
    refresh = client.post("/api/auth/login", json={"email": GUARD[0], "password": GUARD[1]}).json()["refreshToken"]
    new = client.post("/api/auth/refresh", json={"refreshToken": refresh}).json()["accessToken"]
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {new}"}).json()["role"] == "guard"


def test_me_returns_logged_in_user():
    me = client.get("/api/auth/me", headers=login(client, *SUPERVISOR)).json()
    assert me["email"] == SUPERVISOR[0] and me["role"] == "supervisor"


def test_guard_can_view_but_not_change():
    h = login(client, *GUARD)
    assert client.get("/api/alerts", headers=h).status_code == 200
    assert client.get("/api/cameras", headers=h).status_code == 200
    assert client.patch("/api/alerts/1/resolve", headers=h).status_code == 403
    assert client.put("/api/zones/site", json=ZONE, headers=h).status_code == 403
    files = {"file": ("a.mp4", b"x", "video/mp4")}
    assert client.post("/api/videos", files=files, data={"camera_id": "site"}, headers=h).status_code == 403


def test_supervisor_can_resolve_but_not_edit_cameras():
    h = login(client, *SUPERVISOR)
    alert_id = client.post("/api/alerts", json=ALERT, headers=h).json()["id"]
    assert client.patch(f"/api/alerts/{alert_id}/resolve", headers=h).status_code == 200
    assert client.put("/api/cameras/site", json={"name": "Site", "ppeRequired": True}, headers=h).status_code == 403
    assert client.delete("/api/zones/site", headers=h).status_code == 403


def test_pipeline_key_can_post_alerts_only():
    key = {"X-API-Key": "dev-pipeline-key"}
    assert client.post("/api/alerts", json=ALERT, headers=key).status_code == 201
    assert client.get("/api/alerts", headers=key).status_code == 401           # the key can't read
    assert client.post("/api/alerts", json=ALERT, headers={"X-API-Key": "wrong"}).status_code == 401


def test_preview_image_accepts_token_in_url():
    token = create_access_token(1, "admin")
    assert client.get(f"/api/videos/nope/frame?token={token}").status_code == 404   # passed auth, job unknown
    assert client.get("/api/videos/nope/frame").status_code == 401
