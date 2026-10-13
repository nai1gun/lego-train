#!/usr/bin/env python3
"""
Base protocol and dataclasses for the modular traffic light detector system.

This module defines the `TrafficLightDetector` protocol that all detector
implementations must follow, as well as the `DetectionResult` dataclass
that serves as the standard output format.

Usage (implementing a new detector):

    from .base import TrafficLightDetector, DetectionResult
    import numpy as np

    class MyDetector(TrafficLightDetector):
        detector_type = "my_detector"

        def detect(self, frame: np.ndarray) -> DetectionResult:
            # ... your inference logic ...
            return DetectionResult(
                phase="red",
                bbox=(x, y, w, h),
                lamp_states={"red": True, "yellow": False, "green": False},
                lamp_detections=[...],
                metadata={"model": "my-model-v1"},
            )
"""

from __future__ import annotations

import abc
import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass(frozen=True)
class LampDetection:
    """A single lamp detection result (YOLO-style)."""

    label: str
    bbox: Tuple[float, float, float, float]
    confidence: float
    class_probs: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class DetectionResult:
    """Standard output of any traffic light detector."""

    phase: str
    bbox: Optional[Tuple[float, float, float, float]] = None
    lamp_states: Dict[str, bool] = field(default_factory=dict)
    lamp_detections: List[LampDetection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    _raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict compatible with the legacy detector output."""
        d = {"phase": self.phase, "bbox": self.bbox}
        for lamp in ("red", "yellow", "green"):
            lit = self.lamp_states.get(lamp, False)
            d[f"{lamp}_lit"] = lit
            d[f"{lamp}_lit_pixels"] = 0
            d[f"{lamp}_hsv"] = (0, 0, 0)
        d.update(self._raw)
        return d

# ============================================================================
# PROTOCOL
# ============================================================================


class TrafficLightDetector(Protocol):
    """Protocol that all traffic light detectors must implement."""

    detector_type: str

    def detect(self, frame: "np.ndarray") -> DetectionResult:
        """Run detection on a single BGR frame.

        Args:
            frame: BGR image as a numpy array (H, W, 3).

        Returns:
            DetectionResult with phase, bbox, lamp states, and metadata.
        """
        ...


# ============================================================================
# ABSTRACT BASE CLASS
# ============================================================================


class BaseTrafficLightDetector(abc.ABC):
    """Abstract base class for traffic light detectors."""

    detector_type: str = "base"

    @abc.abstractmethod
    def detect(self, frame: "np.ndarray") -> DetectionResult:
        """Run detection on a single BGR frame."""
        ...

    @staticmethod
    def _compute_lamp_positions(
        bbox: Tuple[int, int, int, int],
        lamp_y_fractions: Dict[str, float],
        radius_fraction: float,
    ) -> List[Tuple[str, int, int, int]]:
        """Compute lamp disc positions from a housing bounding box."""
        x, y, w, h = bbox
        radius = int(radius_fraction * h)
        positions = []
        for label, y_frac in lamp_y_fractions.items():
            cx = int(x + w / 2)
            cy = int(y + h * y_frac)
            positions.append((label, cx, cy, radius))
        return positions

    bbox: Optional[Tuple[float, float, float, float]] = None
    lamp_states: Dict[str, bool] = field(default_factory=dict)
    lamp_detections: List[LampDetection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    _raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict compatible with the legacy detector output."""
        d = {"phase": self.phase, "bbox": self.bbox}
        for lamp in ("red", "yellow", "green"):
            lit = self.lamp_states.get(lamp, False)
            d[f"{lamp}_lit"] = lit
            d[f"{lamp}_lit_pixels"] = 0
            d[f"{lamp}_hsv"] = (0, 0, 0)
        d.update(self._raw)
        return d
