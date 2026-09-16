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
  python scripts/detect_traffic_light.py

  # Live camera with debug overlay:
  python scripts/detect_traffic_light.py --show

  # Process a video file for offline testing:
  python scripts/detect_traffic_light.py --video path/to/video.mp4

  # Process a single image (for debugging):
  python scripts/detect_traffic_light.py --image media/traffic_light_green.jpg

  # Process multiple images and print a regression summary:
  python scripts/detect_traffic_light.py --images media/traffic_light_green.jpg media/traffic_light_red.jpg

  # Save debug overlays and masks to a directory:
  python scripts/detect_traffic_light.py --images media/traffic_light_*.jpg --save-debug debug_output/

  # Calibrate colors from Pi camera data:
  python scripts/detect_traffic_light.py --calibrate

  # Disable auto white balance to prevent color shift on Pi:
  python scripts/detect_traffic_light.py --no-auto-wb

  # Custom resolution:
  python scripts/detect_traffic_light.py --resolution 800x600
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

# --- Housing Detection ---
# Red color range (HSV) — captures the red housing body
HOUSING_RED_LOW = np.array([0, 80, 80], dtype=np.uint8)
HOUSING_RED_HIGH = np.array([15, 255, 255], dtype=np.uint8)

# White color range (HSV) — captures the white diagonal stripes
HOUSING_WHITE_LOW = np.array([0, 10, 180], dtype=np.uint8)
HOUSING_WHITE_HIGH = np.array([15, 50, 255], dtype=np.uint8)

HOUSING_MIN_AREA = 500          # px² minimum blob size
HOUSING_MAX_AREA = 500_000     # px² maximum (avoids whole-frame matches)
HOUSING_MIN_ASPECT_RATIO = 0.3  # narrow bounding box allowed
HOUSING_MAX_ASPECT_RATIO = 3.0  # wide bounding box allowed

# --- Phase Detection ---
# How much of each sector to sample (center region, avoids housing edges)
LIGHT_INNER_RATIO = 0.6         # sample center 60% of each sector

# Minimum fraction of sampled area that must be lit to count as ON
MIN_LIT_FRACTION = 0.05         # >5% of sector must be lit

# HSV thresholds for each light color (BGR -> HSV via cvtColor)
# These were tuned for iPhone photos — use --calibrate on Pi data to refine
RED_LOW = np.array([0, 120, 80], dtype=np.uint8)
RED_HIGH = np.array([15, 255, 255], dtype=np.uint8)
# Red wraps around hue=0, so we also check the high end
RED_LOW_HIGH_HUE = np.array([140, 120, 80], dtype=np.uint8)
RED_HIGH_HIGH_HUE = np.array([175, 255, 255], dtype=np.uint8)

YELLOW_LOW = np.array([25, 120, 80], dtype=np.uint8)
YELLOW_HIGH = np.array([35, 255, 255], dtype=np.uint8)

GREEN_LOW = np.array([40, 120, 80], dtype=np.uint8)
GREEN_HIGH = np.array([75, 255, 255], dtype=np.uint8)

# --- Debounce ---
DEBOUNCE_SECONDS = 0.5          # minimum time between phase change events

# --- Camera Defaults ---
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
TARGET_FPS = 30
PI_CAMERA_INDEX = -1            # Picamera2 auto-detects CSI camera
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
    Detect the traffic light housing in the frame using red+white stripe
    color segmentation and contour filtering.

    Args:
        frame: BGR image from camera

    Returns:
        (x, y, w, h) bounding box of the traffic light, or None if not found
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Mask for red housing
    mask_red = cv2.inRange(hsv, HOUSING_RED_LOW, HOUSING_RED_HIGH)

    # Mask for white stripes
    mask_white = cv2.inRange(hsv, HOUSING_WHITE_LOW, HOUSING_WHITE_HIGH)

    # Combine masks (red OR white)
    mask_combined = cv2.bitwise_or(mask_red, mask_white)

    # Morphological operations to connect nearby blobs
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_combined = cv2.erode(mask_combined, kernel, iterations=2)
    mask_combined = cv2.dilate(mask_combined, kernel, iterations=3)

    # Find contours
    contours, _ = cv2.findContours(
        mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    best_bbox = None
    best_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)

        # Filter by area
        if area < HOUSING_MIN_AREA or area > HOUSING_MAX_AREA:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / max(h, 1)

        # Filter by aspect ratio (traffic light is roughly square-ish)
        if aspect_ratio < HOUSING_MIN_ASPECT_RATIO or aspect_ratio > HOUSING_MAX_ASPECT_RATIO:
            continue

        # Select the largest valid contour
        if area > best_area:
            best_area = area
            best_bbox = (x, y, w, h)

    return best_bbox


# ============================================================================
# PHASE DETECTION
# ============================================================================

def detect_phase_from_bbox(
    frame: np.ndarray,
    bbox: Tuple[int, int, int, int],
) -> Dict:
    """
    Detect which lights are ON within the traffic light bounding box.

    Divides the bounding box into 3 vertical sectors:
      - Top third: RED light
      - Middle third: YELLOW light
      - Bottom third: GREEN light

    For each sector, counts pixels matching the target color's HSV range.

    Args:
        frame: BGR image from camera
        bbox: (x, y, w, h) traffic light bounding box

    Returns:
        Dict with keys:
          - 'phase': str — detected phase name
          - 'red': bool — is red light lit?
          - 'yellow': bool — is yellow light lit?
          - 'green': bool — is green light lit?
          - 'red_hsv': tuple — average HSV of red sector
          - 'yellow_hsv': tuple — average HSV of yellow sector
          - 'green_hsv': tuple — average HSV of green sector
          - 'red_lit_pixels': int — count of red-matching pixels
          - 'yellow_lit_pixels': int — count of yellow-matching pixels
          - 'green_lit_pixels': int — count of green-matching pixels
    """
    x, y, w, h = bbox
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Divide bounding box into 3 equal vertical sectors
    sector_height = h // 3
    sectors = [
        ("red", y, y + sector_height),
        ("yellow", y + sector_height, y + 2 * sector_height),
        ("green", y + 2 * sector_height, y + h),
    ]

    results = {"red": False, "yellow": False, "green": False}
    hsv_means = {}
    lit_pixel_counts = {}

    for color_name, y_start, y_end in sectors:
        # Clamp to frame bounds
        y_start = max(0, y_start)
        y_end = min(hsv.shape[0], y_end)

        # Clip to bounding box horizontally
        x_start = max(0, x)
        x_end = min(hsv.shape[1], x + w)

        # Extract sector ROI
        sector_roi = hsv[y_start:y_end, x_start:x_end]

        if sector_roi.size == 0:
            hsv_means[color_name] = (0.0, 0.0, 0.0)
            lit_pixel_counts[color_name] = 0
            continue

        # Sample center region (avoids housing edges)
        inner_x_start = int(x_start + w * (1 - LIGHT_INNER_RATIO) / 2)
        inner_x_end = int(x_start + w * (1 + LIGHT_INNER_RATIO) / 2)
        inner_y_start = int(y_start + sector_height * (1 - LIGHT_INNER_RATIO) / 2)
        inner_y_end = int(y_start + sector_height * (1 + LIGHT_INNER_RATIO) / 2)

        inner_roi = sector_roi[inner_y_start - y_start:inner_y_end - y_start,
                               inner_x_start - x_start:inner_x_end - x_start]

        # Average HSV of sampled region
        avg_h = float(np.mean(inner_roi[:, :, 0]))
        avg_s = float(np.mean(inner_roi[:, :, 1]))
        avg_v = float(np.mean(inner_roi[:, :, 2]))
        hsv_means[color_name] = (avg_h, avg_s, avg_v)

        # Count pixels matching the target color range
        if color_name == "red":
            # Red wraps around hue=0, so check two ranges
            mask1 = cv2.inRange(inner_roi, RED_LOW, RED_HIGH)
            mask2 = cv2.inRange(inner_roi, RED_LOW_HIGH_HUE, RED_HIGH_HIGH_HUE)
            mask = cv2.bitwise_or(mask1, mask2)
        elif color_name == "yellow":
            mask = cv2.inRange(inner_roi, YELLOW_LOW, YELLOW_HIGH)
        elif color_name == "green":
            mask = cv2.inRange(inner_roi, GREEN_LOW, GREEN_HIGH)
        else:
            mask = np.zeros(inner_roi.shape[:2], dtype=np.uint8)

        lit_pixels = int(np.count_nonzero(mask))
        lit_pixel_counts[color_name] = lit_pixels

        # Determine if the light is "on" based on lit pixel fraction
        total_pixels = inner_roi.shape[0] * inner_roi.shape[1]
        if total_pixels > 0:
            lit_fraction = lit_pixels / total_pixels
            results[color_name] = lit_fraction >= MIN_LIT_FRACTION

    # Compile phase from individual light states
    phase = _compute_phase(results)

    return {
        "phase": phase,
        "red": results["red"],
        "yellow": results["yellow"],
        "green": results["green"],
        "red_hsv": hsv_means.get("red", (0.0, 0.0, 0.0)),
        "yellow_hsv": hsv_means.get("yellow", (0.0, 0.0, 0.0)),
        "green_hsv": hsv_means.get("green", (0.0, 0.0, 0.0)),
        "red_lit_pixels": lit_pixel_counts.get("red", 0),
        "yellow_lit_pixels": lit_pixel_counts.get("yellow", 0),
        "green_lit_pixels": lit_pixel_counts.get("green", 0),
    }


def _compute_phase(lights: Dict[str, bool]) -> str:
    """
    Map individual light states to a phase name.

    Args:
        lights: Dict with 'red', 'yellow', 'green' boolean keys

    Returns:
        Phase name string
    """
    red = lights["red"]
    yellow = lights["yellow"]
    green = lights["green"]

    if red and yellow:
        return "red+yellow"
    elif red:
        return "red"
    elif yellow:
        return "yellow"
    elif green:
        return "green"
    elif not any(lights.values()):
        return "off"
    else:
        # Fallback for unexpected combinations
        return "unknown"


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
) -> np.ndarray:
    """
    Draw debug visualization on the frame.

    Args:
        frame: BGR frame to draw on
        bbox: Traffic light bounding box
        phase_result: Output from detect_phase_from_bbox

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

    # Draw current phase
    if phase_result:
        phase = phase_result["phase"]
        phase_color = (0, 255, 0) if phase not in ("off", "unknown") else (0, 0, 255)
        cv2.putText(
            overlay,
            f"Phase: {phase.upper()}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            phase_color,
            2,
        )

        # Draw per-sector status
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
):
    """
    Main detection loop: read frames, detect housing, detect phase, log changes.
    """
    # Initialize camera
    if is_video:
        cap = cv2.VideoCapture(camera_source)
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
                # No housing detected — log as "off" with no bbox
                current_phase_result = {
                    "phase": "off",
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
  python scripts/detect_traffic_light.py

  # Live camera with debug overlay:
  python scripts/detect_traffic_light.py --show

  # Process a video file for offline testing:
  python scripts/detect_traffic_light.py --video path/to/video.mp4

  # Calibrate colors from Pi camera data:
  python scripts/detect_traffic_light.py --calibrate

  # Disable auto white balance on Pi camera:
  python scripts/detect_traffic_light.py --no-auto-wb

  # Custom resolution:
  python scripts/detect_traffic_light.py --resolution 800x600
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

    # Determine show mode
    show = args.show and not args.no_show and not args.dry_run

    # Determine camera source (video or live)
    input_source = args.video or args.input
    cam_index, is_video, _, use_dshow = _get_camera_source(input_source, resolution)

    # Handle Pi camera auto-white-balance
    if args.no_auto_wb and _is_raspberry_pi():
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            # Disable auto white balance to prevent color shift
            picam2.set_controls({"AeEnable": False, "AwbEnable": False})
            print("Auto white balance disabled on Pi camera.")
        except ImportError:
            print("WARNING: picamera2 not available — cannot disable auto white balance.")
        except Exception as e:
            print(f"WARNING: Could not disable auto white balance: {e}")

    # Run detection
    run_detection(
        camera_source=cam_index,
        is_video=is_video,
        show=show,
        dry_run=args.dry_run,
        calibrate=args.calibrate,
        resolution=resolution,
        use_dshow=use_dshow,
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
            masks (dict): intermediate masks ('red', 'white', 'composite')
    """
    frame = cv2.imread(image_path)
    if frame is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    image_shape = frame.shape
    h, w = frame.shape[:2]

    # --- Housing detection ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red mask (with wrap-around)
    mask_red = cv2.inRange(hsv, HOUSING_RED_LOW, HOUSING_RED_HIGH)
    mask_red_wrap = cv2.inRange(
        hsv,
        np.array([168, 80, 80], dtype=np.uint8),
        np.array([180, 255, 255], dtype=np.uint8),
    )
    mask_red = cv2.bitwise_or(mask_red, mask_red_wrap)

    # White mask
    mask_white = cv2.inRange(hsv, HOUSING_WHITE_LOW, HOUSING_WHITE_HIGH)

    # Composite mask
    mask_composite = cv2.bitwise_or(mask_red, mask_white)

    # Morphological closing to connect fragmented stripes
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_composite = cv2.morphologyEx(mask_composite, cv2.MORPH_CLOSE, kernel_close, iterations=2)

    # Erode then dilate to clean noise
    kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_composite = cv2.erode(mask_composite, kernel_erode, iterations=2)
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_composite = cv2.dilate(mask_composite, kernel_dilate, iterations=3)

    # --- Find housing bounding box ---
    contours, _ = cv2.findContours(mask_composite, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bbox = None
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if HOUSING_MIN_AREA <= area <= HOUSING_MAX_AREA:
            x, y, cw, ch = cv2.boundingRect(contour)
            aspect = cw / max(ch, 1)
            if HOUSING_MIN_ASPECT_RATIO <= aspect <= HOUSING_MAX_ASPECT_RATIO:
                if area > max_area:
                    max_area = area
                    bbox = (x, y, cw, ch)

    # --- Phase detection ---
    phase_result = detect_phase_from_bbox(frame, bbox)

    return {
        "phase": phase_result["phase"],
        "bbox": bbox,
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
        "masks": {
            "red": mask_red,
            "white": mask_white,
            "composite": mask_composite,
        },
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
        overlay = draw_debug_overlay(frame, result["bbox"], result)

        stem = Path(image_path).stem
        cv2.imwrite(str(debug_path / f"{stem}_overlay.jpg"), overlay)

        for mask_name, mask_arr in result["masks"].items():
            cv2.imwrite(str(debug_path / f"{stem}_mask_{mask_name}.jpg"), mask_arr)

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


if __name__ == "__main__":
    main()
