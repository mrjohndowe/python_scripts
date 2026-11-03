
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
# Windows | Python 3.14 | MediaPipe Tasks
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
    "private_model": "models/private_regions.pt",
    "private_detector_type": "nudenet",

    "private_class_ids": [],
    "private_labels": [],
    "private_confidence": 0.35,

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
    """Create config.json if it does not exist."""

    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, indent=4),
            encoding="utf-8"
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Fill missing configuration values.
    for key, value in DEFAULT_CONFIG.items():
        config.setdefault(key, value)

    config.setdefault("overlay", {})

    for key, value in DEFAULT_CONFIG["overlay"].items():
        config["overlay"].setdefault(key, value.copy())

    config.setdefault("encoding", DEFAULT_CONFIG["encoding"].copy())

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


def select_censoring_method(region_name):
    """Ask user how they want to censor a specific region."""

    print(f"\n{region_name} censoring options:")
    print("1. Blur")
    print("2. Pixelate")
    print("3. Emoji")
    print("4. Black box")
    print("5. Custom image")

    while True:
        choice = input(f"Select {region_name} censoring method (1-5): ").strip()

        if choice == "1":
            print("\nBlur strength options (higher = more blurry):")
            print("  15: Light blur (features still somewhat visible)")
            print("  31: Medium blur (features heavily obscured)")
            print("  51: Heavy blur (completely indistinguishable)")
            print("  71: Very heavy blur (large smear)")
            while True:
                strength = input("Enter blur strength (15-71, default 31): ").strip()
                if not strength:
                    strength = "31"
                try:
                    strength_val = int(strength)
                    if 3 <= strength_val <= 100:
                        return {"type": "blur", "strength": strength_val}
                    else:
                        print("Strength must be between 3 and 100.")
                except ValueError:
                    print("Please enter a valid number.")
        elif choice == "2":
            print("\nPixelate strength options (higher = larger blocks):")
            print("  10: Small blocks (some detail visible)")
            print("  18: Medium blocks (features obscured)")
            print("  30: Large blocks (completely pixelated)")
            while True:
                strength = input("Enter pixelate strength (2-100, default 18): ").strip()
                if not strength:
                    strength = "18"
                try:
                    strength_val = int(strength)
                    if 2 <= strength_val <= 100:
                        return {"type": "pixelate", "strength": strength_val}
                    else:
                        print("Strength must be between 2 and 100.")
                except ValueError:
                    print("Please enter a valid number.")
        elif choice == "3":
            emoji = input("Enter emoji (e.g., 😎, 🍑): ").strip()
            return {"type": "emoji", "emoji": emoji}
        elif choice == "4":
            return "box"
        elif choice == "5":
            image_path = input("Enter image path: ").strip()
            return {"type": "image", "image": image_path}
        else:
            print("Invalid choice. Please enter 1-5.")


def configure_censoring(config):
    """Ask user how they want to censor faces and private parts."""

    print("\n================================")
    print("CENSORING CONFIGURATION")
    print("================================")

    face_method = select_censoring_method("Face")

    if isinstance(face_method, dict):
        config["overlay"]["face"].update(face_method)
    else:
        config["overlay"]["face"]["type"] = face_method

    private_method = select_censoring_method("Private parts")

    if isinstance(private_method, dict):
        config["overlay"]["private"].update(private_method)
    else:
        config["overlay"]["private"]["type"] = private_method

    # Save configuration
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    print("\nConfiguration saved.")
    return config


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
# OPTIONAL YOLO PRIVATE-REGION DETECTOR
# ------------------------------------------------------------

def create_nudenet_detector(config):
    """Load NudeNet detector."""

    try:
        from nudenet import NudeDetector

        print("[INFO] Loading NudeNet detector...")

        model_path = config.get("private_model", None)

        if model_path and Path(model_path).exists():
            return NudeDetector(model_path=str(model_path))
        else:
            return NudeDetector()

    except Exception as error:
        print("[WARNING] NudeNet initialization failed:", error)
        return None


def create_private_detector(config):
    """Load an optional custom-trained YOLO model or NudeNet."""

    if not config.get("private_detection", True):
        return None

    detector_type = config.get(
        "private_detector_type",
        "yolo"
    ).lower()

    if detector_type == "nudenet":
        return create_nudenet_detector(config)

    model_path = ROOT / config.get(
        "private_model",
        "models/private_regions.pt"
    )

    if not model_path.exists():
        print(
            "[WARNING] Private-region model not found:",
            model_path
        )
        print(
            "Private-region detection is disabled until "
            "a compatible custom YOLO model is supplied."
        )
        return None

    try:
        from ultralytics import YOLO

        print("[INFO] Loading private-region detector...")

        return YOLO(str(model_path))

    except Exception as error:
        print("[WARNING] YOLO initialization failed:", error)
        return None


def detect_nudenet_regions(
    detector,
    frame,
    confidence,
    labels
):
    """Detect regions using NudeNet."""

    try:
        detections = detector.detect(frame)
    except Exception as error:
        print("[WARNING] NudeNet detection failed:", error)
        return []

    boxes = []
    allowed_labels = set(labels) if labels else None

    for detection in detections:
        label = detection.get("class", "")
        score = detection.get("score", 0.0)

        if score < confidence:
            continue

        if allowed_labels and label not in allowed_labels:
            continue

        box = detection.get("box", [0, 0, 0, 0])

        if len(box) == 4:
            x, y, width, height = box
            x2 = x + width
            y2 = y + height
            boxes.append((x, y, x2, y2))

    return boxes


def detect_private_regions(
    model,
    frame,
    confidence,
    class_ids,
    detector_type="yolo",
    labels=None
):
    """Detect regions using a custom YOLO model or NudeNet."""

    if model is None:
        return []

    if detector_type == "nudenet":
        return detect_nudenet_regions(
            model,
            frame,
            confidence,
            labels or []
        )

    results = model.predict(
        frame,
        conf=confidence,
        verbose=False
    )

    boxes = []
    allowed_classes = set(class_ids)

    for result in results:
        if result.boxes is None:
            continue

        for detection in result.boxes:
            class_id = int(detection.cls[0])

            if (
                allowed_classes
                and class_id not in allowed_classes
            ):
                continue

            coordinates = detection.xyxy[0].tolist()

            boxes.append(
                tuple(map(int, coordinates))
            )

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
    """Process one video, then mux the original audio into an MP4."""
    ffmpeg, ffprobe = find_ffmpeg()
    source_width, source_height, fps, duration = get_video_info(video, ffprobe)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{video.stem}_censored.mp4"
    # MJPEG/AVI is a reliable OpenCV intermediate on Windows. MP4V output
    # from OpenCV can be empty/unreadable with some installed codecs.
    temporary = OUTPUT_DIR / f"{video.stem}_processed_temp.avi"

    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open selected video:\n{video}")

    # OpenCV may apply the Samsung Display Matrix rotation automatically.
    # Therefore determine dimensions from the actual decoded frame, not
    # from FFprobe's unrotated 1920x1080 stream dimensions.
    try:
        capture.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
    except Exception:
        pass

    ok, first_frame = capture.read()
    if not ok or first_frame is None:
        capture.release()
        raise RuntimeError("Could not decode the first frame of the selected video.")

    frame_height, frame_width = first_frame.shape[:2]
    writer = cv2.VideoWriter(
        str(temporary),
        cv2.VideoWriter_fourcc(*"MJPG"),
        fps,
        (frame_width, frame_height),
    )
    if not writer.isOpened():
        capture.release()
        raise RuntimeError(f"Could not create intermediate AVI:\n{temporary}")

    face_detector = None
    private_detector = None
    frame_count = 0
    face_boxes = []
    private_boxes = []
    detection_interval = max(1, int(config.get("detect_every_n_frames", 2)))

    print("\n================================")
    print("AUTOCENSORVIDEO")
    print("================================")
    print("Input:", video)
    print("Output:", output)
    print(f"Source stream: {source_width} x {source_height}")
    print(f"Decoded/writer frame: {frame_width} x {frame_height}")
    print("FPS:", round(fps, 2))
    print("Duration:", round(duration, 2))
    print("Intermediate:", temporary)
    print("--------------------------------")

    try:
        face_detector = create_face_detector(config)
        private_detector = create_private_detector(config)

        # Process the already-read first frame, then continue reading.
        frame = first_frame
        while frame is not None:
            if frame.shape[1] != frame_width or frame.shape[0] != frame_height:
                # Keep writer dimensions stable if a decoder reports a frame
                # with a different shape (unusual, but safer than silent drops).
                frame = cv2.resize(frame, (frame_width, frame_height))

            timestamp_ms = int(frame_count * 1000 / fps)
            if frame_count % detection_interval == 0:
                face_boxes = detect_faces(face_detector, frame, timestamp_ms)
                private_boxes = detect_private_regions(
                    private_detector,
                    frame,
                    float(config.get("private_confidence", config.get("confidence", 0.35))),
                    config.get("private_class_ids", []),
                    config.get("private_detector_type", "yolo"),
                    config.get("private_labels", [])
                )

            for box in face_boxes:
                apply_overlay(frame, box, config["overlay"]["face"])
            for box in private_boxes:
                apply_overlay(frame, box, config["overlay"]["private"])

            writer.write(frame)
            frame_count += 1

            if frame_count % max(1, int(fps * 10)) == 0:
                print(f"Processed {frame_count / fps:.0f} / {duration:.0f} seconds")

            ok, next_frame = capture.read()
            frame = next_frame if ok else None

    finally:
        capture.release()
        writer.release()
        if face_detector is not None:
            face_detector.close()

    if frame_count <= 0:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("No frames were processed; intermediate video was not created.")

    # Validate the intermediate before asking FFmpeg to encode it.
    probe_cmd = [
        ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,nb_frames",
        "-of", "json", str(temporary),
    ]
    probe = subprocess.run(probe_cmd, capture_output=True, text=True)
    if probe.returncode != 0:
        raise RuntimeError(
            "FFprobe could not read the processed AVI:\n" + probe.stderr.strip()
        )
    probe_data = json.loads(probe.stdout or "{}")
    streams = probe_data.get("streams", [])
    if not streams:
        raise RuntimeError(
            f"Processed AVI contains no video stream:\n{temporary}\n"
            f"Frames submitted to writer: {frame_count}"
        )
    print("Intermediate validation:", streams[0])
    print("Frames submitted:", frame_count)

    encoding = config.get("encoding", {})
    codec = encoding.get("codec", "libx264")
    audio_codec = encoding.get("audio", "copy")
    command = [
        ffmpeg, "-y",
        "-i", str(temporary),
        "-i", str(video),
        "-map", "0:v:0",
        "-map", "1:a?",
        "-c:v", codec,
        "-crf", str(encoding.get("crf", 20)),
        "-preset", str(encoding.get("preset", "medium")),
        "-c:a", str(audio_codec),
        "-shortest",
        str(output),
    ]

    print("\nEncoding final MP4 and copying original audio...")
    subprocess.run(command, check=True)
    temporary.unlink(missing_ok=True)

    print("\n================================")
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

    use_default = input("\nUse current censoring settings from config.json? (y/n): ").strip().lower()

    if use_default != 'y':
        config = configure_censoring(config)

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
