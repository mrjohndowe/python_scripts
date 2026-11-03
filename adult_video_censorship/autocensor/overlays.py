"""Overlay rendering functions for censorship effects."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from autocensor.config import OverlaySettings
from autocensor.constants import (
    DEFAULT_BLUR_STRENGTH,
    DEFAULT_OPACITY,
    DEFAULT_PADDING,
    DEFAULT_SCALE,
    OVERLAYS_DIR,
    ROOT,
)

logger = logging.getLogger(__name__)


def render_emoji(emoji: str, width: int, height: int) -> Image.Image:
    """Render emoji to transparent RGBA image.

    Args:
        emoji: Emoji character to render.
        width: Width of the output image.
        height: Height of the output image.

    Returns:
        RGBA PIL Image with the emoji.
    """
    image = Image.new("RGBA", (max(1, width), max(1, height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Try multiple emoji fonts for cross-platform support
    emoji_fonts = [
        "seguiemj.ttf",  # Windows
        "AppleColorEmoji.ttf",  # macOS
        "NotoColorEmoji.ttf",  # Linux
        "Symbola.ttf",  # Fallback
    ]

    font = None
    for font_name in emoji_fonts:
        try:
            font = ImageFont.truetype(font_name, max(16, int(height * 0.9)))
            break
        except Exception:
            continue

    if font is None:
        font = ImageFont.load_default()

    draw.text((0, 0), emoji, font=font, embedded_color=True)

    return image


def apply_overlay(frame: np.ndarray, box: tuple[int, int, int, int], settings: OverlaySettings) -> None:
    """Apply configured overlay to a bounding box (modifies frame in-place).

    Args:
        frame: BGR image frame (modified in-place).
        box: Bounding box as (x1, y1, x2, y2).
        settings: Overlay settings dictionary.
    """
    frame_height, frame_width = frame.shape[:2]

    x1, y1, x2, y2 = map(int, box)

    # Clamp to frame boundaries
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(frame_width, x2)
    y2 = min(frame_height, y2)

    if x2 <= x1 or y2 <= y1:
        return

    # Apply padding
    padding = float(settings.get("padding", DEFAULT_PADDING))
    pad_x = int((x2 - x1) * padding)
    pad_y = int((y2 - y1) * padding)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(frame_width, x2 + pad_x)
    y2 = min(frame_height, y2 + pad_y)

    # Scale overlay
    scale = max(0.1, float(settings.get("scale", DEFAULT_SCALE)))

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    box_width = max(2, int((x2 - x1) * scale))
    box_height = max(2, int((y2 - y1) * scale))

    x1 = max(0, center_x - box_width // 2)
    y1 = max(0, center_y - box_height // 2)

    x2 = min(frame_width, x1 + box_width)
    y2 = min(frame_height, y1 + box_height)

    roi = frame[y1:y2, x1:x2].copy()

    if roi.size == 0:
        return

    overlay_type = settings.get("type", "blur").lower()
    strength = max(3, int(settings.get("strength", DEFAULT_BLUR_STRENGTH)))
    opacity = max(0.0, min(1.0, float(settings.get("opacity", DEFAULT_OPACITY))))

    # Apply effect based on type
    if overlay_type == "blur":
        effect = _apply_blur(roi, strength)
    elif overlay_type == "pixelate":
        effect = _apply_pixelate(roi, strength)
    elif overlay_type == "box":
        effect = _apply_box(roi, settings.get("color", [0, 0, 0]))
    elif overlay_type in ("emoji", "image"):
        effect = _apply_image_overlay(roi, settings, overlay_type)
    else:
        logger.warning(f"Unknown overlay type: {overlay_type}, using blur")
        effect = _apply_blur(roi, DEFAULT_BLUR_STRENGTH)

    # Apply opacity if needed
    if opacity < 1.0:
        frame[y1:y2, x1:x2] = cv2.addWeighted(roi, 1.0 - opacity, effect, opacity, 0)
    else:
        frame[y1:y2, x1:x2] = effect


def _apply_blur(roi: np.ndarray, strength: int) -> np.ndarray:
    """Apply Gaussian blur to region of interest.

    Args:
        roi: Region of interest.
        strength: Blur kernel size (must be odd).

    Returns:
        Blurred region.
    """
    if strength % 2 == 0:
        strength += 1

    return cv2.GaussianBlur(roi, (strength, strength), 0)


def _apply_pixelate(roi: np.ndarray, strength: int) -> np.ndarray:
    """Apply pixelation effect to region of interest.

    Args:
        roi: Region of interest.
        strength: Block size for pixelation.

    Returns:
        Pixelated region.
    """
    block = max(2, strength)

    small = cv2.resize(
        roi,
        (max(1, roi.shape[1] // block), max(1, roi.shape[0] // block)),
        interpolation=cv2.INTER_LINEAR
    )

    return cv2.resize(
        small,
        (roi.shape[1], roi.shape[0]),
        interpolation=cv2.INTER_NEAREST
    )


def _apply_box(roi: np.ndarray, color: list[int]) -> np.ndarray:
    """Apply solid color box to region of interest.

    Args:
        roi: Region of interest.
        color: RGB color values.

    Returns:
        Solid color region.
    """
    effect = roi.copy()
    effect[:] = color
    return effect


def _apply_image_overlay(roi: np.ndarray, settings: OverlaySettings, overlay_type: str) -> np.ndarray:
    """Apply emoji or custom image overlay to region of interest.

    Args:
        roi: Region of interest.
        settings: Overlay settings.
        overlay_type: Either "emoji" or "image".

    Returns:
        Region with overlay applied.
    """
    image_path = settings.get("image", "")

    if overlay_type == "image" and image_path:
        # Handle relative and absolute paths
        path = Path(image_path)
        if not path.is_absolute():
            # Try relative to overlays directory first, then project root
            if (OVERLAYS_DIR / path).exists():
                path = OVERLAYS_DIR / path
            elif (ROOT / path).exists():
                path = ROOT / path

        if path.exists():
            icon = Image.open(path).convert("RGBA")
        else:
            logger.warning(f"Image not found: {path}, using emoji instead")
            icon = render_emoji(settings.get("emoji", "🟣"), roi.shape[1], roi.shape[0])
    else:
        icon = render_emoji(settings.get("emoji", "🟣"), roi.shape[1], roi.shape[0])

    icon = icon.resize((roi.shape[1], roi.shape[0]), Image.Resampling.LANCZOS)

    background = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)).convert("RGBA")
    background.alpha_composite(icon)

    return cv2.cvtColor(np.array(background.convert("RGB")), cv2.COLOR_RGB2BGR)
