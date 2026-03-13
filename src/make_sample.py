import argparse
from pathlib import Path

import cv2
import numpy as np


def build_sample(width: int = 1280, height: int = 720) -> np.ndarray:
    x = np.linspace(0, 1, width, dtype=np.float32)
    y = np.linspace(0, 1, height, dtype=np.float32)
    xv, yv = np.meshgrid(x, y)

    b = (180 * (1 - yv) + 50).astype(np.uint8)
    g = (200 * xv).astype(np.uint8)
    r = (160 * (1 - xv) + 30).astype(np.uint8)
    img = cv2.merge([b, g, r])

    cv2.rectangle(img, (140, 120), (460, 420), (50, 210, 240), -1)
    cv2.circle(img, (820, 300), 130, (230, 70, 70), -1)
    cv2.ellipse(img, (1000, 520), (150, 80), -20, 0, 360, (80, 220, 100), -1)
    cv2.putText(img, "Sample Scene", (420, 660), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3, cv2.LINE_AA)

    # Add a removable object for practice
    cv2.rectangle(img, (560, 420), (760, 520), (10, 10, 10), -1)
    cv2.putText(img, "REMOVE", (575, 482), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)

    noise = np.random.normal(0, 6, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return img


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sample input image for Image Cleanup Lab")
    parser.add_argument("--output", default="samples/input.jpg")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    img = build_sample(width=args.width, height=args.height)
    cv2.imwrite(str(out), img)
    print(f"Saved sample image: {out}")


if __name__ == "__main__":
    main()
