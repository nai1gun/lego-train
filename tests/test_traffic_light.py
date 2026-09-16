"""
Regression tests for the traffic-light detector.

Each test loads one of the sample images from ``media/`` and asserts
that ``detect_phase_from_image()`` returns the correct phase string.

Run with::

    pytest tests/test_traffic_light.py -v

Or run all images at once for a summary table::

    pytest tests/test_traffic_light.py -v --tb=short

Or run the full regression harness from the command line::

    python scripts/detect_traffic_light.py --images media/traffic_light_*.jpg
"""

import pathlib
import sys

# Make the project root importable so we can import from scripts/
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from scripts.detect_traffic_light import detect_phase_from_image

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MEDIA_DIR = _PROJECT_ROOT / "media"

# Expected phases for each sample image (ground truth).
# These are the CORRECT phases — the detector should report these.
_EXPECTED_PHASES = {
    "traffic_light_green": "green",
    "traffic_light_off": "off",
    "traffic_light_red": "red",
    "traffic_light_red_yellow": "red_yellow",
    "traffic_light_yellow": "yellow",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _image_path(name: str) -> pathlib.Path:
    """Return the absolute path to a media file by stem name."""
    return MEDIA_DIR / f"{name}.jpg"


# ---------------------------------------------------------------------------
# Per-image phase tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stem,expected_phase", sorted(_EXPECTED_PHASES.items()))
def test_detect_phase(stem: str, expected_phase: str) -> None:
    """Run the detector on one sample image and assert the correct phase."""
    image_path = _image_path(stem)

    # Skip if the file is missing (CI may not have the media dir)
    if not image_path.exists():
        pytest.skip(f"Media file not found: {image_path}")

    result = detect_phase_from_image(str(image_path))
    assert result["phase"] == expected_phase, (
        f"Expected phase '{expected_phase}' for {stem}, got '{result['phase']}'\n"
        f"  bbox={result['bbox']}\n"
        f"  red={result['red_lit']}({result['red_lit_pixels']}px)  "
        f"yellow={result['yellow_lit']}({result['yellow_lit_pixels']}px)  "
        f"green={result['green_lit']}({result['green_lit_pixels']}px)"
    )
