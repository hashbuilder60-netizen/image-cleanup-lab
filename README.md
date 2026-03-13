# Image Cleanup Lab

A beginner-friendly Python project for safe image cleanup workflows:
- Remove unwanted objects from your own photos using masks + inpainting
- Add your own watermark and remove it later (with saved mask)
- Detect watermark-like regions for analysis

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

### 3) Remove any object with custom mask
Create a white-on-black mask where white = object to remove.
```powershell
python src/remove_object.py \
  --input samples/input.jpg \
  --mask samples/object_mask.png \
  --output output/object_removed.jpg
```

### 4) Detect watermark-like areas
```powershell
python src/detect_watermark.py \
  --input samples/input.jpg \
  --overlay-output output/detect_overlay.jpg \
  --mask-output output/detect_mask.png
```

## GitHub Push
```powershell
git init
git add .
git commit -m "Initial commit: image cleanup lab"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```
