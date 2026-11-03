"""Detection modules for faces and private regions."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from autocensor.config import Config
from autocensor.constants import (
    DEFAULT_CONFIDENCE,
    DETECTOR_TYPE_NUDENET,
    DETECTOR_TYPE_YOLO,
    MODEL_DIR,
    ROOT,
)

logger = logging.getLogger(__name__)


class FaceDetector:
    """MediaPipe face detector."""

    def __init__(self, config: Config):
        """Initialize face detector.

        Args:
            config: Configuration dictionary.
        """
        self.detector = None
        self.enabled = config.get("face_detection", True)

        if not self.enabled:
            logger.info("Face detection disabled")
            return

        try:
            import mediapipe as mp

            model_path = ROOT / config.get("face_model", "models/face_detector.tflite")

            if not model_path.exists():
                raise RuntimeError(
                    f"Face detection model missing: {model_path}\n"
                    "Download the model using the README instructions."
                )

            options = mp.tasks.vision.FaceDetectorOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                min_detection_confidence=float(config.get("confidence", DEFAULT_CONFIDENCE))
            )

            self.detector = mp.tasks.vision.FaceDetector.create_from_options(options)
            logger.info("Face detector initialized successfully")

        except Exception as e:
            logger.error(f"Face detector initialization failed: {e}")
            self.enabled = False

    def detect(self, frame: np.ndarray, timestamp_ms: int) -> list[tuple[int, int, int, int]]:
        """Detect faces in a frame.

        Args:
            frame: BGR image frame.
            timestamp_ms: Frame timestamp in milliseconds.

        Returns:
            List of bounding boxes as (x1, y1, x2, y2) tuples.
        """
        if not self.enabled or self.detector is None:
            return []

        try:
            import mediapipe as mp

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = self.detector.detect_for_video(image, timestamp_ms)

            boxes = []
            for detection in result.detections:
                box = detection.bounding_box
                x1 = int(box.origin_x)
                y1 = int(box.origin_y)
                x2 = int(x1 + box.width)
                y2 = int(y1 + box.height)
                boxes.append((x1, y1, x2, y2))

            return boxes

        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []

    def close(self) -> None:
        """Release detector resources."""
        if self.detector is not None:
            self.detector.close()
            self.detector = None


class NudeNetDetector:
    """NudeNet nudity detector."""

    def __init__(self, config: Config):
        """Initialize NudeNet detector.

        Args:
            config: Configuration dictionary.
        """
        self.detector = None
        self.enabled = config.get("private_detection", True)

        if not self.enabled:
            logger.info("Private region detection disabled")
            return

        try:
            from nudenet import NudeDetector

            logger.info("Loading NudeNet detector...")

            model_path = config.get("private_model", None)

            if model_path and Path(model_path).exists():
                self.detector = NudeDetector(model_path=str(model_path))
            else:
                self.detector = NudeDetector()

            logger.info("NudeNet detector initialized successfully")

        except Exception as e:
            logger.warning(f"NudeNet initialization failed: {e}")
            self.enabled = False

    def detect(
        self,
        frame: np.ndarray,
        confidence: float,
        labels: list[str] | None = None
    ) -> list[tuple[int, int, int, int]]:
        """Detect private regions in a frame.

        Args:
            frame: BGR image frame.
            confidence: Detection confidence threshold.
            labels: List of allowed labels (None = all labels).

        Returns:
            List of bounding boxes as (x1, y1, x2, y2) tuples.
        """
        if not self.enabled or self.detector is None:
            return []

        try:
            detections = self.detector.detect(frame)
        except Exception as e:
            logger.warning(f"NudeNet detection failed: {e}")
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
                x2 = int(x + width)
                y2 = int(y + height)
                boxes.append((int(x), int(y), x2, y2))

        return boxes


class YOLODetector:
    """YOLO-based private region detector."""

    def __init__(self, config: Config):
        """Initialize YOLO detector.

        Args:
            config: Configuration dictionary.
        """
        self.model = None
        self.enabled = config.get("private_detection", True)

        if not self.enabled:
            logger.info("Private region detection disabled")
            return

        model_path = ROOT / config.get("private_model", "models/private_regions.pt")

        if not model_path.exists():
            logger.warning(f"Private-region model not found: {model_path}")
            logger.warning("Private-region detection is disabled until a compatible custom YOLO model is supplied.")
            self.enabled = False
            return

        try:
            from ultralytics import YOLO

            logger.info("Loading private-region detector...")
            self.model = YOLO(str(model_path))
            logger.info("YOLO detector initialized successfully")

        except Exception as e:
            logger.warning(f"YOLO initialization failed: {e}")
            self.enabled = False

    def detect(
        self,
        frame: np.ndarray,
        confidence: float,
        class_ids: list[int] | None = None
    ) -> list[tuple[int, int, int, int]]:
        """Detect private regions in a frame.

        Args:
            frame: BGR image frame.
            confidence: Detection confidence threshold.
            class_ids: List of allowed class IDs (None = all classes).

        Returns:
            List of bounding boxes as (x1, y1, x2, y2) tuples.
        """
        if not self.enabled or self.model is None:
            return []

        results = self.model.predict(frame, conf=confidence, verbose=False)

        boxes = []
        allowed_classes = set(class_ids) if class_ids else None

        for result in results:
            if result.boxes is None:
                continue

            for detection in result.boxes:
                class_id = int(detection.cls[0])

                if allowed_classes and class_id not in allowed_classes:
                    continue

                coordinates = detection.xyxy[0].tolist()
                boxes.append(tuple(map(int, coordinates)))

        return boxes


class PrivateDetector:
    """Unified private region detector supporting NudeNet and YOLO."""

    def __init__(self, config: Config):
        """Initialize private detector.

        Args:
            config: Configuration dictionary.
        """
        self.detector_type = config.get("private_detector_type", DETECTOR_TYPE_NUDENET).lower()
        self.nudenet = None
        self.yolo = None

        if self.detector_type == DETECTOR_TYPE_NUDENET:
            self.nudenet = NudeNetDetector(config)
        else:
            self.yolo = YOLODetector(config)

    def detect(
        self,
        frame: np.ndarray,
        confidence: float,
        class_ids: list[int] | None = None,
        labels: list[str] | None = None
    ) -> list[tuple[int, int, int, int]]:
        """Detect private regions in a frame.

        Args:
            frame: BGR image frame.
            confidence: Detection confidence threshold.
            class_ids: List of allowed class IDs for YOLO.
            labels: List of allowed labels for NudeNet.

        Returns:
            List of bounding boxes as (x1, y1, x2, y2) tuples.
        """
        if self.detector_type == DETECTOR_TYPE_NUDENET:
            return self.nudenet.detect(frame, confidence, labels)
        else:
            return self.yolo.detect(frame, confidence, class_ids)

    @property
    def enabled(self) -> bool:
        """Check if detector is enabled."""
        if self.detector_type == DETECTOR_TYPE_NUDENET:
            return self.nudenet.enabled if self.nudenet else False
        else:
            return self.yolo.enabled if self.yolo else False
