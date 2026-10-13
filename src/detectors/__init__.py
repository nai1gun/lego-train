#!/usr/bin/env python3
"""
Modular traffic light detector package.

Public API:
    from detectors import (
        create_detector,
        get_available_detectors,
        DetectionResult,
        LampDetection,
        TrafficLightDetector,
    )

    # Create a detector by name:
    detector = create_detector("heuristics")

    # Run detection:
    result = detector.detect(frame)

    # Access results:
    print(f"Phase: {result.phase}")
    print(f"BBox: {result.bbox}")
    for lamp in result.lamp_detections:
        print(f"  {lamp.label}: {lamp.confidence:.3f}")

Available detectors:
    - "heuristics": Original heuristic-based detector (always available)
    - "ml_yolo": ML-based YOLO detector (requires model weights)
"""

from .base import (
    BaseTrafficLightDetector,
    DetectionResult,
    LampDetection,
    TrafficLightDetector,
)
from .heuristics import HeuristicsTrafficLightDetector
from .ml import MLTrafficLightDetector

__all__ = [
    "BaseTrafficLightDetector",
    "DetectionResult",
    "LampDetection",
    "TrafficLightDetector",
    "create_detector",
    "get_available_detectors",
    "HeuristicsTrafficLightDetector",
    "MLTrafficLightDetector",
]

# Registry of available detectors
_DETREG: dict = {}


def _register_detector(cls) -> None:
    """Register a detector class in the global registry."""
    _DETREG[cls.detector_type] = cls


# Auto-register built-in detectors
_register_detector(HeuristicsTrafficLightDetector)
_register_detector(MLTrafficLightDetector)


def create_detector(detector_type: str = "heuristics") -> TrafficLightDetector:
    """Create a traffic light detector by name.

    This is the main factory function for instantiating detectors.
    It looks up the detector type in the global registry.

    Args:
        detector_type: One of the available detector types.
                       Defaults to "heuristics" (the original detector).

    Returns:
        An instantiated TrafficLightDetector.

    Raises:
        ValueError: If the detector_type is not registered.
        RuntimeError: If the detector fails to initialize (e.g., missing model).

    Examples:
        >>> detector = create_detector("heuristics")
        >>> result = detector.detect(frame)
        >>> print(result.phase)
        'red'

        >>> detector = create_detector("ml_yolo")  # requires model weights
    """
    if detector_type not in _DETREG:
        available = ", ".join(sorted(_DETREG.keys()))
        raise ValueError(
            f"Unknown detector type '{detector_type}'. "
            f"Available types: {available}"
        )

    cls = _DETREG[detector_type]
    try:
        return cls()
    except RuntimeError as e:
        raise RuntimeError(
            f"Failed to initialize detector '{detector_type}': {e}\n"
            f"Make sure all dependencies are installed."
        ) from e


def get_available_detectors() -> list[str]:
    """Return a list of available detector type names."""
    return sorted(_DETREG.keys())
