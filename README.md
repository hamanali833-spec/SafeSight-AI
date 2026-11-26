# 🦺 SafeSight AI: Workplace Safety Monitoring from CCTV

A real-time safety monitoring system that watches ordinary CCTV cameras, detects workers who are missing a **helmet** or **safety vest**, and raises an alert when someone walks into a **restricted zone**. A YOLOv8 detector finds people and safety gear, ByteTrack follows each person across frames, and a rule-based decision engine turns detections into clear, explainable alerts on a web dashboard.

👥 **Team:** Haman Ali · Alishba Saeed · Roshane Asif

---

## 🚀 Features

### 🔍 Detection
- 🪖 **Helmet detection:** `helmet` and `no_helmet` for every person
- 🦺 **Vest detection:** `vest` and `no_vest` for every person
- 🧍 **Person detection:** the base for PPE ownership and zone checks
- 👣 **Person tracking:** ByteTrack gives each person a stable ID across frames
- 🎞️ **Black-bar crop:** removes letterbox borders and shifts zones to match

### 🧠 Decision engine (rules, not ML)
- **PPE ownership:** a helmet or vest belongs to the person whose box contains its center (10% margin)
- **Severity per person:** `SAFE` · `PARTIAL` (one item missing) · `HIGH` (both missing) · `REVIEW` (not visible enough to decide)
- **Restricted zones:** a person is inside when their **feet point** is inside the polygon (ray casting)
- **Small, far-away people** are skipped for PPE (too small to judge) but still checked for zones

### 🚨 Alert system
- ⏱️ **Confirmation:** a track must exist for 1 s and the violation must last 2 s (zones 1 s), so one-frame glitches never alert
- 🔕 **Cooldown:** 30 s per person and alert type, so no repeated alerts after someone leaves and comes back
- ⬆️ **Escalation:** a `PARTIAL` alert can still upgrade to `HIGH` during the cooldown
- 💾 **Stored in a database** and shown live on the dashboard, with resolve tracking

### 📹 Multi-camera
- Three cameras out of the box: **Warehouse**, **Office**, **Site gate**
- Each camera has its **own tracker, alert engine, zone and PPE setting** (an office can turn PPE off and keep only the zone)
- Up to 3 cameras processed in parallel

### 🖥️ Dashboard
- 📺 **Monitoring:** live processed frame per camera with alert counts
- 🔔 **Alerts:** filter by severity, resolve alerts
- 📊 **Analytics:** alerts by camera, type, severity and hour of day
- 🗺️ **Cameras & zones:** draw a zone right in the browser on the camera's first frame
- 🌗 Dark and light themes

### 🔐 Security
- Login with **JWT** (30-minute access token, 7-day refresh token)
- Passwords stored only as **bcrypt** hashes
- **Roles:** guard (view only) · supervisor (run cameras, resolve alerts) · admin (cameras and zones)
- Login rate limit: 5 failed attempts per minute
- The video pipeline posts alerts with an **API key** instead of a user login

---

## 🔄 How it works

```
📹 Video / CCTV frame
   ↓
🎯 YOLOv8n detector ──── person · helmet · no_helmet · vest · no_vest
   ↓
👣 ByteTrack ─────────── stable ID per person
   ↓
🧠 PPE rule engine ───── which gear belongs to whom → SAFE / PARTIAL / HIGH / REVIEW
   ↓
🗺️ Zone check ────────── feet point inside the restricted polygon?
   ↓
🚨 Alert engine ──────── confirmation · cooldown · escalation
   ↓
⚙️ FastAPI + SQLite ──── alerts · cameras · users
   ↓
🖥️ React dashboard
```

Only the detector is machine learning. Every decision after it is plain, unit-tested code, so each alert can be explained.

---

## 📁 Project structure

```
SafeSight-AI/
├── 📂 backend/app/                  # FastAPI server
│   ├── core/                        # config, database, security (JWT, bcrypt), role checks
│   ├── models/                      # database tables: alert, camera, user
│   ├── schemas/                     # request / response shapes (Pydantic)
│   ├── repositories/                # all database access
│   ├── services/                    # business logic: alerts, stats, video jobs
│   ├── routers/                     # API endpoints: auth, alerts, stats, videos, zones, cameras
│   └── main.py                      # app setup, serves the built dashboard
├── 📂 decision_engine/              # The rules
│   ├── ppe_rules.py                 # PPE ownership and severity
│   ├── alerts.py                    # confirmation, cooldown, escalation
│   └── zones.py                     # feet point + point-in-polygon
├── 📂 inference/                    # Video processing
│   ├── tracker.py                   # YOLOv8 + ByteTrack
│   ├── pipeline.py                  # video → detections → rules → alerts
│   └── framing.py                   # black-bar crop and zone shift
├── 📂 frontend/                     # React + TypeScript + Tailwind dashboard
│   └── src/  (pages, components, api, auth)
├── 📂 ppe-detection/                # Trained model weights and training results
├── 📂 scripts/                      # Command-line tools (run a video, draw a zone, send alerts)
├── 📂 tests/                        # Unit and API tests (pytest)
├── 📂 zones/                        # One restricted-zone file per camera
├── 📋 main.py                       # One-command launcher
├── 📄 requirements.txt
└── 📚 README.md
```

---

## 🛠️ Installation

### Prerequisites
- 🐍 Python 3.12
- 🟩 Node.js 18 or newer (only to build the dashboard)
- GPU optional: the model runs on a normal laptop CPU

### Setup
```powershell
# 1. Clone the repository
git clone https://github.com/hamanali833-spec/SafeSight-AI.git
cd SafeSight-AI

# 2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install Python packages
pip install -r requirements.txt
```

---

## ⚡ Quick start

```powershell
python main.py
```

That's it. `main.py` checks the libraries, builds the dashboard the first time, starts the server and opens **http://localhost:8000** in your browser.

| Command | What it does |
|---|---|
| `python main.py` | ▶️ Run the whole project on one port |
| `python main.py --check` | 🩺 Check libraries, database and login, then stop |
| `python main.py --dev` | 🛠️ Development mode: auto-reload + Vite on port 5173 |
| `python -m pytest -q` | 🧪 Run all tests |

### 👤 Demo accounts
| Role | Email | Password | Can do |
|---|---|---|---|
| Admin | admin@safesight.ai | admin123 | Everything, including cameras and zones |
| Supervisor | supervisor@safesight.ai | super123 | Run cameras, resolve alerts |
| Guard | guard@safesight.ai | guard123 | View only |

### 🎬 Try it
1. Log in as **Admin**
2. **Cameras & zones:** pick a camera, choose its video, click the corners of the restricted area, **Save zone**
3. **Monitoring:** drop a video into each camera tile, press **Start all**
4. Watch alerts appear in **Alerts** and **Analytics**

---

## 📊 Model performance

**YOLOv8n**, transfer learning from COCO weights, 50 epochs, image size 640, batch 16, trained on a Kaggle T4 GPU. Tested on **406 images the model never saw during training** (2,785 objects).

| Class | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| 🧍 person | 0.935 | 0.860 | 0.907 | 0.689 |
| 🦺 vest | 0.929 | 0.865 | 0.919 | 0.664 |
| 🪖 helmet | 0.908 | 0.843 | 0.895 | 0.578 |
| ❌ no_vest | 0.883 | 0.782 | 0.836 | 0.506 |
| ❌ no_helmet | 0.846 | 0.743 | 0.819 | 0.481 |
| **✅ All classes** | **0.900** | **0.818** | **0.875** | **0.583** |

- Validation mAP50 **0.910**, close to the test score, so no sign of heavy overfitting
- Exported to **ONNX** for faster CPU inference (about 33 ms per frame on our test laptop)
- Every 3rd frame is processed, which keeps CPU use low while still checking about 10 times per second

---

## 🚨 Alert format

Every confirmed alert is stored and returned by the API like this:

```json
{
  "id": 42,
  "cameraId": "warehouse",
  "trackId": 11,
  "kind": "ZONE",
  "severity": "HIGH",
  "message": "Entered restricted zone",
  "createdAt": "2026-11-21T02:48:05",
  "resolved": false
}
```

| Field | Values |
|---|---|
| `kind` | `PPE` · `ZONE` |
| `severity` | `HIGH` · `PARTIAL` · `REVIEW` |

---

## 🔌 API

Interactive docs at **http://localhost:8000/docs** while the server runs.

| Method | Endpoint | Who |
|---|---|---|
| `POST` | `/api/auth/login` · `/api/auth/refresh` | Everyone |
| `GET` | `/api/auth/me` | Logged in |
| `GET` | `/api/alerts` · `/api/stats` · `/api/cameras` · `/api/zones` | Logged in |
| `PATCH` | `/api/alerts/{id}/resolve` | Supervisor, admin |
| `POST` | `/api/videos` (start a camera) | Supervisor, admin |
| `PUT` / `DELETE` | `/api/zones/{camera}` · `PUT /api/cameras/{camera}` | Admin |
| `POST` | `/api/alerts` | Video pipeline (API key) |

---

## 🔧 Configuration

Settings are read from environment variables, with safe defaults for local use:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./safesight.db` | Database (switch to PostgreSQL by changing only this) |
| `SAFESIGHT_SECRET` | dev value | Signs login tokens: **set a long random value in production** |
| `SAFESIGHT_PIPELINE_KEY` | `dev-pipeline-key` | API key the video pipeline uses to post alerts |

Alert timing lives in `inference/pipeline.py`:
```python
ppe_engine  = AlertEngine(min_track_s=1.0, confirm_s=2.0, cooldown_s=30.0)
zone_engine = AlertEngine(min_track_s=1.0, confirm_s=1.0, cooldown_s=30.0)
```

---

## 🧪 Testing

```powershell
python -m pytest -q
```

Covers the PPE rules, alert engine, zones, black-bar crop, every API endpoint, and login and role permissions.

---

## 🧰 Built with

| Layer | Tools |
|---|---|
| 🤖 Model | YOLOv8n (Ultralytics), ByteTrack, ONNX Runtime, OpenCV |
| ⚙️ Backend | FastAPI, SQLAlchemy, SQLite, Pydantic, PyJWT, bcrypt |
| 🖥️ Frontend | React, TypeScript, Vite, Tailwind CSS |
| 🧪 Testing | pytest |

---

## 🎯 Use cases

- 🏗️ **Construction sites:** helmet and vest compliance at the gate and on the floor
- 🏭 **Warehouses and factories:** PPE checks plus no-go areas around machines and loading bays
- 🏢 **Offices:** restricted rooms such as server rooms, with PPE turned off
- ⚡ **Plants and utilities:** keep people out of high-voltage and hazardous zones

---

## 🗺️ Roadmap

- 📡 Live RTSP camera streams
- 📈 More training data from real site cameras
- 🐘 PostgreSQL and a message queue for many cameras
- 🐳 Docker packaging
- 📱 Push or email notifications for HIGH alerts

---

## 📄 License

Ultralytics YOLOv8 is licensed under **AGPL-3.0**. Commercial use needs an Ultralytics licence or a different detector.

---

## 📬 Contact

- GitHub: [hamanali833-spec](https://github.com/hamanali833-spec)
- Team: Haman Ali · Alishba Saeed · Roshane Asif