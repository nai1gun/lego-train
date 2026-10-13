# Detectors Package

Modular, swappable traffic light detector implementations.

## Architecture

```
src/detectors/
├── __init__.py        # Factory + public API
├── base.py            # TrafficLightDetector protocol, DetectionResult
├── heuristics.py      # Heuristic detector (HSV + blob detection)
└── ml.py              # ML detector (YOLO placeholder)
```

## Protocol

All detectors implement the `TrafficLightDetector` protocol:

```python
class TrafficLightDetector(Protocol):
    detector_type: str
    def detect(self, frame: np.ndarray) -> DetectionResult: ...
```

The `detector_type` string is used to identify the detector in CLI args and benchmark reports.

## Factory

Use `create_detector()` to instantiate detectors by name:

```python
from src.detectors import create_detector

detector = create_detector("heuristics")  # Returns HeuristicsTrafficLightDetector
result = detector.detect(frame)           # Returns DetectionResult
```

New detectors are auto-registered by convention — just create a class with `detector_type` attribute.

## DetectionResult

```python
@dataclass
class DetectionResult:
    red_lit: bool
    yellow_lit: bool
    green_lit: bool
    red_hsv: tuple | None    # (h, s, v) or None
    yellow_hsv: tuple | None
    green_hsv: tuple | None
    red_bbox: tuple | None   # (x, y, w, h) or None
    yellow_bbox: tuple | None
    green_bbox: tuple | None

    def to_dict(self) -> dict:
        # Legacy dict format for backward compatibility
```

## Adding a New Detector

1. Create `src/detectors/my_detector.py`:

```python
import numpy as np
from .base import TrafficLightDetector, DetectionResult

class MyDetector(TrafficLightDetector):
    detector_type: str = "my_detector"

    def detect(self, frame: np.ndarray) -> DetectionResult:
        # Your detection logic here
        return DetectionResult(
            red_lit=False,
            yellow_lit=False,
            green_lit=True,
            red_hsv=None,
            yellow_hsv=None,
            green_hsv=(60, 200, 200),
            red_bbox=None,
            yellow_bbox=None,
            green_bbox=(100, 200, 50, 50),
        )
```

2. The factory auto-registers by convention — no extra code needed.

3. Use it: `python src/detect_traffic_light.py --detector-type my_detector`

## Benchmarking Detectors

Compare detectors against labeled data:

```bash
# Benchmark heuristic detector
python scripts/benchmark_traffic_light.py --detector-type heuristics

# Benchmark any detector (once implemented)
python scripts/benchmark_traffic_light.py --detector-type my_detector

# Compare two detectors on the same run
python scripts/benchmark_traffic_light.py --detector-type heuristics --run 20260917_065933
python scripts/benchmark_traffic_light.py --detector-type my_detector --run 20260917_065933
```

Reports include `detector_type` in metadata for fair comparison.
