
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# AUTOCENSORVIDEO
# Windows | Python 3.12+ | MediaPipe Tasks + NudeNet
# Processes ONE selected video per execution.
# ============================================================

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
OUTPUT_DIR = ROOT / "output"
MODEL_DIR = ROOT / "models"

SUPPORTED_VIDEO = (
    "*.mp4 *.mkv *.mov *.avi *.webm *.m4v *.wmv"
)


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

DEFAULT_CONFIG = {
    "face_detection": True,
    "private_detection": True,

    "face_model": "models/face_detector.tflite",
    "private_confidence": 0.35,
    "private_labels": [
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
        "BUTTOCKS_EXPOSED",
        "ANUS_EXPOSED"
    ],

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
    """Create config.json if absent and merge missing nested defaults."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=4), encoding="utf-8")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value.copy() if isinstance(value, dict) else value

    for section, defaults in DEFAULT_CONFIG["overlay"].items():
        config["overlay"].setdefault(section, {})
        for key, value in defaults.items():
            config["overlay"][section].setdefault(key, value)

    config.setdefault("encoding", {})
    for key, value in DEFAULT_CONFIG["encoding"].items():
        config["encoding"].setdefault(key, value)

    return config


# ------------------------------------------------------------
# FILE SELECTION
# ------------------------------------------------------------

def select_video() -> Path | None:
    """Select exactly one video using a Windows file picker."""

    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.askopenfilename(
        title="AutoCensorVideo - Select ONE video",
        filetypes=[
            ("Video files", SUPPORTED_VIDEO),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if not filename:
        return None

    return Path(filename)


# ------------------------------------------------------------
# FFMPEG
# ------------------------------------------------------------

def find_ffmpeg():
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg was not found in PATH.\n"
            "Install FFmpeg and restart PowerShell."
        )

    if not ffprobe:
        raise RuntimeError(
            "FFprobe was not found in PATH."
        )

    return ffmpeg, ffprobe


def get_video_info(video: Path, ffprobe: str):
    """Return video width, height, FPS, and duration."""

    command = [
        ffprobe,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate",
        "-show_entries",
        "format=duration",
        "-of", "json",
        str(video)
    ]

    result = subprocess.check_output(
        command,
        text=True
    )

    data = json.loads(result)

    stream = data["streams"][0]

    width = int(stream["width"])
    height = int(stream["height"])

    rate = stream.get("r_frame_rate", "30/1")
    numerator, denominator = rate.split("/")

    fps = float(numerator) / float(denominator)

    duration = float(
        data.get("format", {}).get("duration", 0)
    )

    return width, height, fps, duration


# ------------------------------------------------------------
# MEDIAPIPE FACE DETECTOR
# ------------------------------------------------------------

def create_face_detector(config):
    """Create the modern MediaPipe Tasks face detector."""

    if not config.get("face_detection", True):
        return None

    import mediapipe as mp

    model_path = ROOT / config.get(
        "face_model",
        "models/face_detector.tflite"
    )

    if not model_path.exists():
        raise RuntimeError(
            f"Face detection model missing:\n{model_path}\n\n"
            "Download the model using the README instructions."
        )

    options = mp.tasks.vision.FaceDetectorOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(model_path)
        ),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        min_detection_confidence=float(
            config.get("confidence", 0.35)
        )
    )

    return mp.tasks.vision.FaceDetector.create_from_options(
        options
    )


def detect_faces(detector, frame, timestamp_ms):
    """Detect faces using MediaPipe Tasks."""

    if detector is None:
        return []

    import mediapipe as mp

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = detector.detect_for_video(
        image,
        timestamp_ms
    )

    boxes = []

    for detection in result.detections:
        box = detection.bounding_box

        x1 = box.origin_x
        y1 = box.origin_y

        x2 = x1 + box.width
        y2 = y1 + box.height

        boxes.append(
            (x1, y1, x2, y2)
        )

    return boxes


# ------------------------------------------------------------
# NUDENET PRIVATE-REGION DETECTOR
# ------------------------------------------------------------

PRIVATE_LABELS_DEFAULT = {
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "BUTTOCKS_EXPOSED",
    "ANUS_EXPOSED",
}


def create_private_detector(config):
    """Initialize NudeNet's bundled pretrained 320n ONNX detector."""
    if not config.get("private_detection", True):
        print("[INFO] Private-region detection is disabled in config.")
        return None

    try:
        from nudenet import NudeDetector
        print("[INFO] Loading NudeNet pretrained private-region detector...")
        detector = NudeDetector()
        print("[INFO] NudeNet detector ready (bundled 320n model).")
        return detector
    except Exception as error:
        print("[WARNING] NudeNet initialization failed:", error)
        print('[WARNING] Install it with: python -m pip install "nudenet>=3.4.2"')
        return None


def detect_private_regions(detector, frame, confidence, labels):
    """Detect configured exposed-region labels; NudeNet boxes are x,y,w,h."""
    if detector is None:
        return []

    allowed = set(labels or PRIVATE_LABELS_DEFAULT)
    try:
        detections = detector.detect(frame)
    except Exception as error:
        print("[WARNING] NudeNet frame detection failed:", error)
        return []

    boxes = []
    for item in detections:
        label = str(item.get("class", "")).upper()
        score = float(item.get("score", 0.0))
        if label not in allowed or score < float(confidence):
            continue

        box = item.get("box", [])
        if len(box) != 4:
            continue
        x, y, w, h = map(int, box)
        boxes.append((x, y, x + w, y + h))

    return boxes


# ------------------------------------------------------------
# OVERLAY RENDERING
# ------------------------------------------------------------

def render_emoji(emoji, width, height):
    """Render emoji to transparent RGBA image."""

    image = Image.new(
        "RGBA",
        (max(1, width), max(1, height)),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "seguiemj.ttf",
            max(16, int(height * 0.9))
        )
    except Exception:
        font = ImageFont.load_default()

    draw.text(
        (0, 0),
        emoji,
        font=font,
        embedded_color=True
    )

    return image


def apply_overlay(frame, box, settings):
    """Apply configured overlay to a bounding box."""

    frame_height, frame_width = frame.shape[:2]

    x1, y1, x2, y2 = map(int, box)

    x1 = max(0, x1)
    y1 = max(0, y1)

    x2 = min(frame_width, x2)
    y2 = min(frame_height, y2)

    if x2 <= x1 or y2 <= y1:
        return

    # Padding
    padding = float(
        settings.get("padding", 0.15)
    )

    pad_x = int((x2 - x1) * padding)
    pad_y = int((y2 - y1) * padding)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)

    x2 = min(frame_width, x2 + pad_x)
    y2 = min(frame_height, y2 + pad_y)

    # Scale overlay
    scale = max(
        0.1,
        float(settings.get("scale", 1.0))
    )

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    box_width = max(
        2,
        int((x2 - x1) * scale)
    )

    box_height = max(
        2,
        int((y2 - y1) * scale)
    )

    x1 = max(0, center_x - box_width // 2)
    y1 = max(0, center_y - box_height // 2)

    x2 = min(frame_width, x1 + box_width)
    y2 = min(frame_height, y1 + box_height)

    roi = frame[y1:y2, x1:x2].copy()

    if roi.size == 0:
        return

    overlay_type = settings.get(
        "type", "blur"
    ).lower()

    strength = max(
        3,
        int(settings.get("strength", 31))
    )

    opacity = max(
        0.0,
        min(
            1.0,
            float(settings.get("opacity", 1.0))
        )
    )

    # BLUR
    if overlay_type == "blur":

        if strength % 2 == 0:
            strength += 1

        effect = cv2.GaussianBlur(
            roi,
            (strength, strength),
            0
        )

    # PIXELATION
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

    # SOLID BOX
    elif overlay_type == "box":

        effect = roi.copy()

        effect[:] = settings.get(
            "color", [0, 0, 0]
        )

    # EMOJI OR CUSTOM IMAGE
    elif overlay_type in ("emoji", "image"):

        image_path = settings.get("image", "")

        if (
            overlay_type == "image"
            and image_path
            and Path(image_path).exists()
        ):

            icon = Image.open(
                image_path
            ).convert("RGBA")

        else:

            icon = render_emoji(
                settings.get("emoji", "🟣"),
                roi.shape[1],
                roi.shape[0]
            )

        icon = icon.resize(
            (roi.shape[1], roi.shape[0]),
            Image.Resampling.LANCZOS
        )

        background = Image.fromarray(
            cv2.cvtColor(
                roi,
                cv2.COLOR_BGR2RGB
            )
        ).convert("RGBA")

        background.alpha_composite(icon)

        effect = cv2.cvtColor(
            np.array(
                background.convert("RGB")
            ),
            cv2.COLOR_RGB2BGR
        )

    else:

        effect = cv2.GaussianBlur(
            roi,
            (31, 31),
            0
        )

    # Apply opacity
    if opacity < 1.0:

        frame[y1:y2, x1:x2] = cv2.addWeighted(
            roi,
            1.0 - opacity,
            effect,
            opacity,
            0
        )

    else:

        frame[y1:y2, x1:x2] = effect


# ------------------------------------------------------------
# VIDEO PROCESSING
# ------------------------------------------------------------

def process_video(video, config):
    ffmpeg, ffprobe = find_ffmpeg()

    width, height, fps, duration = get_video_info(
        video,
        ffprobe
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output = OUTPUT_DIR / (
        video.stem + "_censored.mp4"
    )

    temporary = OUTPUT_DIR / (
        video.stem + "_processed_temp.avi"
    )

    capture = cv2.VideoCapture(
        str(video)
    )

    if not capture.isOpened():
        raise RuntimeError(
            "Could not open selected video."
        )

    writer = cv2.VideoWriter(
        str(temporary),
        cv2.VideoWriter_fourcc(*"MJPG"),
        fps,
        (width, height)
    )

    if not writer.isOpened():
        capture.release()
        raise RuntimeError("Could not initialize MJPEG video writer.")

    face_detector = None
    private_detector = None

    ffprobe -v error -show_streams .\output\20261029_062921_processed_temp.avi

    try:

        face_detector = create_face_detector(
            config
        )

        private_detector = create_private_detector(
            config
        )

        face_boxes = []
        private_boxes = []

        detection_interval = max(
            1,
            int(
                config.get(
                    "detect_every_n_frames", 2
                )
            )
        )

        frame_number = 0

        print()
        print("================================")
        print("AUTOCENSORVIDEO")
        print("================================")
        print("Input:", video)
        print("Output:", output)
        print("Resolution:", width, "x", height)
        print("FPS:", round(fps, 2))
        print("Private detection:", "enabled" if private_detector else "disabled")
        print("Duration:", round(duration, 2))
        print("--------------------------------")

        while True:

            success, frame = capture.read()

            if not success:
                break

            timestamp_ms = int(
                frame_number * 1000 / fps
            )

            # Run detectors periodically
            if frame_number % detection_interval == 0:

                face_boxes = detect_faces(
                    face_detector,
                    frame,
                    timestamp_ms
                )

                private_boxes = detect_private_regions(
                    private_detector,
                    frame,
                    config.get("private_confidence", config.get("confidence", 0.35)),
                    config.get("private_labels", list(PRIVATE_LABELS_DEFAULT))
                )

            # Face overlays
            face_settings = config["overlay"]["face"]

            for box in face_boxes:

                apply_overlay(
                    frame,
                    box,
                    face_settings
                )

            # Private-region overlays
            private_settings = config["overlay"]["private"]

            for box in private_boxes:

                apply_overlay(
                    frame,
                    box,
                    private_settings
                )

            writer.write(frame)

            frame_number += 1

            if frame_number % max(
                1, int(fps * 10)
            ) == 0:

                print(
                    f"Processed "
                    f"{frame_number / fps:.0f} / "
                    f"{duration:.0f} seconds"
                )

    finally:

        capture.release()
        writer.release()

        if face_detector:
            face_detector.close()

    # --------------------------------------------------------
    # FINAL ENCODING + ORIGINAL AUDIO
    # --------------------------------------------------------

    encoding = config.get(
        "encoding", {}
    )

    print()
    print("Encoding final MP4...")

    command = [
        ffmpeg,
        "-y",

        "-i", str(temporary),
        "-i", str(video),

        "-map", "0:v:0",
        "-map", "1:a?",

        "-c:v", encoding.get(
            "codec", "libx264"
        ),

        "-crf", str(
            encoding.get("crf", 20)
        ),

        "-preset", encoding.get(
            "preset", "medium"
        ),

        "-c:a", encoding.get(
            "audio", "copy"
        ),

        "-shortest",
        str(output)
    ]

    subprocess.run(
        command,
        check=True
    )

    temporary.unlink(
        missing_ok=True
    )

    print()
    print("================================")
    print("PROCESSING COMPLETE")
    print("================================")
    print("Saved:", output)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print("AutoCensorVideo starting...")

    config = load_config()

    video = select_video()

    if video is None:

        print("No video selected.")
        return

    if not video.exists():

        print("Selected file does not exist.")
        return

    process_video(
        video,
        config
    )


# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print("\nProcessing cancelled.")

    except Exception as error:

        print("\nERROR:", error)
        sys.exit(1)
