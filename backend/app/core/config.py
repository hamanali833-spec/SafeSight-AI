"""
Settings for the backend, read from environment variables with safe defaults.
Changing the database (SQLite -> PostgreSQL) only means changing DATABASE_URL.
In production, SECRET_KEY and PIPELINE_API_KEY must be set to long random values.
"""
import os

# SQLite file in the folder you start the server from (the project root)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./safesight.db")

# Signs the login tokens (JWT). Anyone with this key could make valid tokens.
SECRET_KEY = os.getenv("SAFESIGHT_SECRET", "dev-secret-change-me-in-production-0123456789")
ACCESS_TOKEN_MINUTES = 30        # short-lived: sent with every request
REFRESH_TOKEN_DAYS = 7           # long-lived: only used to get a new access token

# The video pipeline (scripts/run_video.py) is a program, not a person, so it
# sends this key instead of logging in.
PIPELINE_API_KEY = os.getenv("SAFESIGHT_PIPELINE_KEY", "dev-pipeline-key")
