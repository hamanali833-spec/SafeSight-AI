"""
Run the full pipeline on a video:
    video -> tracker (ONNX + ByteTrack) -> rule engine -> output video with IDs and decisions

Run from the project root:
    python -m scripts.run_video samples/site_cropped.mp4
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cv2

from inference.tracker import PPETracker
from decision_engine.ppe_rules import evaluate, drop_small_people
from scripts.run_rules import draw   # reuse the same drawing code as for images

OUTPUT_DIR = Path("outputs/video")
VID_STRIDE = 2         # process every 2nd frame to keep the laptop fast
MIN_PERSON_RATIO = 0.2 # ignore people smaller than 20% of the frame height (too far away)


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_video <video_path>")
        return
    path = Path(sys.argv[1])

    # Read the video's frame rate so the output plays at the right speed
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    cap.release()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / path.name
    writer = None
    frames = 0

    # For each person ID, count how many frames they spent in each status,
    # e.g. {4: {"SAFE": 95, "REVIEW": 3}}
    history = defaultdict(Counter)

    tracker = PPETracker()
    for frame, detections in tracker.track_video(str(path), vid_stride=VID_STRIDE):
        # 1. Remove people who are too far away to judge
        detections = drop_small_people(detections, frame.shape[0], MIN_PERSON_RATIO)

        # 2. Apply the rules to this frame
        statuses = evaluate(detections)

        # 3. Count this frame's status for each person ID
        for s in statuses:
            if s.person.track_id is not None:
                history[s.person.track_id][s.severity] += 1

        # 4. Draw and write the frame to the output video
        frame = draw(frame, statuses)
        if writer is None:   # create the writer once we know the frame size
            h, w = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(out_path), fourcc, fps / VID_STRIDE, (w, h))
        writer.write(frame)

        frames += 1
        if frames % 20 == 0:
            print(f"  processed {frames} frames...")

    if writer:
        writer.release()   # finish the file, otherwise the video may not open

    # 5. Summary: for each person, the status counts and the most common one
    print(f"\nFrames processed: {frames}")
    print(f"People tracked: {len(history)}")
    for tid, counts in sorted(history.items()):
        most_common = counts.most_common(1)[0][0]
        print(f"  ID {tid}: {dict(counts)} -> mostly {most_common}")
    print("Saved to:", out_path)


if __name__ == "__main__":
    main()