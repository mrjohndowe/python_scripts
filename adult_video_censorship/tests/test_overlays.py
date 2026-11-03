"""Unit tests for overlay rendering."""

import numpy as np
import pytest

from autocensor.config import OverlaySettings
from autocensor.overlays import apply_overlay, render_emoji


def test_render_emoji():
    """Test emoji rendering."""
    image = render_emoji("😎", 100, 100)
    assert image is not None
    assert image.width == 100
    assert image.height == 100
    assert image.mode == "RGBA"


def test_apply_overlay_blur():
    """Test blur overlay application."""
    frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
    box = (10, 10, 50, 50)
    settings: OverlaySettings = {
        "type": "blur",
        "emoji": "😎",
        "image": "",
        "strength": 31,
        "padding": 0.15,
        "opacity": 1.0,
        "scale": 1.0,
        "color": [0, 0, 0]
    }

    original_roi = frame[10:50, 10:50].copy()
    apply_overlay(frame, box, settings)
    modified_roi = frame[10:50, 10:50]

    # After blur, pixels should be different
    assert not np.array_equal(original_roi, modified_roi)


def test_apply_overlay_pixelate():
    """Test pixelate overlay application."""
    frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
    box = (10, 10, 50, 50)
    settings: OverlaySettings = {
        "type": "pixelate",
        "emoji": "😎",
        "image": "",
        "strength": 10,
        "padding": 0.0,
        "opacity": 1.0,
        "scale": 1.0,
        "color": [0, 0, 0]
    }

    apply_overlay(frame, box, settings)
    # Just verify it doesn't crash
    assert frame.shape == (100, 100, 3)


def test_apply_overlay_box():
    """Test solid box overlay application."""
    frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
    box = (10, 10, 50, 50)
    settings: OverlaySettings = {
        "type": "box",
        "emoji": "😎",
        "image": "",
        "strength": 31,
        "padding": 0.0,
        "opacity": 1.0,
        "scale": 1.0,
        "color": [0, 0, 0]
    }

    apply_overlay(frame, box, settings)
    # Check that the box area is black
    roi = frame[10:50, 10:50]
    assert np.all(roi == 0)


def test_apply_overlay_with_opacity():
    """Test overlay with partial opacity."""
    frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
    box = (10, 10, 50, 50)
    settings: OverlaySettings = {
        "type": "box",
        "emoji": "😎",
        "image": "",
        "strength": 31,
        "padding": 0.0,
        "opacity": 0.5,
        "scale": 1.0,
        "color": [0, 0, 0]
    }

    apply_overlay(frame, box, settings)
    # With 50% opacity, the box should be gray (not pure black or white)
    roi = frame[10:50, 10:50]
    assert np.all(roi > 0)  # Not pure black
    assert np.all(roi < 255)  # Not pure white


def test_apply_overlay_clamping():
    """Test that overlay is clamped to frame boundaries."""
    frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
    box = (-10, -10, 150, 150)  # Box extends beyond frame
    settings: OverlaySettings = {
        "type": "box",
        "emoji": "😎",
        "image": "",
        "strength": 31,
        "padding": 0.0,
        "opacity": 1.0,
        "scale": 1.0,
        "color": [0, 0, 0]
    }

    # Should not crash
    apply_overlay(frame, box, settings)
    assert frame.shape == (100, 100, 3)
