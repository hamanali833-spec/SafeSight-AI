# SafeSight AI: CCTV-Based Workplace Safety Monitoring

A computer vision system that detects people, helmets and safety vests in CCTV footage and raises alerts for missing PPE, unauthorized zone entry and blocked emergency exits.
Team project (3 members) built during the NIAI-NAVTTC AI/ML training program at NETSOL Technologies.

## Modules

| Module | What it does | Status |
|---|---|---|
| 1. PPE detection | Detects helmet, vest, person, no_helmet, no_vest with YOLOv8 | ✅ Trained and tested |
| 2. Restricted zone + authorization | Zone check (geometry) + employee lookup; low-confidence cases go to human review | 🕓 Planned |
| 3. Emergency exit monitoring | Alert if an exit path stays blocked beyond a time limit | 🕓 Planned |

Only detection uses ML. Zones, permissions, severity and alerts are rule-based code.

## Dataset

[Personal-Protective-Equipment (PPE) Dataset](https://www.kaggle.com/datasets/tafartech/personal-protective-equipmentppe) by tafartech on Kaggle (MIT license).

- 4,060 images: train 3,248 / valid 406 / test 406 (YOLO format)
- 5 classes: helmet, no_helmet, no_vest, person, vest

## Training

- Model: YOLOv8n (pretrained weights)
- 50 epochs, image size 640, batch 16, scale augmentation 0.8
- Kaggle T4 GPU, about 26 minutes
- Validation: P 0.918, R 0.843, mAP50 0.910, mAP50-95 0.591

## Test Results (406 unseen images)

| Class | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---|---|---|
| helmet | 0.908 | 0.843 | 0.895 | 0.578 |
| no_helmet | 0.846 | 0.743 | 0.819 | 0.481 |
| no_vest | 0.883 | 0.782 | 0.836 | 0.506 |
| person | 0.935 | 0.860 | 0.907 | 0.689 |
| vest | 0.929 | 0.865 | 0.919 | 0.664 |
| **All** | **0.900** | **0.818** | **0.875** | **0.583** |

Speed: about 4 ms per image on a T4 GPU, and about 125–150 ms per image on CPU.

Plots are in `ppe-detection/results/test/`.

## Known limitations

- `no_helmet` has the lowest recall (0.743)
- Not yet tested on real CCTV, night footage or videos with actual violators

## Planned stack

YOLOv8 + ByteTrack + ONNX Runtime · FastAPI (layered) + PostgreSQL + Redis + WebSocket · JWT + RBAC · React + TypeScript · Docker Compose · Prometheus + Grafana · AWS EC2 + GitHub Actions

## Project structure

```
ppe-detection/     training notebook, weights, test results
inference/         detector (YOLO/ONNX) and tracker (ByteTrack)
decision-engine/   rule-based logic: PPE severity, zones, exit monitor
backend/           FastAPI service
frontend/          React dashboard
scripts/           test and helper scripts
```



