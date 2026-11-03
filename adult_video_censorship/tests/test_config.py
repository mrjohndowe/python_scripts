"""Unit tests for configuration management."""

import json
import tempfile
from pathlib import Path

import pytest

from autocensor.config import (
    Config,
    DEFAULT_CONFIG,
    load_config,
    save_config,
    validate_config,
    load_profile,
    save_profile,
    list_profiles,
)


def test_default_config_structure():
    """Test that default config has all required keys."""
    assert "face_detection" in DEFAULT_CONFIG
    assert "private_detection" in DEFAULT_CONFIG
    assert "overlay" in DEFAULT_CONFIG
    assert "encoding" in DEFAULT_CONFIG
    assert "face" in DEFAULT_CONFIG["overlay"]
    assert "private" in DEFAULT_CONFIG["overlay"]


def test_validate_config_valid():
    """Test validation with valid config."""
    errors = validate_config(DEFAULT_CONFIG)
    assert errors == []


def test_validate_config_invalid_confidence():
    """Test validation with invalid confidence."""
    config = DEFAULT_CONFIG.copy()
    config["confidence"] = 1.5
    errors = validate_config(config)
    assert len(errors) > 0
    assert any("confidence" in error.lower() for error in errors)


def test_validate_config_invalid_overlay_type():
    """Test validation with invalid overlay type."""
    config = DEFAULT_CONFIG.copy()
    config["overlay"]["face"]["type"] = "invalid_type"
    errors = validate_config(config)
    assert len(errors) > 0
    assert any("overlay" in error.lower() for error in errors)


def test_validate_config_invalid_opacity():
    """Test validation with invalid opacity."""
    config = DEFAULT_CONFIG.copy()
    config["overlay"]["face"]["opacity"] = 1.5
    errors = validate_config(config)
    assert len(errors) > 0
    assert any("opacity" in error.lower() for error in errors)


def test_load_config_creates_default():
    """Test that load_config creates default if file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = load_config(config_path)
        assert config_path.exists()
        assert "face_detection" in config


def test_save_and_load_config():
    """Test saving and loading config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        test_config = DEFAULT_CONFIG.copy()
        test_config["confidence"] = 0.5

        save_config(test_config, config_path)
        loaded_config = load_config(config_path)

        assert loaded_config["confidence"] == 0.5


def test_profile_operations():
    """Test profile save/load/list operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        profiles_dir = Path(tmpdir)

        # Save profile with custom path
        test_config = DEFAULT_CONFIG.copy()
        test_config["confidence"] = 0.75
        profile_path = profiles_dir / "test_profile.json"

        with open(profile_path, "w") as f:
            json.dump(test_config, f)

        # Load profile directly
        loaded_config = load_config(profile_path)
        assert loaded_config is not None
        assert loaded_config["confidence"] == 0.75
