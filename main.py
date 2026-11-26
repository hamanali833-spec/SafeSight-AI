"""
SafeSight AI: start the whole project with one command.

    python main.py            normal use: builds the website if needed, starts the server,
                              opens http://localhost:8000 in your browser
    python main.py --check    checks libraries, database and login, then stops (for problems)
    python main.py --dev      for coding: backend auto-reload + Vite on http://localhost:5173

Why one server? FastAPI serves both the API (/api/...) and the built React files.
One process instead of two (uvicorn + npm run dev) = lighter on the laptop, simpler demo.
"""
import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
DIST_INDEX = FRONTEND / "dist" / "index.html"
PORT = 8000

os.chdir(ROOT)                          # database, zones and outputs are relative to the root
sys.path.insert(0, str(ROOT / "backend"))   # so "import app" finds backend/app

NEEDED = {"fastapi": "fastapi", "uvicorn": "uvicorn", "sqlalchemy": "sqlalchemy",
          "multipart": "python-multipart", "jwt": "pyjwt", "bcrypt": "bcrypt"}


def check_libraries() -> bool:
    missing = []
    for module, package in NEEDED.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        print("[X] Missing libraries:", ", ".join(missing))
        print("    Fix (with your venv active):  pip install " + " ".join(missing))
        return False
    print("[OK] Python libraries")
    return True


def npm() -> str | None:
    # Windows has two files: "npm" (a Linux shell script) and "npm.cmd" (the real
    # Windows one). Running the first gives WinError 193, so ask for npm.cmd first.
    if os.name == "nt":
        return shutil.which("npm.cmd") or shutil.which("npm")
    return shutil.which("npm")


def frontend_is_outdated() -> bool:
    """True if there is no build yet, or a frontend file changed after the last build."""
    if not DIST_INDEX.exists():
        return True
    built = DIST_INDEX.stat().st_mtime
    sources = [*(FRONTEND / "src").rglob("*"), FRONTEND / "index.html", *(FRONTEND / "public").rglob("*")]
    return any(f.is_file() and f.stat().st_mtime > built for f in sources)


def build_frontend() -> bool:
    if not frontend_is_outdated():
        print("[OK] Website already built")
        return True
    if npm() is None:
        print("[X] npm not found. Install Node.js, or build once on a PC that has it.")
        return DIST_INDEX.exists()      # an old build is still better than nothing
    if not (FRONTEND / "node_modules").exists():
        print("[..] First time: installing frontend packages (npm install)...")
        subprocess.run([npm(), "install"], cwd=FRONTEND, check=False)
    print("[..] Building the website (npm run build), about 10-30 seconds...")
    result = subprocess.run([npm(), "run", "build"], cwd=FRONTEND)
    if result.returncode != 0:
        print("[X] Website build failed: read the red error above.")
        return False
    print("[OK] Website built")
    return True


def check_login() -> bool:
    """Log in as the demo admin inside Python (no browser) to prove login works."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.repositories.user_repository import DEMO_USERS

    client = TestClient(app)
    email, _, _, password = DEMO_USERS[0]
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print(f"[X] Demo login failed ({res.status_code}): {res.text}")
        return False
    token = res.json()["accessToken"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    print(f"[OK] Login works ({me['email']} as {me['role']})")
    return True


def open_browser_later(url: str):
    def go():
        time.sleep(2.5)                 # give the server a moment to start
        webbrowser.open(url)
    threading.Thread(target=go, daemon=True).start()


def print_accounts():
    print("\n  Demo accounts:  admin@safesight.ai / admin123")
    print("                  supervisor@safesight.ai / super123")
    print("                  guard@safesight.ai / guard123")
    print("  Stop the server: Ctrl + C\n")


def main():
    args = sys.argv[1:]
    print("\n=== SafeSight AI ===")
    if not check_libraries():
        sys.exit(1)

    if "--check" in args:
        ok = check_login()
        if not DIST_INDEX.exists():
            print("[!] Website not built yet (python main.py builds it on start)")
        print("\nAll good!" if ok else "\nFix the [X] lines above.")
        return

    import uvicorn

    if "--dev" in args:
        # Two processes: Vite (instant page reload) + backend with auto-reload
        if npm() is None:
            sys.exit("[X] npm not found, can't start Vite.")
        vite = subprocess.Popen([npm(), "run", "dev"], cwd=FRONTEND)
        open_browser_later("http://localhost:5173")
        print_accounts()
        try:
            uvicorn.run("app.main:app", host="127.0.0.1", port=PORT, reload=True,
                        reload_dirs=[str(ROOT / "backend")])
        finally:
            vite.terminate()
        return

    if not build_frontend():
        sys.exit(1)
    url = f"http://localhost:{PORT}"
    print(f"\n  SafeSight is starting at {url}")
    print_accounts()
    open_browser_later(url)
    uvicorn.run("app.main:app", host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
