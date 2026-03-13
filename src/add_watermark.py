import argparse

import cv2
import numpy as np

from common import ensure_parent, read_color


def position_from_name(name: str, w: int, h: int, margin: int, text_w: int, text_h: int) -> tuple[int, int]:
    n = name.lower()
    if n == "top-left":
        return margin, margin + text_h
    if n == "top-right":
        return w - text_w - margin, margin + text_h
    if n == "bottom-left":
        return margin, h - margin
    return w - text_w - margin, h - margin


def main() -> None:
    parser = argparse.ArgumentParser(description="Add your own text watermark and export its mask")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mask-output", required=True)
    parser.add_argument("--text", default="@mywatermark")
    parser.add_argument("--position", choices=["top-left", "top-right", "bottom-left", "bottom-right"], default="bottom-right")
    parser.add_argument("--alpha", type=float, default=0.45, help="0.0 to 1.0")
    parser.add_argument("--scale", type=float, default=1.2)
    parser.add_argument("--thickness", type=int, default=2)
    parser.add_argument("--margin", type=int, default=20)
    args = parser.parse_args()

    image = read_color(args.input)
    h, w = image.shape[:2]

    alpha = float(np.clip(args.alpha, 0.0, 1.0))
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv2.getTextSize(args.text, font, args.scale, args.thickness)
    x, y = position_from_name(args.position, w, h, args.margin, text_w, text_h)

    overlay = image.copy()
    cv2.putText(overlay, args.text, (x, y), font, args.scale, (255, 255, 255), args.thickness, cv2.LINE_AA)

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.putText(mask, args.text, (x, y), font, args.scale, 255, args.thickness + 2, cv2.LINE_AA)

    result = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

    ensure_parent(args.output)
    ensure_parent(args.mask_output)
    cv2.imwrite(args.output, result)
    cv2.imwrite(args.mask_output, mask)
    print(f"Saved watermarked image: {args.output}")
    print(f"Saved watermark mask: {args.mask_output}")


if __name__ == "__main__":
    main()
