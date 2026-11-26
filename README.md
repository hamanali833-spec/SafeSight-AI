# SafeSight AI

Workplace safety monitoring from ordinary CCTV cameras. SafeSight finds people without a helmet or safety vest, notices when someone walks into a restricted area, and sends one clear alert to the right person.

Final year project by **Haman Ali**, **Alishba Saeed** and **Roshane Asif**.

---

## What it does

- **Helmet and vest checks:** detects every person and decides, person by person, whether they are SAFE, PARTIAL (one item missing), HIGH (both missing) or need human REVIEW.
- **Restricted zones:** an admin draws a zone on each camera in the browser; anyone whose feet enter it triggers an alert.
- **Smart alerts:** an alert needs a stable track (1 s) and a violation that lasts (2 s, zones 1 s), then a 30 s cooldown stops repeats. A PARTIAL can still escalate to HIGH.
- **Multiple cameras:** each camera has its own tracker, alert engine, zone and PPE setting (an office can have PPE off and only a zone).
- **Dashboard:** live camera tiles, alert list with resolve, analytics, camera and zone setup.
- **Login with roles:** guard (view), supervisor (run cameras, resolve alerts), admin (cameras and zones).

## How it works

```
Video / CCTV frame
  -> YOLOv8n detector      person, helmet, no_helmet, vest, no_vest
  -> ByteTrack             a stable ID for each person across frames
  -> PPE rule engine       which helmet/vest belongs to which person -> severity
  -> Zone check            feet point inside the polygon (ray casting)
  -> Alert engine          confirmation, cooldown, escalation
  -> FastAPI + SQLite      alerts, cameras, users
  -> React dashboard
```

Only detection is machine learning. Ownership, severity, zones and alert timing are plain, unit-tested rules, so every decision can be explained.

## Model results

YOLOv8n, transfer learning from COCO weights, 50 epochs, image size 640, batch 16 (Kaggle T4). Tested on 406 images the model never saw during training.

| Class     | Precision | Recall | mAP50 | mAP50-95 |
|-----------|-----------|--------|-------|----------|
| person    | 0.935     | 0.860  | 0.907 | 0.689    |
| vest      | 0.929     | 0.865  | 0.919 | 0.664    |
| helmet    | 0.908     | 0.843  | 0.895 | 0.578    |
| no_vest   | 0.883     | 0.782  | 0.836 | 0.506    |
| no_helmet | 0.846     | 0.743  | 0.819 | 0.481    |
| **All**   | **0.900** | **0.818** | **0.875** | **0.583** |

Validation mAP50 was 0.910, close to the test score. The model is also exported to ONNX for faster CPU inference.

## Run it

Needs Python 3.12 and Node.js.

```powershell
git clone https://github.com/hamanali833-spec/SafeSight-AI.git
cd SafeSight-AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

`main.py` checks the libraries, builds the website the first time (installs the frontend packages if needed), starts the server and opens http://localhost:8000.

| Command | What it does |
|---|---|
| `python main.py` | Run the whole project on one port |
| `python main.py --check` | Check libraries, database and login, then stop |
| `python main.py --dev` | Development: backend auto-reload + Vite on port 5173 |
| `python -m pytest -q` | Run the tests |

Demo accounts (created on first start):

| Role | Email | Password |
|---|---|---|
| Admin | admin@safesight.ai | admin123 |
| Supervisor | supervisor@safesight.ai | super123 |
| Guard | guard@safesight.ai | guard123 |

Change these passwords and set `SAFESIGHT_SECRET` and `SAFESIGHT_PIPELINE_KEY` before any real use.

## Project structure

```
backend/app/       FastAPI: routers -> services -> repositories -> models, plus schemas and core (config, security, auth)
decision_engine/   rules: ppe_rules.py, alerts.py, zones.py
inference/         tracker.py (YOLO + ByteTrack), pipeline.py (video -> alerts), framing.py (black-bar crop)
frontend/          React + TypeScript + Tailwind dashboard
ppe-detection/     trained weights and training results
scripts/           command-line tools: run_video, export_onnx, benchmark, split_grid ...
tests/             unit and API tests
zones/             one restricted-zone file per camera
main.py            one-command launcher
```

## Built with

YOLOv8 (Ultralytics), ByteTrack, ONNX Runtime, OpenCV, FastAPI, SQLAlchemy, SQLite, PyJWT, bcrypt, React, TypeScript, Vite, Tailwind CSS, pytest.

## Next steps

- Live RTSP camera streams instead of video files
- More training data from real site cameras, especially for `no_helmet`
- PostgreSQL and a message queue for many cameras
- Docker packaging

## License note

Ultralytics YOLOv8 is AGPL-3.0. Commercial use needs an Ultralytics licence or a different detector.