import argparse

import cv2
import numpy as np

from common import ensure_parent, read_color


drawing = False
brush = 12
mode_draw = True


def on_mouse(event: int, x: int, y: int, _flags: int, param: dict) -> None:
    global drawing
    image = param["image"]
    mask = param["mask"]

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

    if drawing and event in (cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONDOWN):
        color = 255 if mode_draw else 0
        cv2.circle(mask, (x, y), brush, color, -1)

        # Visual brush hint overlay
        if mode_draw:
            cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
        else:
            cv2.circle(image, (x, y), 1, (255, 0, 0), -1)


def compose_view(base: np.ndarray, mask: np.ndarray) -> np.ndarray:
    red = np.zeros_like(base)
    red[:, :, 2] = 255
    view = base.copy()
    idx = mask > 0
    # OpenCV can return None for empty selections; guard first.
    if np.any(idx):
        view[idx] = cv2.addWeighted(base[idx], 0.35, red[idx], 0.65, 0)
    return view


def main() -> None:
    global brush, mode_draw

    parser = argparse.ArgumentParser(description="Interactive mask painter for object removal")
    parser.add_argument("--input", required=True)
    parser.add_argument("--mask-output", required=True)
    parser.add_argument("--brush", type=int, default=12)
    args = parser.parse_args()

    base = read_color(args.input)
    work = base.copy()
    mask = np.zeros(base.shape[:2], dtype=np.uint8)

    brush = max(1, args.brush)

    window = "Mask Painter"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window, on_mouse, {"image": work, "mask": mask})

    print("Controls: d=draw, e=erase, ] increase brush, [ decrease brush, c=clear, s=save, q=quit")

    while True:
        view = compose_view(base, mask)
        info = f"mode={'draw' if mode_draw else 'erase'} brush={brush} white=remove region"
        cv2.putText(view, info, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow(window, view)
        key = cv2.waitKey(16) & 0xFF

        if key == ord("q"):
            break
        if key == ord("d"):
            mode_draw = True
        if key == ord("e"):
            mode_draw = False
        if key == ord("]"):
            brush = min(100, brush + 2)
        if key == ord("["):
            brush = max(1, brush - 2)
        if key == ord("c"):
            mask[:, :] = 0
        if key == ord("s"):
            ensure_parent(args.mask_output)
            cv2.imwrite(args.mask_output, mask)
            print(f"Saved mask: {args.mask_output}")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
