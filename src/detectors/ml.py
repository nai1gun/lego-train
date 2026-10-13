#!/usr/bin/env python3
"""
ML-based traffic light detector placeholder (YOLO-style).

This is a skeleton detector showing the expected interface for future
ML-based implementations. It returns placeholder results to demonstrate
the detector protocol contract.

Expected architecture: YOLO-style object detector that returns:
  - Bounding boxes for the traffic-light housing
  - Per-lamp detections with class probabilities (red, yellow, green)

Usage (once implemented):
    from detectors import create_detector

    detector = create_detector("ml_yolo")
    result = detector.detect(frame)

    # Access structured detections:
    for lamp_det in result.lamp_detections:
        print(f"{lamp_det.label}: conf={lamp_det.confidence:.3f}")

    # Access final phase:
    print(f"Phase: {result.phase}")

TODO:
    1. Load YOLO model (e.g., YOLOv8n on custom-trained traffic-light dataset)
    2. Implement `detect()` to run inference on BGR frames
    3. Parse model outputs into LampDetection objects
    4. Compute final phase from lamp class probabilities
    5. Add model loading/caching for efficiency
    6. Add calibration/quantization support for Pi deployment
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import numpy as np

from .base import BaseTrafficLightDetector, DetectionResult, LampDetection


class MLTrafficLightDetector(BaseTrafficLightDetector):
    """Placeholder ML detector (YOLO-style).

    This detector currently returns placeholder results to demonstrate
    the protocol interface. Replace the placeholder logic with actual
    model inference when ready.
    """

    detector_type: str = "ml_yolo"

    def __init__(self, model_path: str = "") -> None:
        """Initialize the ML detector.

        Args:
            model_path: Path to the YOLO model file (.pt, .onnx, etc.).
                        If empty, the detector returns placeholder results.
        """
        self._model_path = model_path
        self._model = None  # Will hold the loaded model
        self._frame_count: int = 0
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Load the ML model from disk.

        TODO: Implement actual model loading.
        Example with ultralytics:
            from ultralytics import YOLO
            self._model = YOLO(self._model_path)
        """
        if self._model_path:
            # TODO: Load model when ML pipeline is ready
            # self._model = YOLO(self._model_path)
            pass
        else:
            pass  # Placeholder mode — will return dummy results

    def detect(self, frame: np.ndarray) -> DetectionResult:
        """Run ML-based detection on a single BGR frame.

        This is the main inference method. It should:
        1. Preprocess the frame (resize, normalize, etc.)
        2. Run model inference
        3. Parse outputs into LampDetection objects
        4. Compute final phase from lamp detections

        Args:
            frame: BGR image as a numpy array (H, W, 3).

        Returns:
            DetectionResult with phase, bbox, lamp states, and metadata.
        """
        start_time = time.time()
        self._frame_count += 1

        # TODO: Replace this placeholder with actual inference logic.
        # The placeholder returns a "no_detection" result to demonstrate
        # the protocol contract. When implemented, it should:
        #
        #   1. Run YOLO inference on the frame
        #   2. Filter detections by confidence threshold
        #   3. Group detections into housing + lamp detections
        #   4. Compute phase from lamp class probabilities
        #   5. Return DetectionResult with all fields populated

        placeholder_result = DetectionResult(
            phase="no_detection",
            bbox=None,
            lamp_states={"red": False, "yellow": False, "green": False},
            lamp_detections=[],
            metadata={
                "detector_type": self.detector_type,
                "elapsed_ms": (time.time() - start_time) * 1000,
                "frame_count": self._frame_count,
                "model_path": self._model_path or "not_loaded",
                "status": "placeholder — not yet implemented",
            },
        )

        return placeholder_result
