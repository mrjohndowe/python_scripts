"""Configuration management for AutoCensorVideo."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict

from autocensor.constants import (
    DEFAULT_AUDIO_CODEC,
    DEFAULT_BLUR_STRENGTH,
    DEFAULT_CODEC,
    DEFAULT_CONFIDENCE,
    DEFAULT_CRF,
    DEFAULT_DETECT_INTERVAL,
    DEFAULT_OPACITY,
    DEFAULT_PADDING,
    DEFAULT_PIXELATE_STRENGTH,
    DEFAULT_PRESET,
    DEFAULT_SCALE,
    DETECTOR_TYPE_NUDENET,
    DETECTOR_TYPE_YOLO,
    OVERLAY_TYPE_BLUR,
    OVERLAY_TYPE_BOX,
    OVERLAY_TYPE_EMOJI,
    OVERLAY_TYPE_IMAGE,
    OVERLAY_TYPE_PIXELATE,
    CONFIG_PATH,
    PROFILES_DIR,
    ROOT,
)


class OverlaySettings(TypedDict):
    """Type definition for overlay settings."""

    type: str
    emoji: str
    image: str
    strength: int
    padding: float
    opacity: float
    scale: float
    color: list[int]


class EncodingSettings(TypedDict):
    """Type definition for encoding settings."""

    codec: str
    crf: int
    preset: str
    audio: str


class Config(TypedDict):
    """Type definition for main configuration."""

    face_detection: bool
    private_detection: bool
    face_model: str
    private_model: str
    private_detector_type: str
    private_class_ids: list[int]
    private_labels: list[str]
    private_confidence: float
    confidence: float
    detect_every_n_frames: int
    overlay: dict[str, OverlaySettings]
    encoding: EncodingSettings


DEFAULT_CONFIG: Config = {
    "face_detection": True,
    "private_detection": True,
    "face_model": "models/face_detector.tflite",
    "private_model": "models/private_regions.pt",
    "private_detector_type": DETECTOR_TYPE_NUDENET,
    "private_class_ids": [],
    "private_labels": [
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
        "BUTTOCKS_EXPOSED",
        "ANUS_EXPOSED"
    ],
    "private_confidence": DEFAULT_CONFIDENCE,
    "confidence": DEFAULT_CONFIDENCE,
    "detect_every_n_frames": DEFAULT_DETECT_INTERVAL,
    "overlay": {
        "face": {
            "type": OVERLAY_TYPE_BLUR,
            "emoji": "😎",
            "image": "",
            "strength": DEFAULT_BLUR_STRENGTH,
            "padding": DEFAULT_PADDING,
            "opacity": DEFAULT_OPACITY,
            "scale": DEFAULT_SCALE,
            "color": [0, 0, 0]
        },
        "private": {
            "type": OVERLAY_TYPE_EMOJI,
            "emoji": "🍑",
            "image": "",
            "strength": DEFAULT_BLUR_STRENGTH,
            "padding": DEFAULT_PADDING,
            "opacity": DEFAULT_OPACITY,
            "scale": DEFAULT_SCALE,
            "color": [0, 0, 0]
        }
    },
    "encoding": {
        "codec": DEFAULT_CODEC,
        "crf": DEFAULT_CRF,
        "preset": DEFAULT_PRESET,
        "audio": DEFAULT_AUDIO_CODEC
    }
}


def validate_config(config: Config) -> list[str]:
    """Validate configuration and return list of errors.

    Args:
        config: Configuration dictionary to validate.

    Returns:
        List of error messages (empty if valid).
    """
    errors: list[str] = []

    # Validate detection settings
    if "confidence" in config:
        conf = config["confidence"]
        if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
            errors.append("confidence must be between 0 and 1")

    if "detect_every_n_frames" in config:
        interval = config["detect_every_n_frames"]
        if not isinstance(interval, int) or interval < 1:
            errors.append("detect_every_n_frames must be a positive integer")

    # Validate detector type
    if "private_detector_type" in config:
        detector_type = config["private_detector_type"].lower()
        if detector_type not in (DETECTOR_TYPE_YOLO, DETECTOR_TYPE_NUDENET):
            errors.append(f"private_detector_type must be '{DETECTOR_TYPE_YOLO}' or '{DETECTOR_TYPE_NUDENET}'")

    # Validate overlay settings
    if "overlay" in config:
        for region, settings in config["overlay"].items():
            if not isinstance(settings, dict):
                errors.append(f"overlay.{region} must be a dictionary")
                continue

            overlay_type = settings.get("type", "").lower()
            valid_types = (OVERLAY_TYPE_BLUR, OVERLAY_TYPE_PIXELATE, OVERLAY_TYPE_EMOJI,
                          OVERLAY_TYPE_BOX, OVERLAY_TYPE_IMAGE)
            if overlay_type not in valid_types:
                errors.append(f"overlay.{region}.type must be one of: {', '.join(valid_types)}")

            # Validate strength
            if "strength" in settings:
                strength = settings["strength"]
                if not isinstance(strength, int) or strength < 1:
                    errors.append(f"overlay.{region}.strength must be a positive integer")

            # Validate padding
            if "padding" in settings:
                padding = settings["padding"]
                if not isinstance(padding, (int, float)) or not (0 <= padding <= 1):
                    errors.append(f"overlay.{region}.padding must be between 0 and 1")

            # Validate opacity
            if "opacity" in settings:
                opacity = settings["opacity"]
                if not isinstance(opacity, (int, float)) or not (0 <= opacity <= 1):
                    errors.append(f"overlay.{region}.opacity must be between 0 and 1")

            # Validate scale
            if "scale" in settings:
                scale = settings["scale"]
                if not isinstance(scale, (int, float)) or scale <= 0:
                    errors.append(f"overlay.{region}.scale must be a positive number")

            # Validate color
            if "color" in settings:
                color = settings["color"]
                if not isinstance(color, list) or len(color) != 3:
                    errors.append(f"overlay.{region}.color must be a list of 3 integers")
                elif not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                    errors.append(f"overlay.{region}.color must be RGB values between 0 and 255")

    # Validate encoding settings
    if "encoding" in config:
        encoding = config["encoding"]
        if "crf" in encoding:
            crf = encoding["crf"]
            if not isinstance(crf, int) or not (0 <= crf <= 51):
                errors.append("encoding.crf must be between 0 and 51")

    return errors


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from file, creating with defaults if needed.

    Args:
        config_path: Path to config file. Uses default if None.

    Returns:
        Validated configuration dictionary.
    """
    path = config_path or CONFIG_PATH

    # Create config if it doesn't exist
    if not path.exists():
        path.write_text(
            json.dumps(DEFAULT_CONFIG, indent=4),
            encoding="utf-8"
        )

    with open(path, "r", encoding="utf-8") as f:
        config: Config = json.load(f)

    # Fill missing configuration values
    for key, value in DEFAULT_CONFIG.items():
        config.setdefault(key, value)

    config.setdefault("overlay", {})

    for key, value in DEFAULT_CONFIG["overlay"].items():
        config["overlay"].setdefault(key, value.copy())

    config.setdefault("encoding", DEFAULT_CONFIG["encoding"].copy())

    # Validate and report errors
    errors = validate_config(config)
    if errors:
        print("[WARNING] Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")

    return config


def save_config(config: Config, config_path: Path | None = None) -> None:
    """Save configuration to file.

    Args:
        config: Configuration dictionary to save.
        config_path: Path to save to. Uses default if None.
    """
    path = config_path or CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def load_profile(profile_name: str) -> Config | None:
    """Load a configuration profile.

    Args:
        profile_name: Name of the profile (without .json extension).

    Returns:
        Configuration dictionary or None if not found.
    """
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = PROFILES_DIR / f"{profile_name}.json"

    if not profile_path.exists():
        return None

    return load_config(profile_path)


def save_profile(config: Config, profile_name: str) -> None:
    """Save configuration as a profile.

    Args:
        config: Configuration dictionary to save.
        profile_name: Name of the profile (without .json extension).
    """
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = PROFILES_DIR / f"{profile_name}.json"
    save_config(config, profile_path)


def list_profiles() -> list[str]:
    """List available configuration profiles.

    Returns:
        List of profile names (without .json extension).
    """
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    profiles = []
    for path in PROFILES_DIR.glob("*.json"):
        profiles.append(path.stem)

    return sorted(profiles)
