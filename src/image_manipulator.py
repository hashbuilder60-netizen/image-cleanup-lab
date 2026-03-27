import argparse
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from common import ensure_parent, read_color


def gamma_correct(image: np.ndarray, gamma: float) -> np.ndarray:
    normalized = image.astype(np.float32) / 255.0
    corrected = np.power(normalized, 1.0 / max(gamma, 1e-6))
    return np.clip(corrected * 255.0, 0, 255).astype(np.uint8)


def adjust_contrast_brightness(image: np.ndarray, contrast: float, brightness: float) -> np.ndarray:
    output = image.astype(np.float32) * contrast + brightness
    return np.clip(output, 0, 255).astype(np.uint8)


def quantize_bits(image: np.ndarray, bits: int) -> np.ndarray:
    bits = int(np.clip(bits, 1, 8))
    levels = 2**bits
    step = 256 / levels
    quantized = np.floor(image.astype(np.float32) / step) * step
    return np.clip(quantized, 0, 255).astype(np.uint8)


def apply_blur(image: np.ndarray, blur_level: int) -> np.ndarray:
    if blur_level <= 0:
        return image
    kernel_size = blur_level * 2 + 1
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def apply_sharpen(image: np.ndarray, sharpen_level: int) -> np.ndarray:
    if sharpen_level <= 0:
        return image
    amount = sharpen_level / 10.0
    blurred = cv2.GaussianBlur(image, (0, 0), 1.0 + sharpen_level / 8.0)
    return cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0.0)


def rotate_and_scale(image: np.ndarray, angle_deg: float, scale: float) -> np.ndarray:
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2.0, height / 2.0), angle_deg, scale)
    return cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT,
    )


def translate(image: np.ndarray, shift_x: int, shift_y: int) -> np.ndarray:
    height, width = image.shape[:2]
    matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    return cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_WRAP,
    )


def apply_flip(image: np.ndarray, flip_mode: int) -> np.ndarray:
    if flip_mode == 1:
        return cv2.flip(image, 1)
    if flip_mode == 2:
        return cv2.flip(image, 0)
    if flip_mode == 3:
        return cv2.flip(image, -1)
    return image


def channel_shift(image: np.ndarray, shift_b: int, shift_g: int, shift_r: int) -> np.ndarray:
    blue, green, red = cv2.split(image)
    blue = np.roll(blue, shift_b, axis=1)
    green = np.roll(green, shift_g, axis=1)
    red = np.roll(red, shift_r, axis=1)
    return cv2.merge([blue, green, red])


def to_gray3(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.merge([gray, gray, gray])


def edge_blend(image: np.ndarray, blend_alpha: float) -> np.ndarray:
    if blend_alpha <= 0:
        return image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    edge_rgb = cv2.merge([edges, edges, edges])
    return cv2.addWeighted(image, 1.0 - blend_alpha, edge_rgb, blend_alpha, 0.0)


def solarize(image: np.ndarray, threshold: int) -> np.ndarray:
    output = image.copy()
    mask = output >= threshold
    output[mask] = 255 - output[mask]
    return output


def apply_effect(image: np.ndarray, effect_mode: int, amount: int) -> np.ndarray:
    if effect_mode == 0:
        return image
    if effect_mode == 1:
        return cv2.bitwise_not(image)
    if effect_mode == 2:
        return solarize(image, threshold=max(0, min(255, amount * 2)))
    if effect_mode == 3:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(np.int16) + amount, 0, 255).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    if effect_mode == 4:
        alpha = max(0.0, min(1.0, amount / 100.0))
        return edge_blend(image, alpha)

    height, _ = image.shape[:2]
    output = image.copy()
    step = max(1, 12 - min(10, amount // 10))
    max_shift = max(1, amount // 4)
    for y_pos in range(0, height, step):
        shift = int(max_shift * np.sin(y_pos * 0.08))
        output[y_pos : y_pos + step, :] = np.roll(output[y_pos : y_pos + step, :], shift, axis=1)
    return output


def apply_mode(image: np.ndarray, mode: int) -> np.ndarray:
    if mode == 1:
        return to_gray3(image)
    if mode == 2:
        edges = cv2.Canny(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 80, 160)
        return cv2.merge([edges, edges, edges])
    return image


def stack_side_by_side(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    if left.shape[:2] != right.shape[:2]:
        right = cv2.resize(right, (left.shape[1], left.shape[0]), interpolation=cv2.INTER_AREA)
    return np.hstack([left, right])


def no_op(_: int) -> None:
    return


def build_output_path(save_path: str | None) -> Path:
    if save_path:
        return Path(save_path)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(__file__).resolve().parents[1] / "output" / f"manipulated_{stamp}.png"


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive image manipulation tool")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--save-path", help="Optional fixed output path used when pressing s")
    args = parser.parse_args()

    original = read_color(args.input)

    window = "Image Manipulation Tool"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    cv2.createTrackbar("Gamma x100", window, 100, 300, no_op)
    cv2.createTrackbar("Contrast", window, 100, 300, no_op)
    cv2.createTrackbar("Brightness", window, 100, 200, no_op)
    cv2.createTrackbar("BitDepth", window, 8, 8, no_op)
    cv2.createTrackbar("Blur", window, 0, 20, no_op)
    cv2.createTrackbar("Sharpen", window, 0, 20, no_op)
    cv2.createTrackbar("Flip", window, 0, 3, no_op)
    cv2.createTrackbar("Mode", window, 0, 2, no_op)
    cv2.createTrackbar("Rotate", window, 180, 360, no_op)
    cv2.createTrackbar("Scale x100", window, 100, 200, no_op)
    cv2.createTrackbar("ShiftX", window, 100, 200, no_op)
    cv2.createTrackbar("ShiftY", window, 100, 200, no_op)
    cv2.createTrackbar("ChannelSplit", window, 0, 100, no_op)
    cv2.createTrackbar("Effect", window, 0, 5, no_op)
    cv2.createTrackbar("EffectAmt", window, 0, 100, no_op)

    print("Keys: s=save current image, r=reset sliders, q=quit")
    print("Mode: 0=color, 1=grayscale, 2=edges")
    print("Flip: 0=none, 1=horizontal, 2=vertical, 3=both")
    print("Effect: 0=none, 1=invert, 2=solarize, 3=saturate, 4=edge blend, 5=glitch")

    while True:
        gamma = max(cv2.getTrackbarPos("Gamma x100", window), 1) / 100.0
        contrast = cv2.getTrackbarPos("Contrast", window) / 100.0
        brightness = cv2.getTrackbarPos("Brightness", window) - 100
        bits = max(cv2.getTrackbarPos("BitDepth", window), 1)
        blur = cv2.getTrackbarPos("Blur", window)
        sharpen = cv2.getTrackbarPos("Sharpen", window)
        flip_mode = cv2.getTrackbarPos("Flip", window)
        mode = cv2.getTrackbarPos("Mode", window)
        angle = cv2.getTrackbarPos("Rotate", window) - 180
        scale = max(cv2.getTrackbarPos("Scale x100", window), 1) / 100.0
        shift_x = cv2.getTrackbarPos("ShiftX", window) - 100
        shift_y = cv2.getTrackbarPos("ShiftY", window) - 100
        channel_amount = cv2.getTrackbarPos("ChannelSplit", window)
        effect = cv2.getTrackbarPos("Effect", window)
        effect_amount = cv2.getTrackbarPos("EffectAmt", window)

        processed = rotate_and_scale(original, angle_deg=float(angle), scale=scale)
        processed = translate(processed, shift_x=shift_x, shift_y=shift_y)
        processed = apply_flip(processed, flip_mode=flip_mode)
        processed = channel_shift(
            processed,
            shift_b=-channel_amount,
            shift_g=0,
            shift_r=channel_amount,
        )
        processed = gamma_correct(processed, gamma=gamma)
        processed = adjust_contrast_brightness(processed, contrast=contrast, brightness=float(brightness))
        processed = quantize_bits(processed, bits=bits)
        processed = apply_blur(processed, blur_level=blur)
        processed = apply_sharpen(processed, sharpen_level=sharpen)
        processed = apply_effect(processed, effect_mode=effect, amount=effect_amount)
        processed = apply_mode(processed, mode=mode)

        view = stack_side_by_side(original, processed)

        mode_name = "color" if mode == 0 else "gray" if mode == 1 else "edges"
        label = (
            f"g={gamma:.2f} c={contrast:.2f} b={brightness:+d} bits={bits} blur={blur} sharp={sharpen} "
            f"rot={angle:+d} scale={scale:.2f} shift=({shift_x:+d},{shift_y:+d}) "
            f"flip={flip_mode} split={channel_amount} mode={mode_name} fx={effect}:{effect_amount}"
        )
        cv2.putText(view, label, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow(window, view)
        key = cv2.waitKey(16) & 0xFF

        if key == ord("q"):
            break
        if key == ord("r"):
            cv2.setTrackbarPos("Gamma x100", window, 100)
            cv2.setTrackbarPos("Contrast", window, 100)
            cv2.setTrackbarPos("Brightness", window, 100)
            cv2.setTrackbarPos("BitDepth", window, 8)
            cv2.setTrackbarPos("Blur", window, 0)
            cv2.setTrackbarPos("Sharpen", window, 0)
            cv2.setTrackbarPos("Flip", window, 0)
            cv2.setTrackbarPos("Mode", window, 0)
            cv2.setTrackbarPos("Rotate", window, 180)
            cv2.setTrackbarPos("Scale x100", window, 100)
            cv2.setTrackbarPos("ShiftX", window, 100)
            cv2.setTrackbarPos("ShiftY", window, 100)
            cv2.setTrackbarPos("ChannelSplit", window, 0)
            cv2.setTrackbarPos("Effect", window, 0)
            cv2.setTrackbarPos("EffectAmt", window, 0)
        if key == ord("s"):
            output_path = build_output_path(args.save_path)
            ensure_parent(str(output_path))
            cv2.imwrite(str(output_path), processed)
            print(f"Saved image: {output_path}")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
