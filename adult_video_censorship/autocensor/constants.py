"""Constants for AutoCensorVideo."""

from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
OUTPUT_DIR = ROOT / "output"
MODEL_DIR = ROOT / "models"
OVERLAYS_DIR = ROOT / "overlays"
PROFILES_DIR = ROOT / "profiles"

# Video format support
SUPPORTED_VIDEO = (
    "*.mp4 *.mkv *.mov *.avi *.webm *.m4v *.wmv"
)

# Overlay type constants
OVERLAY_TYPE_BLUR = "blur"
OVERLAY_TYPE_PIXELATE = "pixelate"
OVERLAY_TYPE_EMOJI = "emoji"
OVERLAY_TYPE_BOX = "box"
OVERLAY_TYPE_IMAGE = "image"

# Detector type constants
DETECTOR_TYPE_YOLO = "yolo"
DETECTOR_TYPE_NUDENET = "nudenet"

# Detection and processing defaults
DEFAULT_CONFIDENCE = 0.35
DEFAULT_DETECT_INTERVAL = 2
DEFAULT_PADDING = 0.15
DEFAULT_SCALE = 1.0
DEFAULT_OPACITY = 1.0

# Overlay strength defaults
DEFAULT_BLUR_STRENGTH = 31
DEFAULT_PIXELATE_STRENGTH = 18
MIN_BLUR_STRENGTH = 3
MAX_BLUR_STRENGTH = 100
MIN_PIXELATE_STRENGTH = 2
MAX_PIXELATE_STRENGTH = 100

# Encoding defaults
DEFAULT_CODEC = "libx264"
DEFAULT_CRF = 20
DEFAULT_PRESET = "medium"
DEFAULT_AUDIO_CODEC = "copy"

# Video processing
MIN_PROGRESS_UPDATE_INTERVAL = 10  # seconds
DEFAULT_INTERMEDIATE_CODEC = "MJPG"
INTERMEDIATE_EXTENSION = ".avi"

# Retry logic
MAX_FFMPEG_RETRIES = 3
FFMPEG_RETRY_DELAY = 2  # seconds

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
