import argparse

import cv2

from common import ensure_parent, read_color, read_mask


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove your own watermark using saved mask")
    parser.add_argument("--input", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--radius", type=int, default=5, help="Inpaint radius")
    args = parser.parse_args()

    image = read_color(args.input)
    mask = read_mask(args.mask)

    if image.shape[:2] != mask.shape[:2]:
        raise ValueError("Mask size must match image size")

    cleaned = cv2.inpaint(image, mask, args.radius, cv2.INPAINT_TELEA)

    ensure_parent(args.output)
    cv2.imwrite(args.output, cleaned)
    print(f"Saved cleaned image: {args.output}")


if __name__ == "__main__":
    main()
