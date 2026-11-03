"""Video processing and FFmpeg operations."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from tqdm import tqdm

from autocensor.config import Config
from autocensor.constants import (
    DEFAULT_AUDIO_CODEC,
    DEFAULT_CODEC,
    DEFAULT_CRF,
    DEFAULT_PRESET,
    DEFAULT_INTERMEDIATE_CODEC,
    INTERMEDIATE_EXTENSION,
    MAX_FFMPEG_RETRIES,
    MIN_PROGRESS_UPDATE_INTERVAL,
    OUTPUT_DIR,
    ROOT,
)

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handle video processing with FFmpeg and OpenCV."""

    def __init__(self, config: Config):
        """Initialize video processor.

        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.ffmpeg, self.ffprobe = self._find_ffmpeg()
        self.stats = {
            "total_frames": 0,
            "faces_detected": 0,
            "private_regions_detected": 0,
            "processing_time": 0.0
        }

    def _find_ffmpeg(self) -> tuple[str, str]:
        """Find FFmpeg and FFprobe executables.

        Returns:
            Tuple of (ffmpeg_path, ffprobe_path).

        Raises:
            RuntimeError: If FFmpeg or FFprobe not found.
        """
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")

        if not ffmpeg:
            raise RuntimeError(
                "FFmpeg was not found in PATH.\n"
                "Install FFmpeg and restart PowerShell."
            )

        if not ffprobe:
            raise RuntimeError("FFprobe was not found in PATH.")

        return ffmpeg, ffprobe

    def get_video_info(self, video: Path) -> tuple[int, int, float, float]:
        """Get video width, height, FPS, and duration.

        Args:
            video: Path to video file.

        Returns:
            Tuple of (width, height, fps, duration).
        """
        command = [
            self.ffprobe,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-show_entries", "format=duration",
            "-of", "json",
            str(video)
        ]

        result = subprocess.check_output(command, text=True)
        data = json.loads(result)

        stream = data["streams"][0]
        width = int(stream["width"])
        height = int(stream["height"])

        rate = stream.get("r_frame_rate", "30/1")
        numerator, denominator = rate.split("/")
        fps = float(numerator) / float(denominator)

        duration = float(data.get("format", {}).get("duration", 0))

        return width, height, fps, duration

    def process_video(
        self,
        video: Path,
        face_detector: Any,
        private_detector: Any,
        preview_mode: bool = False,
        export_detections: bool = False,
        frame_skip: int = 0,
        progress_callback: callable | None = None
    ) -> Path:
        """Process a video with censorship overlays.

        Args:
            video: Path to input video.
            face_detector: Face detector instance.
            private_detector: Private region detector instance.
            preview_mode: If True, skip encoding and return intermediate.
            export_detections: If True, export detection boxes to JSON.
            frame_skip: Number of frames to skip (0 = process all).
            progress_callback: Optional callback function(current, total, faces, private).

        Returns:
            Path to output video.

        Raises:
            RuntimeError: If processing fails.
        """
        start_time = time.time()

        source_width, source_height, fps, duration = self.get_video_info(video)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output = OUTPUT_DIR / f"{video.stem}_censored.mp4"
        temporary = OUTPUT_DIR / f"{video.stem}_processed_temp{INTERMEDIATE_EXTENSION}"

        capture = cv2.VideoCapture(str(video))
        if not capture.isOpened():
            raise RuntimeError(f"Could not open selected video: {video}")

        # Handle rotation
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
            cv2.VideoWriter_fourcc(*DEFAULT_INTERMEDIATE_CODEC),
            fps,
            (frame_width, frame_height),
        )

        if not writer.isOpened():
            capture.release()
            raise RuntimeError(f"Could not create intermediate video: {temporary}")

        detection_interval = max(1, int(self.config.get("detect_every_n_frames", 2)))
        frame_count = 0
        face_boxes = []
        private_boxes = []
        all_detections = [] if export_detections else None

        logger.info(f"Processing video: {video}")
        logger.info(f"Output: {output}")
        logger.info(f"Source stream: {source_width} x {source_height}")
        logger.info(f"Decoded frame: {frame_width} x {frame_height}")
        logger.info(f"FPS: {fps:.2f}, Duration: {duration:.2f}s")

        # Progress bar (only show if no callback provided)
        total_frames = int(duration * fps)
        pbar = tqdm(total=total_frames, desc="Processing frames", unit="frames", disable=progress_callback is not None)

        try:
            frame = first_frame
            while frame is not None:
                # Handle frame skip
                if frame_skip > 0 and frame_count % (frame_skip + 1) != 0:
                    writer.write(frame)
                    frame_count += 1
                    pbar.update(1)
                    ok, next_frame = capture.read()
                    frame = next_frame if ok else None
                    continue

                # Resize if needed
                if frame.shape[1] != frame_width or frame.shape[0] != frame_height:
                    frame = cv2.resize(frame, (frame_width, frame_height))

                timestamp_ms = int(frame_count * 1000 / fps)

                # Run detection at intervals
                if frame_count % detection_interval == 0:
                    face_boxes = face_detector.detect(frame, timestamp_ms)
                    private_boxes = private_detector.detect(
                        frame,
                        float(self.config.get("private_confidence", self.config.get("confidence", 0.35))),
                        self.config.get("private_class_ids", []),
                        self.config.get("private_labels", [])
                    )

                    # Update stats
                    self.stats["faces_detected"] += len(face_boxes)
                    self.stats["private_regions_detected"] += len(private_boxes)

                    # Export detections if requested
                    if export_detections and all_detections is not None:
                        all_detections.append({
                            "frame": frame_count,
                            "timestamp_ms": timestamp_ms,
                            "faces": face_boxes,
                            "private_regions": private_boxes
                        })

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(frame_count, total_frames, len(face_boxes), len(private_boxes))

                # Apply overlays
                from autocensor.overlays import apply_overlay

                for box in face_boxes:
                    apply_overlay(frame, box, self.config["overlay"]["face"])
                for box in private_boxes:
                    apply_overlay(frame, box, self.config["overlay"]["private"])

                writer.write(frame)
                frame_count += 1
                pbar.update(1)

                ok, next_frame = capture.read()
                frame = next_frame if ok else None

        finally:
            capture.release()
            writer.release()
            pbar.close()

        self.stats["total_frames"] = frame_count
        self.stats["processing_time"] = time.time() - start_time

        if frame_count <= 0:
            temporary.unlink(missing_ok=True)
            raise RuntimeError("No frames were processed; intermediate video was not created.")

        # Validate intermediate
        self._validate_intermediate(temporary, frame_count)

        # Export detections if requested
        if export_detections and all_detections:
            detections_path = OUTPUT_DIR / f"{video.stem}_detections.json"
            with open(detections_path, "w", encoding="utf-8") as f:
                json.dump(all_detections, f, indent=2)
            logger.info(f"Detections exported to: {detections_path}")

        # Return early in preview mode
        if preview_mode:
            logger.info("Preview mode: skipping final encoding")
            return temporary

        # Encode final video with retry logic
        self._encode_final_video(video, temporary, output, source_width, source_height)

        # Cleanup
        temporary.unlink(missing_ok=True)

        logger.info(f"Processing complete: {output}")
        return output

    def _validate_intermediate(self, temporary: Path, frame_count: int) -> None:
        """Validate intermediate video file.

        Args:
            temporary: Path to intermediate video.
            frame_count: Number of frames written.

        Raises:
            RuntimeError: If validation fails.
        """
        probe_cmd = [
            self.ffprobe, "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height,nb_frames",
            "-of", "json", str(temporary),
        ]

        probe = subprocess.run(probe_cmd, capture_output=True, text=True)

        if probe.returncode != 0:
            raise RuntimeError(f"FFprobe could not read the processed video: {probe.stderr.strip()}")

        probe_data = json.loads(probe.stdout or "{}")
        streams = probe_data.get("streams", [])

        if not streams:
            raise RuntimeError(
                f"Processed video contains no video stream: {temporary}\n"
                f"Frames submitted to writer: {frame_count}"
            )

        logger.info(f"Intermediate validation: {streams[0]}")
        logger.info(f"Frames submitted: {frame_count}")

    def _encode_final_video(
        self,
        video: Path,
        temporary: Path,
        output: Path,
        source_width: int,
        source_height: int
    ) -> None:
        """Encode final MP4 with audio, with retry logic.

        Args:
            video: Original video path.
            temporary: Intermediate video path.
            output: Output video path.
            source_width: Original video width.
            source_height: Original video height.

        Raises:
            RuntimeError: If encoding fails after retries.
        """
        encoding = self.config.get("encoding", {})
        codec = encoding.get("codec", DEFAULT_CODEC)
        audio_codec = encoding.get("audio", DEFAULT_AUDIO_CODEC)

        command = [
            self.ffmpeg, "-y",
            "-i", str(temporary),
            "-i", str(video),
            "-map", "0:v:0",
            "-map", "1:a?",
            "-c:v", codec,
            "-crf", str(encoding.get("crf", DEFAULT_CRF)),
            "-preset", str(encoding.get("preset", DEFAULT_PRESET)),
            "-c:a", str(audio_codec),
            "-shortest",
            str(output),
        ]

        logger.info("Encoding final MP4 and copying original audio...")

        for attempt in range(MAX_FFMPEG_RETRIES):
            try:
                subprocess.run(command, check=True)
                logger.info("Encoding successful")
                return
            except subprocess.CalledProcessError as e:
                if attempt < MAX_FFMPEG_RETRIES - 1:
                    logger.warning(f"Encoding attempt {attempt + 1} failed, retrying in {MAX_FFMPEG_RETRIES} seconds...")
                    time.sleep(MAX_FFMPEG_RETRIES)
                else:
                    raise RuntimeError(f"FFmpeg encoding failed after {MAX_FFMPEG_RETRIES} attempts: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get processing statistics.

        Returns:
            Dictionary with processing statistics.
        """
        return self.stats.copy()

    def print_stats(self) -> None:
        """Print processing statistics to console."""
        print("\n================================")
        print("PROCESSING STATISTICS")
        print("================================")
        print(f"Total frames processed: {self.stats['total_frames']}")
        print(f"Faces detected: {self.stats['faces_detected']}")
        print(f"Private regions detected: {self.stats['private_regions_detected']}")
        print(f"Processing time: {self.stats['processing_time']:.2f}s")
        if self.stats['total_frames'] > 0:
            fps = self.stats['total_frames'] / self.stats['processing_time']
            print(f"Average processing speed: {fps:.2f} FPS")
        print("================================")
