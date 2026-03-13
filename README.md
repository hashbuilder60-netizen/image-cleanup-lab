# Image Cleanup Lab

A beginner-friendly Python project for safe image cleanup workflows:
- Remove unwanted objects from your own photos using masks + inpainting
- Add your own watermark and remove it later (with saved mask)
- Detect watermark-like regions for analysis
- Build smarter masks with GrabCut + interactive painting

## Safety and Usage Policy
Use this project only on images you own or have permission to edit.
Do not use it to remove third-party copyright or ownership marks.

## Features
1. `add_watermark.py`
- Adds a text watermark to an image.
- Exports both the watermarked image and an exact watermark mask.

2. `remove_own_watermark.py`
- Removes your own previously added watermark using the saved mask.

3. `remove_object.py`
- Removes any selected object region from your own image using a user-provided mask.

4. `detect_watermark.py`
- Heuristically detects likely watermark-like regions and outputs preview + mask.

5. `auto_mask.py`
- Generates an initial object mask from a rectangle using GrabCut.

6. `mask_painter.py`
- Lets you paint/erase a mask interactively for precise object removal.

## Setup
```powershell
pip install -r requirements.txt
```

## Quick Start

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
Use a rectangle around the object.
```powershell
python src/auto_mask.py \
  --input samples/input.jpg \
  --mask-output output/object_mask_auto.png \
  --preview-output output/object_mask_preview.jpg \
  --x 200 --y 120 --w 300 --h 260
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
git commit -m "Add smart mask workflow"
git push
```
