"""
Command-line runner for the video pipeline.

Run from the project root:
    python -m scripts.run_video samples/warehouse.mp4
If zones/<video name>.json exists (made with scripts/draw_zone.py), zone alerts are on.
Confirmed alerts are printed and sent to the backend API (if it is running).
"""
import sys
from pathlib import Path

from inference.pipeline import process_video
from scripts.alert_client import send_alert

OUTPUT_DIR = Path("outputs/video")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_video <video_path>")
        return
    path = Path(sys.argv[1])
    camera_id = path.stem      # the video name stands in for the camera name, e.g. "warehouse"
    zones_path = Path("zones") / f"{path.stem}.json"
    print(f"Restricted zones: {'yes' if zones_path.exists() else 'none'}")

    def on_alert(alert, kind):
        what = "entered restricted zone" if kind == "ZONE" else alert.severity
        print(f"  {kind} ALERT at {alert.time_s:5.1f}s: ID {alert.track_id} {what}")
        send_alert(alert, kind, camera_id)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / path.name
    summary = process_video(path, zones_path=zones_path, output_path=out_path, on_alert=on_alert)

    print(f"\nFrames processed: {summary['frames']}  ({summary['seconds']} s of video)")
    print(f"People tracked: {len(summary['people'])}")
    for tid, counts in sorted(summary["people"].items()):
        print(f"  ID {tid}: {counts}")
    print(f"PPE alerts: {summary['ppe_alerts']}   Zone alerts: {summary['zone_alerts']}")
    print("Saved to:", out_path)


if __name__ == "__main__":
    main()
