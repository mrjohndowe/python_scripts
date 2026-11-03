"""Main entry point for AutoCensorVideo."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from autocensor.config import Config, load_config, save_config
from autocensor.constants import CONFIG_PATH, ROOT
from autocensor.detectors import FaceDetector, PrivateDetector
from autocensor.ui import (
    ask_choice,
    ask_yes_no,
    configure_censoring,
    select_profile,
    select_video,
    select_videos,
)
from autocensor.video_processor import VideoProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main application entry point."""
    logger.info("AutoCensorVideo starting...")

    config = load_config()

    # Ask user for processing mode
    print("\n================================")
    print("AUTOCENSORVIDEO")
    print("================================")
    print("Select processing mode:")
    print("  1. Single video")
    print("  2. Batch processing (multiple videos)")
    print("  3. Preview mode (test detections)")
    print("  4. Configuration only")

    mode = ask_choice("Select mode", ["Single video", "Batch processing", "Preview mode", "Configuration only"], default=0)

    if mode == 3:
        # Preview mode
        run_preview_mode(config)
    elif mode == 2:
        # Batch processing
        run_batch_mode(config)
    elif mode == 1:
        # Single video
        run_single_video(config)
    else:
        # Configuration only
        run_configuration(config)


def run_single_video(config: Config) -> None:
    """Process a single video.

    Args:
        config: Configuration dictionary.
    """
    video = select_video()

    if video is None:
        logger.info("No video selected.")
        return

    if not video.exists():
        logger.error("Selected file does not exist.")
        return

    # Ask if user wants to use current config or modify it
    use_default = ask_yes_no("Use current censoring settings from config.json?", default=True)

    if not use_default:
        config = configure_censoring(config)
        save_config(config)

    # Ask for optional features
    export_detections = ask_yes_no("Export detection boxes to JSON?", default=False)

    process_video_internal(video, config, preview_mode=False, export_detections=export_detections)


def run_batch_mode(config: Config) -> None:
    """Process multiple videos in batch.

    Args:
        config: Configuration dictionary.
    """
    videos = select_videos()

    if not videos:
        logger.info("No videos selected.")
        return

    # Ask if user wants to use current config or modify it
    use_default = ask_yes_no("Use current censoring settings from config.json?", default=True)

    if not use_default:
        config = configure_censoring(config)
        save_config(config)

    # Ask for optional features
    export_detections = ask_yes_no("Export detection boxes to JSON?", default=False)

    logger.info(f"Processing {len(videos)} videos...")

    for i, video in enumerate(videos, 1):
        logger.info(f"\n[{i}/{len(videos)}] Processing: {video.name}")

        if not video.exists():
            logger.warning(f"File does not exist, skipping: {video}")
            continue

        try:
            process_video_internal(video, config, preview_mode=False, export_detections=export_detections)
        except Exception as e:
            logger.error(f"Failed to process {video.name}: {e}")

    logger.info("\nBatch processing complete.")


def run_preview_mode(config: Config) -> None:
    """Run preview mode to test detections without full encoding.

    Args:
        config: Configuration dictionary.
    """
    video = select_video()

    if video is None:
        logger.info("No video selected.")
        return

    if not video.exists():
        logger.error("Selected file does not exist.")
        return

    logger.info("Preview mode: Processing first 30 seconds with frame skip for faster preview")

    # Use frame skip for faster preview
    process_video_internal(video, config, preview_mode=True, export_detections=True, frame_skip=4)


def run_configuration(config: Config) -> None:
    """Run configuration-only mode.

    Args:
        config: Configuration dictionary.
    """
    print("\n================================")
    print("CONFIGURATION MODE")
    print("================================")

    print("Options:")
    print("  1. Modify overlay settings")
    print("  2. Load configuration profile")
    print("  3. Save current configuration as profile")
    print("  4. List available profiles")
    print("  5. Exit")

    choice = ask_choice("Select option", [
        "Modify overlay settings",
        "Load configuration profile",
        "Save current configuration as profile",
        "List available profiles",
        "Exit"
    ], default=0)

    if choice == 0:
        config = configure_censoring(config)
        save_config(config)
        logger.info("Configuration saved.")
    elif choice == 1:
        profile_name = select_profile()
        if profile_name:
            from autocensor.config import load_profile
            new_config = load_profile(profile_name)
            if new_config:
                config = new_config
                save_config(config)
                logger.info(f"Loaded profile: {profile_name}")
    elif choice == 2:
        profile_name = input("Enter profile name: ").strip()
        if profile_name:
            from autocensor.config import save_profile
            save_profile(config, profile_name)
            logger.info(f"Saved profile: {profile_name}")
    elif choice == 3:
        from autocensor.config import list_profiles
        profiles = list_profiles()
        if profiles:
            print("\nAvailable profiles:")
            for profile in profiles:
                print(f"  - {profile}")
        else:
            print("No profiles available.")
    else:
        logger.info("Exiting configuration mode.")


def process_video_internal(
    video: Path,
    config: Config,
    preview_mode: bool = False,
    export_detections: bool = False,
    frame_skip: int = 0
) -> None:
    """Internal video processing function.

    Args:
        video: Path to video file.
        config: Configuration dictionary.
        preview_mode: If True, skip final encoding.
        export_detections: If True, export detection boxes to JSON.
        frame_skip: Number of frames to skip (0 = process all).
    """
    try:
        # Initialize detectors
        face_detector = FaceDetector(config)
        private_detector = PrivateDetector(config)

        # Initialize video processor
        processor = VideoProcessor(config)

        # Process video
        output = processor.process_video(
            video,
            face_detector,
            private_detector,
            preview_mode=preview_mode,
            export_detections=export_detections,
            frame_skip=frame_skip
        )

        # Print statistics
        processor.print_stats()

        if not preview_mode:
            print(f"\nSaved: {output}")
        else:
            print(f"\nPreview saved: {output}")
            print("Note: This is an intermediate file. Process normally for final MP4.")

        # Cleanup detectors
        face_detector.close()

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nProcessing cancelled.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nERROR: {e}")
        sys.exit(1)
