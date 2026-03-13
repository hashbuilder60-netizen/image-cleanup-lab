import argparse

import cv2
import numpy as np

from common import ensure_parent, read_color


def build_rect(x: int, y: int, w: int, h: int, image_w: int, image_h: int) -> tuple[int, int, int, int]:
    x = max(0, min(x, image_w - 1))
    y = max(0, min(y, image_h - 1))
    w = max(1, min(w, image_w - x))
    h = max(1, min(h, image_h - y))
    return x, y, w, h


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate object mask automatically using GrabCut")
    parser.add_argument("--input", required=True)
    parser.add_argument("--mask-output", required=True)
    parser.add_argument("--preview-output", required=True)
    parser.add_argument("--x", type=int, required=True, help="Rectangle x")
    parser.add_argument("--y", type=int, required=True, help="Rectangle y")
    parser.add_argument("--w", type=int, required=True, help="Rectangle width")
    parser.add_argument("--h", type=int, required=True, help="Rectangle height")
    parser.add_argument("--iters", type=int, default=5)
    args = parser.parse_args()

    image = read_color(args.input)
    ih, iw = image.shape[:2]

    rect = build_rect(args.x, args.y, args.w, args.h, iw, ih)

    mask = np.zeros((ih, iw), np.uint8)
    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)

    cv2.grabCut(image, mask, rect, bg_model, fg_model, args.iters, cv2.GC_INIT_WITH_RECT)

    # probable/definite foreground -> white
    binary = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

    preview = image.copy()
    cv2.rectangle(preview, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 255), 2)
    red = np.zeros_like(preview)
    red[:, :, 2] = 255
    blend_mask = binary > 0
    preview[blend_mask] = cv2.addWeighted(preview[blend_mask], 0.35, red[blend_mask], 0.65, 0)

    ensure_parent(args.mask_output)
    ensure_parent(args.preview_output)
    cv2.imwrite(args.mask_output, binary)
    cv2.imwrite(args.preview_output, preview)

    print(f"Saved mask: {args.mask_output}")
    print(f"Saved preview: {args.preview_output}")


if __name__ == "__main__":
    main()
