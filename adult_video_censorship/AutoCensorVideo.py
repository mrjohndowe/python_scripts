
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# AUTOCENSORVIDEO - ONE VIDEO PER RUN
# ============================================================

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / "config.json"
OUTPUT_DIR = ROOT / "output"

DEFAULT_CONFIG = {
    "face_detection": True,
    "private_detection": True,
    "private_model": "models/private_regions.pt",
    "private_class_ids": [],
    "confidence": 0.35,
    "detect_every_n_frames": 2,

    "overlay": {
        "face": {
            "type": "blur",
            "emoji": "😎",
            "image": "",
            "strength": 31,
            "padding": 0.15,
            "opacity": 1.0,
            "scale": 1.0,
            "color": [0, 0, 0]
        },

        "private": {
            "type": "emoji",
            "emoji": "🍑",
            "image": "",
            "strength": 31,
            "padding": 0.15,
            "opacity": 1.0,
            "scale": 1.0,
            "color": [0, 0, 0]
        }
    },

    "encoding": {
        "codec": "libx264",
        "crf": 20,
        "preset": "medium",
        "audio": "copy"
    }
}


def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(DEFAULT_CONFIG, indent=4),
            encoding="utf-8"
        )

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def select_video():
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.askopenfilename(
        title="Select ONE video to censor",
        filetypes=[
            ("Video Files", "*.mp4 *.mkv *.mov *.avi *.webm *.m4v"),
            ("All Files", "*.*")
        ]
    )

    root.destroy()

    if not filename:
        return None

    return Path(filename)


def get_ffmpeg():
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")

    if not ffmpeg or not ffprobe:
        raise RuntimeError(
            "FFmpeg and FFprobe must be installed and added to PATH."
        )

    return ffmpeg, ffprobe


def get_video_info(video, ffprobe):
    result = subprocess.check_output([
        ffprobe,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-show_entries", "format=duration",
        "-of", "json",
        str(video)
    ], text=True)

    data = json.loads(result)
    stream = data["streams"][0]

    rate = stream["r_frame_rate"].split("/")
    fps = float(rate[0]) / float(rate[1])

    width = int(stream["width"])
    height = int(stream["height"])
    duration = float(data["format"]["duration"])

    return width, height, fps, duration


def make_emoji(emoji, width, height):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("seguiemj.ttf", max(16, int(height * 0.85)))
    except Exception:
        font = ImageFont.load_default()

    draw.text((0, 0), emoji, font=font, embedded_color=True)
    return image


def apply_overlay(frame, box, settings):
    """
    Supported:
      blur
      pixelate
      emoji
      box
      image
    """

    height, width = frame.shape[:2]

    x1, y1, x2, y2 = map(int, box)

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(width, x2)
    y2 = min(height, y2)

    if x2 <= x1 or y2 <= y1:
        return

    # Expand bounding box
    padding = float(settings.get("padding", 0.15))

    pad_x = int((x2 - x1) * padding)
    pad_y = int((y2 - y1) * padding)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(width, x2 + pad_x)
    y2 = min(height, y2 + pad_y)

    # Optional scaling
    scale = float(settings.get("scale", 1.0))

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    box_w = max(2, int((x2 - x1) * scale))
    box_h = max(2, int((y2 - y1) * scale))

    x1 = max(0, center_x - box_w // 2)
    y1 = max(0, center_y - box_h // 2)
    x2 = min(width, x1 + box_w)
    y2 = min(height, y1 + box_h)

    roi = frame[y1:y2, x1:x2].copy()

    overlay_type = settings.get("type", "blur").lower()
    strength = max(3, int(settings.get("strength", 31)))
    opacity = max(0.0, min(1.0, float(settings.get("opacity", 1.0))))

    if overlay_type == "blur":
        if strength % 2 == 0:
            strength += 1

        effect = cv2.GaussianBlur(
            roi,
            (strength, strength),
            0
        )

    elif overlay_type == "pixelate":
        block = max(2, strength)

        small = cv2.resize(
            roi,
            (
                max(1, roi.shape[1] // block),
                max(1, roi.shape[0] // block)
            ),
            interpolation=cv2.INTER_LINEAR
        )

        effect = cv2.resize(
            small,
            (roi.shape[1], roi.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

    elif overlay_type == "box":
        effect = roi.copy()
        effect[:] = settings.get("color", [0, 0, 0])

    elif overlay_type in ("emoji", "image"):
        if overlay_type == "image" and settings.get("image"):
            image_path = Path(settings["image"])

            if image_path.exists():
                icon = Image.open(image_path).convert("RGBA")
            else:
                icon = make_emoji(
                    settings.get("emoji", "🟣"),
                    roi.shape[1],
                    roi.shape[0]
                )
        else:
            icon = make_emoji(
                settings.get("emoji", "🟣"),
                roi.shape[1],
                roi.shape[0]
            )

        icon = icon.resize(
            (roi.shape[1], roi.shape[0]),
            Image.Resampling.LANCZOS
        )

        background = Image.fromarray(
            cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        ).convert("RGBA")

        background.alpha_composite(icon)

        effect = cv2.cvtColor(
            np.array(background.convert("RGB")),
            cv2.COLOR_RGB2BGR
        )

    else:
        effect = cv2.GaussianBlur(roi, (31, 31), 0)

    if opacity < 1.0:
        frame[y1:y2, x1:x2] = cv2.addWeighted(
            roi, 1.0 - opacity,
            effect, opacity,
            0
        )
    else:
        frame[y1:y2, x1:x2] = effect


def detect_faces(detector, frame):
    faces = []

    if detector is None:
        return faces

    height, width = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = detector.process(rgb)

    if result.detections:
        for detection in result.detections:
            box = detection.location_data.relative_bounding_box

            x1 = int(box.xmin * width)
            y1 = int(box.ymin * height)
            x2 = x1 + int(box.width * width)
            y2 = y1 + int(box.height * height)

            faces.append((x1, y1, x2, y2))

    return faces


def detect_private_regions(model, frame, confidence, class_ids):
    regions = []

    if model is None:
        return regions

    results = model.predict(
        frame,
        conf=confidence,
        verbose=False
    )

    allowed = set(class_ids)

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            class_id = int(box.cls[0])

            if allowed and class_id not in allowed:
                continue

            coords = box.xyxy[0].tolist()
            regions.append(tuple(map(int, coords)))

    return regions


def main():
    config = load_config()

    video = select_video()

    if video is None:
        print("No video selected.")
        return

    if not video.is_file():
        print("Invalid video.")
        return

    ffmpeg, ffprobe = get_ffmpeg()

    import mediapipe as mp

    face_detector = None

    if config.get("face_detection", True):
        face_detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=config.get("confidence", 0.35)
        )

    private_model = None

    if config.get("private_detection", True):
        model_path = ROOT / config.get(
            "private_model",
            "models/private_regions.pt"
        )

        if model_path.exists():
            try:
                from ultralytics import YOLO
                private_model = YOLO(str(model_path))
            except Exception as error:
                print("Could not load private detector:", error)
        else:
            print("Private-region model not installed.")
            print("Private-region detection will be skipped.")

    width, height, fps, duration = get_video_info(video, ffprobe)

    OUTPUT_DIR.mkdir(exist_ok=True)

    output = OUTPUT_DIR / f"{video.stem}_censored.mp4"
    temporary = OUTPUT_DIR / f"{video.stem}_temporary.mp4"

    capture = cv2.VideoCapture(str(video))

    writer = cv2.VideoWriter(
        str(temporary),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    face_boxes = []
    private_boxes = []

    interval = max(
        1,
        int(config.get("detect_every_n_frames", 2))
    )

    frame_number = 0

    print()
    print("AUTOCENSORVIDEO")
    print("============================")
    print("Input :", video)
    print("Output:", output)
    print("Duration:", round(duration, 2), "seconds")
    print("Processing ONE video...")
    print()

    try:
        while True:
            success, frame = capture.read()

            if not success:
                break

            if frame_number % interval == 0:
                face_boxes = detect_faces(
                    face_detector,
                    frame
                )

                private_boxes = detect_private_regions(
                    private_model,
                    frame,
                    config.get("confidence", 0.35),
                    config.get("private_class_ids", [])
                )

            for box in face_boxes:
                apply_overlay(
                    frame,
                    box,
                    config["overlay"]["face"]
                )

            for box in private_boxes:
                apply_overlay(
                    frame,
                    box,
                    config["overlay"]["private"]
                )

            writer.write(frame)
            frame_number += 1

            if frame_number % int(fps * 10) == 0:
                print(
                    f"Processed {frame_number / fps:.0f}"
                    f" / {duration:.0f} seconds"
                )

    finally:
        capture.release()
        writer.release()

        if face_detector:
            face_detector.close()

    print()
    print("Encoding final video...")

    encoding = config.get("encoding", {})

    subprocess.run([
        ffmpeg,
        "-y",
        "-i", str(temporary),
        "-i", str(video),
        "-map", "0:v:0",
        "-map", "1:a?",
        "-c:v", encoding.get("codec", "libx264"),
        "-crf", str(encoding.get("crf", 20)),
        "-preset", encoding.get("preset", "medium"),
        "-c:a", encoding.get("audio", "copy"),
        "-shortest",
        str(output)
    ], check=True)

    temporary.unlink(missing_ok=True)

    print()
    print("COMPLETE")
    print("Saved:", output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as error:
        print("\nERROR:", error)
        sys.exit(1)
