
# AutoCensorVideo

Single-video censorship utility for Windows.

## Features

- Select one video at a time.
- No automatic folder processing.
- Face detection using MediaPipe Tasks.
- Optional custom YOLO private-region detector.
- Blur, pixelation, emoji, image, or solid-box overlays.
- Configurable overlay settings.
- Original video remains unchanged.
- Audio copied from original video.
- MP4 output.

## Requirements

- Windows 10 or Windows 11
- Python 3.14, 64-bit
- FFmpeg and FFprobe
- MediaPipe face detection model

## Installation

Open PowerShell in this project folder.

Create the virtual environment:

    py -3.14 -m venv .venv

Activate it:

    .\.venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install --upgrade pip

    pip install -r requirements.txt

## FFmpeg

Install FFmpeg and make sure both commands work:

    ffmpeg -version
    ffprobe -version

## Face Detection Model

Create the models folder:

    New-Item -ItemType Directory -Force .\models

Download the face detector:

    Invoke-WebRequest `
      -Uri "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite" `
      -OutFile ".\models\face_detector.tflite"

## Run

    python .\AutoCensorVideo.py

Choose ONE video in the file picker.

Output:

    output\<video-name>_censored.mp4

## Overlay Settings

Edit config.json.

Supported overlay types:

- blur
- pixelate
- emoji
- box
- image

Example emoji:

    "type": "emoji",
    "emoji": "🍑"

Example pixelation:

    "type": "pixelate",
    "strength": 18

Example blur:

    "type": "blur",
    "strength": 51

Example black box:

    "type": "box",
    "color": [0, 0, 0]

Example custom image:

    "type": "image",
    "image": "overlays/censor.png"

## Configuration

- confidence: Detection confidence threshold.
- detect_every_n_frames: Detection interval.
- padding: Expand detection area.
- scale: Resize overlay relative to detection box.
- opacity: 0.0 to 1.0.
- strength: Blur kernel or pixelation block size.
- crf: Video quality setting.
- preset: Encoding speed/quality setting.

## Private-Region Detection

Private-region detection requires a compatible custom-trained
YOLO model.

Place it here:

    models\private_regions.pt

The model must recognize the regions you want censored.

A general object detector does not automatically recognize
private anatomical regions.

## Limitations

- Face detection may miss partially hidden faces.
- Detection boxes are reused between detector frames.
- This implementation does not perform optical-flow tracking.
- Private-region detection is skipped if its model is missing.
- Always review processed videos.
- This implementation does not provide a live preview window.
