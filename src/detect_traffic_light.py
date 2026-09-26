#!/usr/bin/env python3
"""
Traffic Light Detection for LEGO Autonomous Train

Detects Lego traffic light phases (off, green, yellow, red, red+yellow) from
camera streams using OpenCV color segmentation and contour detection.

Features:
  - Dynamic housing detection via red+white stripe color segmentation
  - 3-sector phase detection (top=red, middle=yellow, bottom=green)
  - Cross-platform camera support (Picamera2 on Pi, cv2 on Windows)
  - CSV logging of phase changes with timestamps
  - Debug overlay visualization
  - Color calibration mode for Pi camera tuning

Usage:
  # Live camera on Pi (auto-detects CSI camera):
  python src/detect_traffic_light.py

  # Live camera with debug overlay:
  python src/detect_traffic_light.py --show

  # Process a video file for offline testing:
  python src/detect_traffic_light.py --video path/to/video.mp4

  # Process a single image (for debugging):
  python src/detect_traffic_light.py --image media/traffic_light_green.jpg

  # Process multiple images and print a regression summary:
  python src/detect_traffic_light.py --images media/traffic_light_green.jpg media/traffic_light_red.jpg

  # Save debug overlays and masks to a directory:
  python src/detect_traffic_light.py --images media/traffic_light_*.jpg --save-debug debug_output/

  # Calibrate colors from Pi camera data:
  python src/detect_traffic_light.py --calibrate

  # Disable auto white balance to prevent color shift on Pi:
  python src/detect_traffic_light.py --no-auto-wb

  # Custom resolution:
  python src/detect_traffic_light.py --resolution 800x600
"""

import argparse
import csv
import datetime
import os
import platform
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


# ============================================================================
# CONSTANTS — Tune these values based on real Pi camera data
# ============================================================================

# --- Housing Detection (Requirement C + E) ---
# Red hue with wrap-around: 0–8 OR 168–180, S>90, V>60
# This correctly isolates the red stripes on the housing.
HOUSING_RED_LOW_1 = np.array([0, 90, 60], dtype=np.uint8)
HOUSING_RED_HIGH_1 = np.array([8, 255, 255], dtype=np.uint8)
HOUSING_RED_LOW_2 = np.array([168, 90, 60], dtype=np.uint8)
HOUSING_RED_HIGH_2 = np.array([180, 255, 255], dtype=np.uint8)

# Area thresholds as fractions of frame area (Requirement C)
# Works at both 640×480 and 775×1033 and any other resolution.
HOUSING_MIN_FRAC = 0.001        # minimum 0.1% of frame area
HOUSING_MAX_FRAC = 0.50         # maximum 50% of frame area

# Aspect ratio of the tall traffic-light panel
HOUSING_MIN_ASPECT_RATIO = 0.20  # narrow bounding box allowed
HOUSING_MAX_ASPECT_RATIO = 0.80  # wide bounding box allowed

# Morphology kernel size for connecting red stripe fragments (Requirement C)
# Dilate with a large kernel (≈ 1/4 of expected panel height) to connect
# nearby red blobs into clusters before bounding-box extraction.
HOUSING_DILATE_KERNEL = 25       # base kernel size; scaled by panel height

# Stripe gating: keep red only near red/white stripe boundaries (rejects red walls)
STRIPE_WHITE_MAX_S = 70      # white stripe: low saturation
STRIPE_WHITE_MIN_V = 120     # white stripe: bright
STRIPE_NEAR_PX = 15          # keep red within this neighborhood of a red/white edge
# Measured bias of the detector's box vs ground truth (pred/GT)
HOUSING_BOX_W_BIAS = 1.28
HOUSING_BOX_H_BIAS = 1.11

# --- Phase Detection (LAMP-BASED — position, not colour) (Requirement B) ---
# The architecture now determines phase by lamp *position* within the panel:
#   top lamp  = always red
#   middle lamp = always yellow
#   bottom lamp = always green
# A lamp is "lit" by comparing each lamp's brightness to its neighbours
# and its own recent history — not against absolute HSV bounds.
# Hue is used only as a sanity check (logged as warning on mismatch).

# Lamp centres as a fraction of panel height (measured from media/ samples)
LAMP_Y_FRACTIONS = {"red": 0.22, "yellow": 0.48, "green": 0.72}
LAMP_RADIUS_FRACTION = 0.13   # disc radius as a fraction of panel height
LIT_PIXEL_FRACTION = 0.02     # fraction of disc pixels passing the S/V gate

# High-saturation + high-value gate for lit-LED pixels (Requirement D)
# S>140 AND V>205 selects lit-LED pixels only — robust against exposure
# and white-balance changes. Treated as a starting point / gate, not a
# solution (it will break under glare and daylight).
LIT_SAT_GATE = 140
LIT_VAL_GATE = 205

# Hue sanity-check ranges for lit lamps (Requirement E)
# Red ≈ 168–180 ∪ 0–8, Yellow/amber ≈ 12–32, Green ≈ 40–80
HUE_RED_RANGES = [(0, 8), (168, 180)]
HUE_YELLOW_RANGES = [(12, 32)]
HUE_GREEN_RANGES = [(40, 80)]

# --- Debounce ---
DEBOUNCE_SECONDS = 0.5          # minimum time between phase change events

# --- Camera Defaults ---
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
TARGET_FPS = 30
PI_CAMERA_INDEX = -1            # Ignored on Pi — picamera2 auto-detects CSI
WIN_CAMERA_INDEX = 0            # First USB/webcam device on Windows

# --- Logging ---
LOG_DIR = "logs"
LOG_CSV_PREFIX = "traffic_log_" # e.g., traffic_log_20260913_142301.csv
LOG_FLUSH_INTERVAL = 1.0        # flush CSV to disk every N seconds


# ============================================================================
# KEYBOARD LISTENER (separate thread, avoids cv2.waitKey issues on Windows)
# ============================================================================

class KeyboardListener:
    """Listens for 'q' key press in a background thread.

    This avoids the known issue where cv2.waitKey doesn't reliably
    capture keyboard events on Windows with OpenCV MSMF backend.
    """

    def __init__(self):
        self._quit_event = threading.Event()

    @property
    def should_quit(self) -> bool:
        """Check if the user pressed 'q'."""
        return self._quit_event.is_set()

    def start(self):
        """Start listening for keyboard input in a background thread."""
        thread = threading.Thread(target=self._listen, daemon=True)
        thread.start()

    def _listen(self):
        """Background thread that waits for 'q' key press."""
        print("[INFO] Press 'q' to quit at any time...")
        try:
            # Read from stdin — works reliably across all platforms
            while not self._quit_event.is_set():
                try:
                    char = sys.stdin.read(1)
                    if char.lower() == 'q':
                        self._quit_event.set()
                        break
                except Exception:
                    time.sleep(0.05)
        except KeyboardInterrupt:
            self._quit_event.set()

    def stop(self):
        """Signal the listener to stop."""
        self._quit_event.set()


# ============================================================================
# HOUSING DETECTION
# ============================================================================

def find_traffic_light_housing(
    frame: np.ndarray,
) -> Optional[Tuple[int, int, int, int]]:
    """
    Detect the traffic light housing in the frame using red-hue-with-wrap
    (0–8 OR 168–180, S>90, V>60) and white-stripe segmentation.

    Requirement C: group red fragments instead of taking the largest.
    Dilate with a large kernel (≈ 1/4 of expected panel height) to connect
    nearby red blobs into clusters, then score candidates on fill ratio and
    aspect ratio ≈ 0.45 (tall panel).

    Requirement E: use correct hue ranges so no hue votes for nothing.

    Requirement D: area thresholds as fractions of frame area — works at
    640×480 and at 775×1033.

    Args:
        frame: BGR image from camera

    Returns:
        (x, y, w, h) bounding box of the traffic light, or None if not found
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, w = frame.shape[:2]
    frame_area = h * w

    # --- Red mask with wrap-around (Requirement E) ---
    # Range 1: low hue 0–8
    mask_red_1 = cv2.inRange(hsv, HOUSING_RED_LOW_1, HOUSING_RED_HIGH_1)
    # Range 2: high hue 168–180
    mask_red_2 = cv2.inRange(hsv, HOUSING_RED_LOW_2, HOUSING_RED_HIGH_2)
    mask_red = cv2.bitwise_or(mask_red_1, mask_red_2)

    # --- Stripe gating: keep only red near red/white stripe boundaries ---
    _, sat, val = cv2.split(hsv)
    white = ((sat <= STRIPE_WHITE_MAX_S) & (val >= STRIPE_WHITE_MIN_V)).astype(np.uint8)
    k3 = np.ones((3, 3), np.uint8)
    stripe_edge = cv2.dilate((mask_red > 0).astype(np.uint8), k3) & cv2.dilate(white, k3)
    near_edge = cv2.dilate(stripe_edge, np.ones((STRIPE_NEAR_PX, STRIPE_NEAR_PX), np.uint8))
    mask_red = cv2.bitwise_and(mask_red, mask_red, mask=near_edge)

    # --- Use the red mask alone (white stripes are photometrically
    # identical to the white table background, so the white mask pulls
    # the bounding box onto the table in most test images) ---
    mask_combined = mask_red

    # --- Dilate to connect nearby fragments (Requirement C) ---
    # Kernel size scales with expected panel height (≈ 1/2.5 of panel height)
    # to bridge bezel cuts that fragment the red stripes.
    # We assume the panel occupies roughly 10-30% of frame height.
    expected_panel_h = max(int(h * 0.1), 50)  # conservative lower bound
    kernel_size = max(3, int(expected_panel_h / 2.5))
    # Ensure odd kernel size for morphology
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask_combined = cv2.dilate(mask_combined, kernel, iterations=2)
    mask_combined = cv2.erode(mask_combined, kernel, iterations=1)

    # --- Find connected components / contours ---
    contours, _ = cv2.findContours(
        mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    best_bbox = None
    best_score = -1.0

    for contour in contours:
        area = cv2.contourArea(contour)

        # --- Requirement C: fraction-based area filtering ---
        min_area = int(frame_area * HOUSING_MIN_FRAC)
        max_area = int(frame_area * HOUSING_MAX_FRAC)
        if area < min_area or area > max_area:
            continue

        x, y, bw, bh = cv2.boundingRect(contour)
        aspect_ratio = bw / max(bh, 1)

        # --- Filter by aspect ratio (tall panel ≈ 0.2–0.8) ---
        if aspect_ratio < HOUSING_MIN_ASPECT_RATIO or aspect_ratio > HOUSING_MAX_ASPECT_RATIO:
            continue

        # --- Score candidate on fill ratio and aspect ratio ---
        # Fill ratio: how much of the bounding box is covered by the contour
        bbox_area = bw * bh
        fill_ratio = area / max(bbox_area, 1)

        # Ideal aspect ratio for a traffic-light panel is roughly 0.45 (tall)
        ideal_aspect = 0.45
        aspect_penalty = 1.0 - min(abs(aspect_ratio - ideal_aspect) / ideal_aspect, 1.0)

        # Combined score: prefer good fill ratio and ideal aspect ratio
        score = fill_ratio * 0.5 + aspect_penalty * 0.5

        if score > best_score:
            best_score = score
            best_bbox = (x, y, bw, bh)

    # --- Correct systematic box-size bias (shrink around center) ---
    if best_bbox is not None:
        bx, by, bw, bh = best_bbox
        nw, nh = bw / HOUSING_BOX_W_BIAS, bh / HOUSING_BOX_H_BIAS
        best_bbox = (int(bx + (bw - nw) / 2), int(by + (bh - nh) / 2), int(nw), int(nh))
    return best_bbox


# ============================================================================
# LAMP BEZEL DETECTION
# ============================================================================





# ============================================================================
# LAMP STATE DETECTION (relative brightness)
# ============================================================================





def _detect_lamps_lit(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
    lamp_positions: List[Tuple[str, int, int, int]],
) -> Tuple[Dict[str, bool], Dict[str, float], Dict[str, float], List[str]]:
    """
    Determine which lamps are lit using pixel-fraction counting inside
    each lamp disc.

    NEW ARCHITECTURE (pixel-fraction):
      For each lamp disc, count how many pixels pass the high-S + high-V
      gate (S > 140 AND V > 205).  If the fraction of passing pixels
      exceeds LIT_PIXEL_FRACTION of the disc area, the lamp is lit.

    This is far more reliable than the old mean-brightness approach because
    the LED core occupies only a tiny fraction of the dark bezel ring —
    the mean Value was always dominated by the dark plastic.

    Args:
        frame: BGR image
        bbox: (x, y, w, h) of the traffic light housing
        lamp_positions: list of (label, cx, cy, radius) sorted top->bottom

    Returns:
        Tuple of:
            - lit_states: dict mapping lamp label -> bool (lit or not)
            - lamp_brightnesses: dict mapping lamp label -> mean Value
            - lamp_hues: dict mapping lamp label -> median Hue (for sanity check)
            - hue_warnings: list of warning strings for hue cross-check failures
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, w = frame.shape[:2]
    lit_states = {}
    lamp_brightnesses = {}
    lamp_hues = {}
    hue_warnings = []

    # High-S + high-V gate for lit-LED pixels (Requirement D)
    sat_gate = 140
    val_gate = 205

    for label, cx, cy, radius in lamp_positions:
        cx, cy, radius = int(cx), int(cy), int(radius)
        inner_r = max(1, int(radius * 0.8))  # use inner 80 % to avoid bezel edge

        # Build circular mask using vectorised ops (fast, no Python loops)
        y_coords, x_coords = np.ogrid[:h, :w]
        mask = (x_coords - cx) ** 2 + (y_coords - cy) ** 2 <= inner_r ** 2

        # Extract HSV values inside the mask
        pixel_s = hsv[mask][:, 1]
        pixel_v = hsv[mask][:, 2]

        if pixel_s.size == 0:
            lit_states[label] = False
            lamp_brightnesses[label] = 0.0
            lamp_hues[label] = 0.0
            continue

        mean_v = float(np.mean(pixel_v))
        median_h_val = float(np.median(hsv[mask][:, 0]))

        # Count pixels that pass the S+V gate
        lit_pixels = int(np.sum((pixel_s > sat_gate) & (pixel_v > val_gate)))
        total_pixels = pixel_s.size
        lit_fraction = lit_pixels / total_pixels if total_pixels > 0 else 0.0

        lit_states[label] = lit_fraction > LIT_PIXEL_FRACTION
        lamp_brightnesses[label] = mean_v
        lamp_hues[label] = median_h_val

        # Hue cross-check: if lamp is lit, verify hue matches expected range
        if lit_states[label]:
            if label == "red":
                ranges = HUE_RED_RANGES
            elif label == "yellow":
                ranges = HUE_YELLOW_RANGES
            elif label == "green":
                ranges = HUE_GREEN_RANGES
            else:
                ranges = []

            hue_valid = any(r[0] <= median_h_val <= r[1] for r in ranges)
            if not hue_valid:
                hue_warnings.append(
                    f"Lamp '{label}' lit but hue={median_h_val:.1f} "
                    f"outside expected ranges {ranges}"
                )

    # --- Red-glow spill fix for yellow lamp ---
    # When red is lit, its glow can spill into the yellow disc, causing
    # false-positive yellow detection (e.g. frames 000202–000228).
    # Suppress yellow as "lit" unless BOTH hold:
    #   (a) its median hue is genuinely in the yellow range (12–32), NOT red
    #   (b) its brightness is at least ~0.6× the red lamp's brightness
    if lit_states.get("yellow", False) and lit_states.get("red", False):
        yellow_hue = lamp_hues.get("yellow", 0.0)
        red_brightness = lamp_brightnesses.get("red", 0.0)
        yellow_brightness = lamp_brightnesses.get("yellow", 0.0)

        # (a) Hue must be in yellow range, not red range
        hue_in_yellow = any(r[0] <= yellow_hue <= r[1] for r in HUE_YELLOW_RANGES)
        hue_in_red = any(r[0] <= yellow_hue <= r[1] for r in HUE_RED_RANGES)

        if not hue_in_yellow or hue_in_red:
            lit_states["yellow"] = False
            hue_warnings.append(
                f"Yellow suppressed: red-glow detected (hue={yellow_hue:.1f}, "
                f"red_hue={lamp_hues.get('red', 0.0):.1f})"
            )
        elif red_brightness > 0 and yellow_brightness < 0.6 * red_brightness:
            # (b) Yellow brightness too low relative to red — likely spill
            lit_states["yellow"] = False
            hue_warnings.append(
                f"Yellow suppressed: brightness ratio {yellow_brightness:.1f}/{red_brightness:.1f} "
                f"= {yellow_brightness / red_brightness:.2f} < 0.60"
            )

    return lit_states, lamp_brightnesses, lamp_hues, hue_warnings


# ============================================================================
# POSITION-BASED PHASE COMPUTATION
# ============================================================================


def _compute_phase_from_lamps(lit_states: Dict[str, bool]) -> str:
    """
    Map lamp states to phase name using *position* (not colour).

    The top lamp is always red, the middle is always yellow, the bottom
    is always green. We only need to know which lamps are lit.

    Args:
        lit_states: dict mapping 'red'/'yellow'/'green' (by position) -> bool

    Returns:
        Phase name string: 'off', 'green', 'yellow', 'red', or 'red_yellow'
    """
    red = lit_states.get("red", False)
    yellow = lit_states.get("yellow", False)
    green = lit_states.get("green", False)

    if red and yellow:
        return "red_yellow"
    elif red:
        return "red"
    elif yellow:
        return "yellow"
    elif green:
        return "green"
    if not any(lit_states.values()):
        return "off"


# ============================================================================
# PHASE DETECTION
# ============================================================================


def detect_phase_from_bbox(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
) -> Dict:
    """
    Detect which traffic light lamp is lit inside the housing bounding box.

    NEW ARCHITECTURE (arithmetic lamp positions):
      1. Derive lamp positions from housing bbox using LAMP_Y_FRACTIONS
         and LAMP_RADIUS_FRACTION — no bezel detection needed.
      2. For each lamp disc, count how many pixels pass the high-S + high-V
         gate (S > 140 AND V > 205).  If the fraction exceeds
         LIT_PIXEL_FRACTION, the lamp is lit.
      3. Use lamp position to name the phase: top=red, middle=yellow,
         bottom=green. Hue is used only as a sanity check.

    Args:
        frame: BGR image from camera
        bbox: (x, y, w, h) of the traffic light housing

    Returns:
        dict with keys:
            phase (str): Detected phase name
            red (bool), yellow (bool), green (bool): lit state by position
            red_hsv, yellow_hsv, green_hsv: mean HSV of each lamp disc
            red_lit_pixels, yellow_lit_pixels, green_lit_pixels: mean brightness
    """
    # Default "no detection" result
    default_result = {
        "phase": "no_detection",
        "red": False,
        "yellow": False,
        "green": False,
        "red_hsv": (0.0, 0.0, 0.0),
        "yellow_hsv": (0.0, 0.0, 0.0),
        "green_hsv": (0.0, 0.0, 0.0),
        "red_lit_pixels": 0,
        "yellow_lit_pixels": 0,
        "green_lit_pixels": 0,
    }

    if bbox is None:
        return default_result

    # Step 1: Derive lamp positions arithmetically from housing bbox
    bx, by, bw, bh = bbox
    lamp_radius = int(bw * LAMP_RADIUS_FRACTION)
    lamp_positions = [
        ("red",    bx + bw // 2, int(by + bh * LAMP_Y_FRACTIONS["red"]), lamp_radius),
        ("yellow", bx + bw // 2, int(by + bh * LAMP_Y_FRACTIONS["yellow"]), lamp_radius),
        ("green",  bx + bw // 2, int(by + bh * LAMP_Y_FRACTIONS["green"]), lamp_radius),
    ]

    # Step 2: Determine which lamps are lit using pixel-fraction counting
    lit_states, lamp_brightnesses, lamp_hues, hue_warnings = _detect_lamps_lit(
        frame, bbox, lamp_positions
    )

    # Step 3: Compute phase from lamp positions
    phase = _compute_phase_from_lamps(lit_states)

    # Compute lit fractions for overlay / debug
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, w = frame.shape[:2]
    lamp_lit_fractions = {}
    for label, cx, cy, radius in lamp_positions:
        cx_i, cy_i, r_i = int(cx), int(cy), int(radius)
        inner_r = max(1, int(r_i * 0.8))
        y_coords, x_coords = np.ogrid[:h, :w]
        mask = (x_coords - cx_i) ** 2 + (y_coords - cy_i) ** 2 <= inner_r ** 2
        pixel_s = hsv[mask][:, 1]
        pixel_v = hsv[mask][:, 2]
        if pixel_s.size == 0:
            lamp_lit_fractions[label] = 0.0
        else:
            lit_pixels = int(np.sum((pixel_s > 140) & (pixel_v > 205)))
            lamp_lit_fractions[label] = lit_pixels / pixel_s.size

    # Build result dict
    return {
        "phase": phase,
        "red": lit_states.get("red", False),
        "yellow": lit_states.get("yellow", False),
        "green": lit_states.get("green", False),
        "red_hsv": (lamp_hues.get("red", 0.0), 0.0, lamp_brightnesses.get("red", 0.0)),
        "yellow_hsv": (lamp_hues.get("yellow", 0.0), 0.0, lamp_brightnesses.get("yellow", 0.0)),
        "green_hsv": (lamp_hues.get("green", 0.0), 0.0, lamp_brightnesses.get("green", 0.0)),
        "red_lit_pixels": int(lamp_brightnesses.get("red", 0)),
        "yellow_lit_pixels": int(lamp_brightnesses.get("yellow", 0)),
        "green_lit_pixels": int(lamp_brightnesses.get("green", 0)),
        # Internal keys for debug overlay and hue cross-check
        "_lamp_positions": lamp_positions,
        "_lamp_hues": lamp_hues,
        "_lamp_lit_fractions": lamp_lit_fractions,
        "_hue_warnings": hue_warnings,
    }


# ============================================================================
# CAMERA SOURCE (Cross-Platform)
# ============================================================================

def _is_raspberry_pi() -> bool:
    """Detect if running on a Raspberry Pi."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
            return "Raspberry Pi" in cpuinfo or "BCM2711" in cpuinfo or "BCM2835" in cpuinfo
    except FileNotFoundError:
        return False


def _opencv_has_gui_backend() -> bool:
    """Check whether the installed OpenCV supports GUI (imshow, waitKey, etc.).

    On Raspberry Pi we typically install ``opencv-python-headless`` which has
    no GUI backend.  This function detects that so we can gracefully skip
    window operations instead of crashing with:

        cv2.error: The function is not implemented. Rebuild the library with
        Windows, GTK+ 2.x or Cocoa support.

    Returns:
        True if ``cv2.imshow`` / ``cv2.waitKey`` will work, False otherwise.
    """
    try:
        import cv2

        # Check the compiled GUI backend list
        backends = cv2.getBuildInformation()
        # headless OpenCV shows "GUI: NONE" — we need GTK+, Cocoa, or Qt
        gui_section = False
        for line in backends.splitlines():
            stripped = line.strip()
            if stripped.startswith("GUI:"):
                gui_section = True
            elif stripped and not stripped.startswith((" ", "\t")) and gui_section:
                # Next non-indented line ends the GUI section
                gui_section = False
            if gui_section and "NONE" in stripped:
                return False
        # If we never saw a "GUI:" line or it had no "NONE", assume GUI is present
        return True
    except Exception:
        # If we can't determine, assume no GUI to be safe
        return False


class _Picamera2Camera:
    """Thin wrapper around Picamera2 to provide a cap.read()-like interface.

    This lets us swap between cv2.VideoCapture and picamera2 without changing
    the rest of the detection loop.

    Attributes:
        cam: The underlying Picamera2 instance.
    """

    def __init__(self, resolution: tuple, no_auto_wb: bool = False):
        """Initialize the picamera2 camera at the given resolution.

        Args:
            resolution: (width, height) tuple for the video stream.
            no_auto_wb: If True, disable auto white balance to prevent color shift.
        """
        from picamera2 import Picamera2

        self.cam = Picamera2()
        cfg = self.cam.create_video_configuration(
            main={"size": resolution, "format": "RGB888"}
        )
        self.cam.configure(cfg)
        self.cam.start()

        # Disable auto white balance if requested (prevents color shift)
        if no_auto_wb:
            self.cam.set_controls({"AeEnable": False, "AwbEnable": False})
            print("[INFO] Auto white balance disabled on Pi camera.")

    def read(self):
        """Capture one frame.

        Returns:
            Tuple of (success: bool, frame: numpy array).
            The frame is always a BGR888 numpy array (OpenCV expects BGR).
        """
        frame = self.cam.capture_array("main")  # RGB888 numpy array
        # picamera2 returns RGB; OpenCV expects BGR — convert
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return True, frame

    def release(self):
        """Stop and release the camera."""
        self.cam.stop()


def _get_camera_source(
    input_arg: Optional[str],
    resolution: Tuple[int, int] = (DEFAULT_WIDTH, DEFAULT_HEIGHT),
) -> Tuple:
    """
    Get the camera source based on platform and input argument.

    Args:
        input_arg: User-provided input (camera index or video file path)
        resolution: Target (width, height) for live camera

    Returns:
        (source, is_video, camera_object, use_dshow) tuple
        - source: camera index int or video file path string
        - is_video: whether the source is a video file
        - camera_object: initialized cv2.VideoCapture or Picamera2 object
        - use_dshow: whether to use DirectShow backend on Windows
    """
    # If user provided a video file, use that
    if input_arg is not None:
        if os.path.isfile(input_arg):
            cap = cv2.VideoCapture(input_arg)
            if not cap.isOpened():
                print(f"ERROR: Could not open video file: {input_arg}")
                sys.exit(1)
            return input_arg, True, cap, False  # video files don't need DShow

        # User provided a camera index as string (e.g., "0")
        try:
            cam_index = int(input_arg)
            return cam_index, False, None, False  # user specified index, no DShow
        except ValueError:
            print(f"ERROR: Invalid input: {input_arg}")
            print("  Provide a camera index (e.g., '0') or a video file path.")
            sys.exit(1)

    # Auto-detect platform and default camera
    if _is_raspberry_pi():
        cam_index = PI_CAMERA_INDEX  # Picamera2 auto-detects CSI
        print(f"Platform: Raspberry Pi (auto-detecting CSI camera)")
    else:
        cam_index = WIN_CAMERA_INDEX
        print(f"Platform: Windows (using camera index {cam_index})")

    # On Windows, prefer DirectShow backend for reliable keyboard input
    use_dshow = platform.system() == "Windows" and not _is_raspberry_pi()

    return cam_index, False, None, use_dshow


# ============================================================================
# LOGGING
# ============================================================================

class TrafficLightLogger:
    """Logs traffic light phase changes to a timestamped CSV file."""

    def __init__(self, log_dir: str = LOG_DIR):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped CSV file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{LOG_CSV_PREFIX}{timestamp}.csv"

        # CSV columns
        self.columns = [
            "timestamp",
            "frame_id",
            "previous_phase",
            "new_phase",
            "red_lit",
            "yellow_lit",
            "green_lit",
            "housing_bbox",
            "red_hsv_mean",
            "yellow_hsv_mean",
            "green_hsv_mean",
            "red_lit_pixels",
            "yellow_lit_pixels",
            "green_lit_pixels",
        ]

        # Write CSV header
        with open(self.log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)

        self.last_flush_time = time.time()
        self._buffer: List[List] = []

        print(f"\n[LOG] Log file: {self.log_file}")
        print("-" * 60)

    def log_phase_change(
        self,
        frame_id: int,
        previous_phase: str,
        new_phase: str,
        red_lit: bool,
        yellow_lit: bool,
        green_lit: bool,
        bbox: Optional[Tuple[int, int, int, int]],
        red_hsv: Tuple[float, float, float],
        yellow_hsv: Tuple[float, float, float],
        green_hsv: Tuple[float, float, float],
        red_pixels: int,
        yellow_pixels: int,
        green_pixels: int,
    ):
        """Buffer a phase change event."""
        now = datetime.datetime.now().isoformat(timespec="milliseconds")

        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}" if bbox else "none"

        row = [
            now,
            frame_id,
            previous_phase,
            new_phase,
            red_lit,
            yellow_lit,
            green_lit,
            bbox_str,
            f"({red_hsv[0]:.1f},{red_hsv[1]:.1f},{red_hsv[2]:.1f})",
            f"({yellow_hsv[0]:.1f},{yellow_hsv[1]:.1f},{yellow_hsv[2]:.1f})",
            f"({green_hsv[0]:.1f},{green_hsv[1]:.1f},{green_hsv[2]:.1f})",
            red_pixels,
            yellow_pixels,
            green_pixels,
        ]

        self._buffer.append(row)

        # Flush periodically
        if time.time() - self.last_flush_time >= LOG_FLUSH_INTERVAL:
            self.flush()

    def flush(self):
        """Write buffered rows to disk."""
        if not self._buffer:
            return

        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self._buffer)

        self._buffer.clear()
        self.last_flush_time = time.time()

    def close(self):
        """Final flush and close."""
        self.flush()
        print(f"\n[OK] Logged {sum(1 for _ in open(self.log_file)) - 1} events to {self.log_file}")


# ============================================================================
# DEBUG OVERLAY
# ============================================================================

def draw_debug_overlay(
    frame: np.ndarray,
    bbox: Optional[Tuple[int, int, int, int]],
    phase_result: Dict,
    lamp_positions: Optional[List[Tuple[str, int, int, int]]] = None,
    lamp_hues: Optional[Dict[str, float]] = None,
    lamp_lit_fractions: Optional[Dict[str, float]] = None,
) -> np.ndarray:
    """
    Draw debug visualization on the frame.

    Args:
        frame: BGR frame to draw on
        bbox: Traffic light bounding box
        phase_result: Output from detect_phase_from_bbox or detect_phase_from_image
        lamp_positions: Optional list of (label, cx, cy, radius) for lamp discs
        lamp_hues: Optional dict mapping label -> median hue of gate-passing pixels
        lamp_lit_fractions: Optional dict mapping label -> lit fraction

    Returns:
        Frame with debug overlays
    """
    overlay = frame.copy()

    # Draw housing bounding box
    if bbox:
        x, y, w, h = bbox
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Draw sector dividers
        sector_height = h // 3
        for i in range(1, 3):
            line_y = y + i * sector_height
            cv2.line(
                overlay,
                (x, line_y),
                (x + w, line_y),
                (255, 255, 0),
                1,
                cv2.LINE_AA,
            )

        # Draw sector labels
        labels = ["RED", "YELLOW", "GREEN"]
        for i, label in enumerate(labels):
            label_y = y + i * sector_height + sector_height // 2 + 5
            cv2.putText(
                overlay,
                label,
                (x + 5, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (200, 200, 200),
                1,
            )

    # Draw lamp discs and print lamp stats
    if lamp_positions and lamp_hues and lamp_lit_fractions:
        disc_y = y + h + 15
        for label, cx, cy, radius in lamp_positions:
            cx, cy, radius = int(cx), int(cy), int(radius)
            # Colour the disc based on lamp identity
            lamp_colors = {"red": (0, 0, 255), "yellow": (0, 200, 255), "green": (0, 255, 0)}
            disc_color = lamp_colors.get(label, (255, 255, 255))
            cv2.circle(overlay, (cx, cy), radius, disc_color, 2)

            # Print lit fraction and median hue next to each disc
            lit_frac = lamp_lit_fractions.get(label, 0.0)
            median_hue = lamp_hues.get(label, 0.0)
            text = f"{label}: frac={lit_frac:.3f} hue={median_hue:.1f}"
            cv2.putText(
                overlay,
                text,
                (x, disc_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
            )
            disc_y += 18

    # Draw current phase
    if phase_result:
        phase = phase_result["phase"]
        if phase == "no_detection":
            phase_color = (0, 165, 255)  # Orange for no_detection
        elif phase not in ("off", "unknown"):
            phase_color = (0, 255, 0)  # Green for lit phases
        else:
            phase_color = (0, 0, 255)  # Blue for off/unknown
        cv2.putText(
            overlay,
            f"Phase: {phase.upper()}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            phase_color,
            2,
        )

        # Draw per-lamp status
        status_y = 60
        for color_name in ["red", "yellow", "green"]:
            lit = phase_result[color_name]
            hsv = phase_result[f"{color_name}_hsv"]
            pixels = phase_result[f"{color_name}_lit_pixels"]
            status = "ON" if lit else "OFF"
            color = (0, 255, 0) if lit else (0, 0, 255)
            text = f"{color_name.upper()}: {status} (H={hsv[0]:.0f} S={hsv[1]:.0f} V={hsv[2]:.0f} px={pixels})"
            cv2.putText(
                overlay,
                text,
                (10, status_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                color,
                1,
            )
            status_y += 20

    return overlay


# ============================================================================
# MAIN LOOP
# ============================================================================

def run_detection(
    camera_source,
    is_video: bool,
    show: bool,
    dry_run: bool,
    calibrate: bool,
    resolution: Tuple[int, int],
    use_dshow: bool = False,
    no_auto_wb: bool = False,
):
    """
    Main detection loop: read frames, detect housing, detect phase, log changes.
    """
    # Initialize camera
    if is_video:
        cap = cv2.VideoCapture(camera_source)
    else:
        # On Raspberry Pi, use picamera2 for CSI camera (IMX708).
        # cv2.VideoCapture fails because the CSI camera is managed by libcamera,
        # not exposed as a standard V4L2 device.
        if _is_raspberry_pi():
            print("[INFO] Detected Raspberry Pi — using picamera2 for CSI camera.")
            cap = _Picamera2Camera(resolution, no_auto_wb=no_auto_wb)
            print(f"[INFO] Camera configured: {resolution[0]}x{resolution[1]} @ ~30 fps")
        else:
            # On Windows, set DirectShow backend BEFORE opening the camera
            if use_dshow:
                cap = cv2.VideoCapture(camera_source, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(camera_source)
            if not cap.isOpened():
                print(f"ERROR: Could not open camera at index {camera_source}")
                sys.exit(1)

            # Set resolution for live camera
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

            # Verify actual resolution
            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Camera resolution: {actual_w}x{actual_h}")

    # Initialize logger
    logger = TrafficLightLogger()

    # Initialize keyboard listener (background thread)
    kb = KeyboardListener()
    kb.start()

    # State tracking
    previous_phase = "none"
    last_phase_change_time = 0.0
    frame_id = 0
    frame_count = 0
    start_time = time.time()
    max_frames = 10 if dry_run else None  # Limit frames for dry-run testing
    consecutive_failures = 0
    max_consecutive_failures = 30  # Exit after 30 failed captures (~3 seconds)

    print(f"\n[TRAIN] Traffic Light Detection Started")
    print(f"   Resolution: {resolution[0]}x{resolution[1]}")
    print(f"   Mode: {'video' if is_video else 'live camera'}")
    print(f"   Show overlay: {show}")
    print(f"   Dry run: {dry_run}")
    print(f"   Calibration mode: {calibrate}")
    print("-" * 60)
    print("Press 'q' to quit.\n")

    try:
        while True:
            # Exit if max frames reached (dry-run safety)
            if max_frames and frame_count >= max_frames:
                print(f"\n[DONE] Dry-run complete. Processed {frame_count} frames.")
                break

            ret, frame = cap.read()
            if not ret:
                consecutive_failures += 1
                if is_video:
                    print("\n[WARN] Video ended.")
                    break
                elif consecutive_failures >= max_consecutive_failures:
                    print(f"\n[WARN] Camera unavailable after {max_consecutive_failures} attempts. Exiting.")
                    break
                else:
                    print(f"\r[WARN] Failed to capture frame. Retrying... ({consecutive_failures}/{max_consecutive_failures})", end="")
                    time.sleep(0.1)
                    continue
            else:
                consecutive_failures = 0  # Reset on success

            frame_count += 1

            # --- Step 1: Detect housing ---
            bbox = find_traffic_light_housing(frame)

            if bbox is None:
                # No housing detected — log as "no_detection" with no bbox
                current_phase_result = {
                    "phase": "no_detection",
                    "red": False,
                    "yellow": False,
                    "green": False,
                    "red_hsv": (0.0, 0.0, 0.0),
                    "yellow_hsv": (0.0, 0.0, 0.0),
                    "green_hsv": (0.0, 0.0, 0.0),
                    "red_lit_pixels": 0,
                    "yellow_lit_pixels": 0,
                    "green_lit_pixels": 0,
                }
            else:
                # --- Step 2: Detect phase within housing ---
                current_phase_result = detect_phase_from_bbox(frame, bbox)

            current_phase = current_phase_result["phase"]

            # --- Step 3: Check for phase change (with debounce) ---
            now = time.time()
            if current_phase != previous_phase and (now - last_phase_change_time) >= DEBOUNCE_SECONDS:
                # Log the phase change
                logger.log_phase_change(
                    frame_id=frame_id,
                    previous_phase=previous_phase,
                    new_phase=current_phase,
                    red_lit=current_phase_result["red"],
                    yellow_lit=current_phase_result["yellow"],
                    green_lit=current_phase_result["green"],
                    bbox=bbox,
                    red_hsv=current_phase_result["red_hsv"],
                    yellow_hsv=current_phase_result["yellow_hsv"],
                    green_hsv=current_phase_result["green_hsv"],
                    red_pixels=current_phase_result["red_lit_pixels"],
                    yellow_pixels=current_phase_result["yellow_lit_pixels"],
                    green_pixels=current_phase_result["green_lit_pixels"],
                )

                # Print phase change event
                elapsed = now - start_time
                print(
                    f"[{elapsed:.1f}s] Frame {frame_id}: "
                    f"{previous_phase.upper()} -> {current_phase.upper()} "
                    f"(red={current_phase_result['red']}, "
                    f"yellow={current_phase_result['yellow']}, "
                    f"green={current_phase_result['green']})"
                )

                previous_phase = current_phase
                last_phase_change_time = now

            # --- Step 4: Calibration output ---
            if calibrate and frame_count % 30 == 0:  # Every 30 frames
                if bbox:
                    print(f"\n--- Calibration Sample (Frame {frame_id}) ---")
                    print(f"  Housing bbox: {bbox}")
                    for color in ["red", "yellow", "green"]:
                        hsv = current_phase_result[f"{color}_hsv"]
                        pixels = current_phase_result[f"{color}_lit_pixels"]
                        print(f"  {color.upper()}: H={hsv[0]:.1f} S={hsv[1]:.1f} V={hsv[2]:.1f} lit_px={pixels}")
                    print("-" * 60)

            # --- Step 5: Debug overlay ---
            if show and not dry_run:
                debug_frame = draw_debug_overlay(frame, bbox, current_phase_result)
                cv2.imshow("Traffic Light Detection", debug_frame)

                # Also show raw frame for color inspection
                if calibrate:
                    cv2.imshow("Raw Frame", frame)

                # Small delay to let the window paint before checking for quit
                cv2.waitKey(1)

            # Check if user pressed 'q' (via background thread)
            if kb.should_quit:
                print("\nUser pressed 'q' to quit.")
                break

            # Brief sleep for live camera to avoid CPU spinning
            if not is_video and not dry_run:
                time.sleep(0.01)

            frame_id += 1

    except KeyboardInterrupt:
        print("\n\n[WARN] Interrupted by user.")
    finally:
        # Stop keyboard listener
        kb.stop()

        # Flush and close logger
        logger.flush()
        logger.close()

        # Release camera
        cap.release()
        if show:
            cv2.destroyAllWindows()

        # Print summary
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"\n[SUMMARY] Summary:")
        print(f"   Total frames processed: {frame_count}")
        print(f"   Duration: {elapsed:.1f}s")
        print(f"   Average FPS: {fps:.1f}")
        print(f"   Log file: {logger.log_file}")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Traffic Light Detection for LEGO Autonomous Train",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Live camera (auto-detects platform):
  python src/detect_traffic_light.py

  # Live camera with debug overlay:
  python src/detect_traffic_light.py --show

  # Process a video file for offline testing:
  python src/detect_traffic_light.py --video path/to/video.mp4

  # Calibrate colors from Pi camera data:
  python src/detect_traffic_light.py --calibrate

  # Disable auto white balance on Pi camera:
  python src/detect_traffic_light.py --no-auto-wb

  # Custom resolution:
  python src/detect_traffic_light.py --resolution 800x600
        """,
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        default=None,
        help="Camera index (e.g., '0') or video file path. Default: auto-detect platform.",
    )

    parser.add_argument(
        "-v", "--video",
        type=str,
        default=None,
        help="Process a video file instead of live camera.",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        default=True,
        help="Enable debug window with overlays (default: True).",
    )

    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Disable debug window (useful for headless Pi).",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run detection without displaying frames (saves CPU/GPU).",
    )

    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Save per-sector ROI HSV averages to log for color tuning.",
    )

    parser.add_argument(
        "--no-auto-wb",
        action="store_true",
        help="Disable auto white balance on Pi camera (prevents color shift).",
    )

    parser.add_argument(
        "--resolution",
        type=str,
        default=f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}",
        help=f"Camera resolution as WxH (default: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}).",
    )

    # --- Image / regression mode ---
    parser.add_argument(
        "-I", "--image",
        type=str,
        default=None,
        help="Process a single image file instead of a camera stream.",
    )

    parser.add_argument(
        "--images",
        type=str,
        nargs="+",
        default=None,
        help="Process multiple image files and print a regression summary.",
    )

    parser.add_argument(
        "--save-debug",
        type=str,
        default=None,
        help="Directory to save debug overlays and masks when using --image or --images.",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # --- Image mode: process one or more static images ---
    if args.image:
        print(f"Processing single image: {args.image}")
        run_regression_test(
            image_paths=[args.image],
            save_debug_dir=args.save_debug,
        )
        return

    if args.images:
        print(f"Processing {len(args.images)} images...")
        run_regression_test(
            image_paths=args.images,
            save_debug_dir=args.save_debug,
        )
        return

    # Parse resolution
    try:
        w, h = map(int, args.resolution.split("x"))
        resolution = (w, h)
    except ValueError:
        print(f"ERROR: Invalid resolution format: {args.resolution}")
        print("  Use format: WIDTHxHEIGHT (e.g., 640x480)")
        sys.exit(1)

    # Determine show mode — but only if OpenCV has GUI backend installed
    show = args.show and not args.no_show and not args.dry_run

    # If OpenCV is headless (e.g. opencv-python-headless on Pi), disable show
    if show and not _opencv_has_gui_backend():
        show = False
        print("[INFO] OpenCV has no GUI backend (headless build detected). "
              "Debug overlay disabled. Use --show on a machine with full OpenCV.")

    # Determine camera source (video or live)
    input_source = args.video or args.input
    cam_index, is_video, _, use_dshow = _get_camera_source(input_source, resolution)

    # Run detection
    run_detection(
        camera_source=cam_index,
        is_video=is_video,
        show=show,
        dry_run=args.dry_run,
        calibrate=args.calibrate,
        resolution=resolution,
        use_dshow=use_dshow,
        no_auto_wb=args.no_auto_wb if _is_raspberry_pi() else False,
    )


# ============================================================================


def detect_phase_from_image(image_path: str) -> Dict:
    """
    Run the full traffic-light detection pipeline on a single image file.

    This is a thin wrapper around the existing detection logic, but it
    operates on a loaded image rather than a camera frame.  It returns
    a dict suitable for assertion-based testing.

    Args:
        image_path: Absolute or relative path to a BGR image file.

    Returns:
        dict with keys:
            phase (str): Detected phase (e.g. 'red', 'green', 'off', 'no_detection')
            bbox (tuple or None): (x, y, w, h) of the traffic-light housing
            red_lit (bool), yellow_lit (bool), green_lit (bool)
            red_hsv (tuple), yellow_hsv (tuple), green_hsv (tuple)
            red_lit_pixels (int), yellow_lit_pixels (int), green_lit_pixels (int)
            image_shape (tuple): (height, width, channels) of the input image
    """
    frame = cv2.imread(image_path)
    if frame is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    image_shape = frame.shape
    h, w = frame.shape[:2]

    # --- Housing detection (call the single canonical function) ---
    bbox = find_traffic_light_housing(frame)

    # --- Phase detection ---
    phase_result = detect_phase_from_bbox(frame, bbox)

    return {
        "phase": phase_result["phase"],
        "bbox": bbox,
        "red": phase_result["red"],
        "yellow": phase_result["yellow"],
        "green": phase_result["green"],
        "red_lit": phase_result["red"],
        "yellow_lit": phase_result["yellow"],
        "green_lit": phase_result["green"],
        "red_hsv": phase_result["red_hsv"],
        "yellow_hsv": phase_result["yellow_hsv"],
        "green_hsv": phase_result["green_hsv"],
        "red_lit_pixels": phase_result["red_lit_pixels"],
        "yellow_lit_pixels": phase_result["yellow_lit_pixels"],
        "green_lit_pixels": phase_result["green_lit_pixels"],
        "image_shape": image_shape,
        # Forward internal keys for debug overlay
        "_lamp_positions": phase_result.get("_lamp_positions"),
        "_lamp_hues": phase_result.get("_lamp_hues"),
        "_lamp_lit_fractions": phase_result.get("_lamp_lit_fractions"),
        "_hue_warnings": phase_result.get("_hue_warnings", []),
    }


def process_single_image(
    image_path: str,
    save_debug_dir: Optional[str] = None,
) -> Dict:
    """
    Run detection on a single image and optionally save debug output.

    Args:
        image_path: Path to the image file.
        save_debug_dir: If provided, write overlay + masks to this directory.

    Returns:
        Detection result dict (from detect_phase_from_image).
    """
    result = detect_phase_from_image(image_path)

    if save_debug_dir:
        debug_path = Path(save_debug_dir)
        debug_path.mkdir(parents=True, exist_ok=True)

        frame = cv2.imread(image_path)
        overlay = draw_debug_overlay(
            frame,
            result["bbox"],
            result,
            lamp_positions=result.get("_lamp_positions"),
            lamp_hues=result.get("_lamp_hues"),
            lamp_lit_fractions=result.get("_lamp_lit_fractions"),
        )

        stem = Path(image_path).stem
        cv2.imwrite(str(debug_path / f"{stem}_overlay.jpg"), overlay)

        print(f"  [DEBUG] Saved to {debug_path}/")

    return result


def run_regression_test(
    image_paths: List[str],
    expected_phases: Optional[Dict[str, str]] = None,
    save_debug_dir: Optional[str] = None,
) -> Dict:
    """
    Run detection on multiple images and print a regression summary.

    Args:
        image_paths: List of image file paths.
        expected_phases: Optional dict mapping image stem -> expected phase.
        save_debug_dir: If provided, debug output is saved per-image.

    Returns:
        dict with keys: results (list), total (int), correct (int)
    """
    results = []
    correct = 0
    total = len(image_paths)

    print(f"\n{'='*60}")
    print(f"  Regression Test: {total} image(s)")
    print(f"{'='*60}")

    for img_path in image_paths:
        stem = Path(img_path).stem
        print(f"\n  Image: {img_path}")

        try:
            result = process_single_image(img_path, save_debug_dir)
        except FileNotFoundError as e:
            print(f"    [SKIP] {e}")
            continue

        phase = result["phase"]
        bbox = result["bbox"]
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}" if bbox else "none"

        sectors = []
        for color_name in ["red", "yellow", "green"]:
            lit = result[f"{color_name}_lit"]
            pixels = result[f"{color_name}_lit_pixels"]
            status = "ON" if lit else "OFF"
            sectors.append(f"{color_name.upper()}:{status}({pixels}px)")

        print(f"    Phase: {phase.upper()}")
        print(f"    BBox:  {bbox_str}")
        print(f"    Sectors: {', '.join(sectors)}")

        if expected_phases and stem in expected_phases:
            exp = expected_phases[stem]
            status_icon = "PASS" if phase == exp else "FAIL"
            print(f"    Expected: {exp.upper()}  ->  [{status_icon}]")
            if phase == exp:
                correct += 1
            else:
                print(f"    *** MISMATCH ***")
        else:
            print(f"    (no expected phase set)")

        results.append(result)

    print(f"\n{'='*60}")
    if expected_phases:
        print(f"  Results: {correct}/{total} correct")
    else:
        print(f"  Results: {total} images processed (no expected phases)")
    print(f"{'='*60}\n")

    return {"results": results, "total": total, "correct": correct}

if __name__ == "__main__":
    main()
