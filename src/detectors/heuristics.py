#!/usr/bin/env python3
"""
Heuristics-based traffic light detector.

This is the original heuristic detector, extracted verbatim from
`detect_traffic_light.py`. No logic changes — exact same constants,
thresholds, and behavior.

It wraps the legacy functions (`find_traffic_light_housing`,
`_detect_lamps_lit`, `_compute_phase_from_lamps`) in the
`TrafficLightDetector` protocol.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

# Lazy imports — avoid circular dependency with detect_traffic_light
# The actual imports happen inside detect() where needed.

from .base import BaseTrafficLightDetector, DetectionResult, LampDetection


class HeuristicsTrafficLightDetector(BaseTrafficLightDetector):
    """The original heuristic detector wrapped in the detector protocol.

    This detector:
    1. Finds the traffic-light housing via red-stripe color segmentation
    2. Computes lamp disc positions from the housing bbox
    3. Detects lamp states via HSV pixel-fraction counting
    4. Computes phase from lamp states (position-based)

    All logic is identical to the original `detect_traffic_light.py`.
    """

    detector_type: str = "heuristics"

    def __init__(self) -> None:
        self._frame_count: int = 0
        self._last_phase: str = "none"
        self._last_change_time: float = 0.0

    def detect(self, frame: np.ndarray) -> DetectionResult:
        """Run the heuristic detector on a single BGR frame.

        Args:
            frame: BGR image as a numpy array (H, W, 3).

        Returns:
            DetectionResult with phase, bbox, lamp states, and metadata.
        """
        # Lazy import to avoid circular dependency
        from detect_traffic_light import (
            find_traffic_light_housing,
            _detect_lamps_lit,
            _compute_phase_from_lamps,
            LAMP_Y_FRACTIONS,
            LAMP_RADIUS_FRACTION,
        )

        start_time = time.time()

        # Step 1: Find housing
        bbox = find_traffic_light_housing(frame)

        if bbox is None:
            elapsed = time.time() - start_time
            return DetectionResult(
                phase="no_detection",
                bbox=None,
                lamp_states={"red": False, "yellow": False, "green": False},
                metadata={"detector_type": self.detector_type, "elapsed_ms": elapsed * 1000},
            )

        # Step 2: Compute lamp positions
        lamp_positions = self._compute_lamp_positions(
            bbox,
            LAMP_Y_FRACTIONS,
            LAMP_RADIUS_FRACTION,
        )

        # Step 3: Detect lamp states
        lamp_states, lamp_brightnesses, lamp_hues, hue_warnings, lit_fractions = (
            _detect_lamps_lit(frame, bbox, lamp_positions)
        )

        # Step 4: Compute phase
        phase = _compute_phase_from_lamps(lamp_states)

        elapsed = time.time() - start_time

        # Build LampDetection objects for YOLO-style compat
        lamp_detections: List[LampDetection] = []
        for label, cx, cy, radius in lamp_positions:
            lit = lamp_states.get(label, False)
            conf = float(lit)  # Heuristic detector doesn't have probabilities
            lamp_detections.append(
                LampDetection(
                    label=label,
                    bbox=(float(cx - radius), float(cy - radius), 2 * radius, 2 * radius),
                    confidence=conf,
                    class_probs={label: conf},
                )
            )

        # Build _raw dict for backward compat
        raw: Dict[str, Any] = {
            "_lamp_positions": lamp_positions,
            "_lamp_hues": lamp_hues,
            "_lamp_lit_fractions": lit_fractions,
            "_hue_warnings": hue_warnings,
        }

        return DetectionResult(
            phase=phase,
            bbox=(float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])),
            lamp_states=lamp_states,
            lamp_detections=lamp_detections,
            metadata={
                "detector_type": self.detector_type,
                "elapsed_ms": elapsed * 1000,
                "frame_count": self._frame_count,
            },
            _raw=raw,
        )
