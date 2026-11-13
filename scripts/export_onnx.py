"""
Export the trained PyTorch model (best.pt) to ONNX format.

Why: PyTorch is built for training. ONNX Runtime is built only for
fast inference, so the same model usually runs faster on a CPU.
"""
from pathlib import Path          # Path handles file paths safely on Windows and Linux

from ultralytics import YOLO      # Ultralytics library that loads and runs YOLO models

# Location of our trained model (relative to the project root)
WEIGHTS = Path("ppe-detection/weights/best.pt")


def main():
    # 1. Load the trained PyTorch model
    model = YOLO(WEIGHTS)

    # 2. Convert it to ONNX
    #    imgsz=640    -> same image size the model was trained on
    #    simplify=True -> clean up the model graph (removes extra steps)
    onnx_path = model.export(format="onnx", imgsz=640, simplify=True, dynamic=True)

    # 3. Show where the new file was saved (best.onnx, next to best.pt)
    print("ONNX model saved to:", onnx_path)


# Run main() only when this file is executed directly,
# not when another file imports it
if __name__ == "__main__":
    main()