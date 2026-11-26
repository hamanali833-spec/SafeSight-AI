"""
Shared test setup (pytest runs this file before any test file).
Points the app at a throwaway database BEFORE it is imported, so real data is never touched.
"""
import os
import sys
from pathlib import Path

TEST_DB = Path("test_safesight.db")
TEST_DB.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DB}"
sys.path.insert(0, "backend")     # so "import app" finds backend/app


def login(client, email, password):
    """Log in and return the auth header. Clears the rate limiter so tests don't hit 429."""
    from app.routers import auth
    auth._attempts.clear()
    token = client.post("/api/auth/login", json={"email": email, "password": password}).json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}
