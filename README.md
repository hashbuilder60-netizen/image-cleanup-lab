# Image Manipulation Tool

A beginner-friendly Python project for broader image editing and controlled cleanup:
- Manipulate images interactively with color, geometry, and effect controls
- Remove unwanted objects from your own photos using masks + inpainting
- Add your own watermark and remove it later with the saved mask
- Detect watermark-like regions for analysis
- Build smarter masks with GrabCut + interactive painting

## Safety and Usage Policy
Use this project only on images you own or have permission to edit.
Do not use it to remove third-party copyright or ownership marks.

## Features
1. `image_manipulator.py`
- Interactive editor for image transformation and visual effects.
- Includes gamma, contrast, brightness, blur, sharpen, rotate, scale, shift, flip, grayscale, channel split, and stylized effects.

2. `add_watermark.py`
- Adds a text watermark to an image.
- Exports both the watermarked image and an exact watermark mask.

3. `remove_own_watermark.py`
- Removes your own previously added watermark using the saved mask.

4. `remove_object.py`
- Removes any selected object region from your own image using a user-provided mask.

5. `detect_watermark.py`
- Heuristically detects likely watermark-like regions and outputs preview + mask.

6. `auto_mask.py`
- Generates an initial object mask from a rectangle using GrabCut.

7. `mask_painter.py`
- Lets you paint/erase a mask interactively for precise object removal.

8. `make_sample.py`
- Generates a ready-to-use sample image at `samples/input.jpg`.

## Setup
```powershell
pip install -r requirements.txt
```

## First Run (Create a Sample Input)
```powershell
python src/make_sample.py --output samples/input.jpg
```

## Quick Start: General Manipulation

Run the interactive editor:
```powershell
python src/image_manipulator.py --input samples/input.jpg
```

Keys:
- `s` save current image
- `r` reset sliders
- `q` quit

Main editor controls:
- `Gamma x100`, `Contrast`, `Brightness`
- `BitDepth`, `Blur`, `Sharpen`
- `Rotate`, `Scale x100`, `ShiftX`, `ShiftY`, `Flip`
- `ChannelSplit`, `Mode`, `Effect`, `EffectAmt`

## Quick Start: Cleanup Tools

### 1) Add your watermark
```powershell
python src/add_watermark.py \
  --input samples/input.jpg \
  --output output/watermarked.jpg \
  --mask-output output/watermark_mask.png \
  --text "@hashbuilder" \
  --position bottom-right
```

### 2) Remove your own watermark (using saved mask)
```powershell
python src/remove_own_watermark.py \
  --input output/watermarked.jpg \
  --mask output/watermark_mask.png \
  --output output/cleaned.jpg
```

### 3) Detect watermark-like areas (analysis)
```powershell
python src/detect_watermark.py \
  --input samples/input.jpg \
  --overlay-output output/detect_overlay.jpg \
  --mask-output output/detect_mask.png
```

## Smarter Object Removal Workflow

### Step A: Auto-generate initial mask
Use a rectangle around the black `REMOVE` block in the sample scene.
```powershell
python src/auto_mask.py \
  --input samples/input.jpg \
  --mask-output output/object_mask_auto.png \
  --preview-output output/object_mask_preview.jpg \
  --x 540 --y 400 --w 250 --h 140
```

### Step B: Refine mask manually (optional but recommended)
```powershell
python src/mask_painter.py \
  --input samples/input.jpg \
  --mask-output output/object_mask_refined.png
```
Mask editor controls:
- `d` draw (white = remove)
- `e` erase
- `[` / `]` change brush size
- `c` clear
- `s` save mask
- `q` quit

### Step C: Remove the object with final mask
```powershell
python src/remove_object.py \
  --input samples/input.jpg \
  --mask output/object_mask_refined.png \
  --output output/object_removed.jpg
```

## GitHub Push
```powershell
git add .
git commit -m "Update workflows"
git push
```
