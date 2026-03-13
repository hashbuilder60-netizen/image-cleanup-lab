import argparse

import cv2
import numpy as np

from common import ensure_parent, read_color


def detect_watermark_like_regions(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Highlight bright low-contrast text-like regions often seen in watermarks.
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    high = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        41,
        -7,
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned = cv2.morphologyEx(high, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)

    return cleaned


def overlay_boxes(image: np.ndarray, mask: np.ndarray, min_area: int = 250) -> np.ndarray:
    out = image.copy()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 255), 2)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect likely watermark-like regions (analysis only)")
    parser.add_argument("--input", required=True)
    parser.add_argument("--overlay-output", required=True)
    parser.add_argument("--mask-output", required=True)
    args = parser.parse_args()

    image = read_color(args.input)
    mask = detect_watermark_like_regions(image)
    overlay = overlay_boxes(image, mask)

    ensure_parent(args.overlay_output)
    ensure_parent(args.mask_output)
    cv2.imwrite(args.overlay_output, overlay)
    cv2.imwrite(args.mask_output, mask)

    print(f"Saved detection overlay: {args.overlay_output}")
    print(f"Saved detection mask: {args.mask_output}")


if __name__ == "__main__":
    main()
