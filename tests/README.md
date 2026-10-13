# Tests

This folder contains unit tests for the LEGO Train project.

## Running tests

```powershell
# Activate the virtual environment first
.venv\Scripts\activate

# Run all tests
pytest

# Run only traffic light detector tests
pytest tests/test_traffic_light.py -v
```

## Current status

### Traffic Light Detector Tests (`test_traffic_light.py`)

Tests the modular detector architecture under `src/detectors/`:

| Test | Description | Status |
|------|-------------|--------|
| `test_detect_phase[heuristics-...]` | Heuristic detector detects all phases correctly | ✅ Passing |
| `test_hue_warnings_empty` | Hue warning thresholds don't fire on normal images | ✅ Passing |
| `test_detect_phase[ml_yolo-...]` | ML detector tests (placeholder) | ⏭️ Skipped |

**Available detectors for testing:**
- `heuristics` — HSV color thresholding + blob detection (production-ready)
- `ml_yolo` — YOLO-based detector (placeholder — not yet implemented)

### Future Tests

- Bluetooth controller tests (mocking BLE responses)
- Motor power command validation
- Camera capture tests
