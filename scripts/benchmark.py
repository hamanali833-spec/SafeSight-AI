"""
Compare inference speed of PyTorch (.pt) vs ONNX (.onnx) on CPU.

It checks two things:
  1. Which format is faster?
  2. Do both formats give the same detections? (speed must not cost accuracy)
"""
import sys                        # read the image path from the command line
import statistics                 # calculate the average time
from pathlib import Path

from ultralytics import YOLO

# The two model files we want to compare
MODELS = {
    "PyTorch": Path("ppe-detection/weights/best.pt"),
    "ONNX":    Path("ppe-detection/weights/best.onnx"),
}

# Number of timed runs. One run is noisy; the average of many is reliable.
RUNS = 20


def benchmark(name, weights, image):
    """Run one model many times and return its average inference time (ms)."""

    # Load the model. task="detect" tells YOLO what kind of model the ONNX file is.
    model = YOLO(weights, task="detect")

    # Warm-up run: the first run is always slow (loading into memory,
    # setting up the runtime), so we run once and ignore it.
    model.predict(image, conf=0.4, verbose=False)

    # Timed runs: store the inference time of each run
    times = []
    for _ in range(RUNS):
        result = model.predict(image, conf=0.4, verbose=False)[0]
        times.append(result.speed["inference"])   # time of the neural network only (ms)

    # Turn class numbers into names, e.g. [0, 3, 4] -> ['helmet', 'person', 'vest']
    labels = sorted(model.names[int(c)] for c in result.boxes.cls)

    average = statistics.mean(times)
    print(f"{name:<8} avg {average:6.1f} ms | detections: {labels}")
    return average


def main():
    # Use the image given on the command line, or our sample image by default
    image = sys.argv[1] if len(sys.argv) > 1 else "samples/helmet_worker.jpg"

    # Measure both formats on the same image
    pt_time = benchmark("PyTorch", MODELS["PyTorch"], image)
    onnx_time = benchmark("ONNX", MODELS["ONNX"], image)

    # Speed-up: how many times faster ONNX is (e.g. 2.00x = twice as fast)
    print(f"\nONNX is {pt_time / onnx_time:.2f}x faster on this CPU")


if __name__ == "__main__":
    main()