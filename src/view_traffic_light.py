#!/usr/bin/env python3
"""
Terminal frontend for traffic light detection.

Displays the currently detected traffic light phase with ANSI-colored text
in the terminal. Only updates the display when the phase actually changes
(debounced), so it doesn't spam the terminal.

Phase color coding:
    GREEN  -> green text
    YELLOW -> yellow text
    RED    -> red text
    RED+YELLOW -> "RED" in red + "YELLOW" in yellow on the same line
    OFF    -> grey text
    NO DETECTION -> grey text

Usage:
    # Live camera on Pi (uses picamera2 for CSI camera):
    python src/view_traffic_light.py

    # Custom camera index:
    python src/view_traffic_light.py --camera 0

    # Process a recorded video file:
    python src/view_traffic_light.py --video data/captured/my_run.mp4

    # Custom resolution:
    python src/view_traffic_light.py --resolution 800x600

    # Quit anytime by pressing 'q'
"""

import argparse
import re
import sys
import time
import threading
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Ensure we can import from detect_traffic_light in the same directory
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from detect_traffic_light import (
    find_traffic_light_housing,
    detect_phase_from_bbox,
    KeyboardListener,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480

# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

# We define color constants so Lev can easily see which escape codes map to
# which colors. ANSI 9x = bright/high-intensity colors (more readable).
class Color:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"        # bright red
    GREEN = "\033[92m"      # bright green
    YELLOW = "\033[93m"     # bright yellow
    GREY = "\033[90m"       # dim grey
    BOLD = "\033[1m"
    RESET = "\033[0m"


# Phase labels and their display colors.
# "red_yellow" is a special multi-color case handled separately.
_PHASE_COLORS = {
    "green":    Color.GREEN,
    "yellow":   Color.YELLOW,
    "red":      Color.RED,
    "off":      Color.GREY,
}


def _ansi_phase_text(phase: str) -> str:
    """Return an ANSI-colored string for a given phase name.

    Args:
        phase: One of 'green', 'yellow', 'red', 'red_yellow', 'off',
               or 'no_detection'.

    Returns:
        A string with embedded ANSI color codes ready to print to the
        terminal.
    """
    if phase == "no_detection":
        return f"{Color.GREY}NO DETECTION{Color.RESET}"

    # Multi-color case: "RED" in red + "YELLOW" in yellow
    if phase == "red_yellow":
        return (
            f"{Color.RED}RED{Color.RESET}"
            f" "
            f"{Color.YELLOW}+{Color.RESET}"
            f" "
            f"{Color.RED}YELLOW{Color.RESET}"
        )

    # Single-color phase
    color = _PHASE_COLORS.get(phase)
    if color is not None:
        return f"{color}{phase.upper()}{Color.RESET}"

    # Unknown phase — grey fallback
    return f"{Color.GREY}{phase.upper()}{Color.RESET}"


# ---------------------------------------------------------------------------
# Terminal display manager
# ---------------------------------------------------------------------------

class PhaseViewer:
    """Manages terminal display of traffic light phases without spamming.

    Uses a carriage return (\\r) so the display updates in-place on the
    same line instead of creating new lines.

    Every frame is printed so Lev can debug detection results in real time.
    """

    def __init__(self):
        self.last_phase = None
        self.frame_count = 0
        self.start_time = time.time()

    def update(self, phase: str):
        """Update the display every frame (for debugging).

        Args:
            phase: Current detected phase name (e.g. 'green', 'off').
        """
        self.frame_count += 1
        current_time = time.time()

        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0.0

        # Build the display line with ANSI color for the phase
        phase_text = _ansi_phase_text(phase)
        status_line = (
            f"\r{Color.BOLD}[Phase Viewer]{Color.RESET} "
            f"Frame {self.frame_count:05d} | "
            f"Elapsed: {elapsed:.1f}s | "
            f"FPS: {fps:5.1f} | "
            f"Status: {phase_text}"
        )

        # Pad with spaces to fully overwrite any previous longer line.
        # We use a fixed terminal width of 80 chars — ANSI escape codes
        # don't take up space on screen. Strip all \033[...] sequences to
        # count only the visible characters.
        visible_len = len(re.sub(r'\033\[[0-9;]*m', '', status_line))
        sys.stdout.write(status_line + " " * max(0, 80 - visible_len))
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def _is_raspberry_pi() -> bool:
    """Detect if running on a Raspberry Pi by checking /proc/cpuinfo.

    Returns:
        True if running on a Raspberry Pi, False otherwise.
    """
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
            return (
                "Raspberry Pi" in cpuinfo
                or "BCM2711" in cpuinfo
                or "BCM2835" in cpuinfo
            )
    except FileNotFoundError:
        return False


# ---------------------------------------------------------------------------
# Picamera2 camera wrapper (for Raspberry Pi CSI camera access)
# ---------------------------------------------------------------------------

class _Picamera2Camera:
    """Thin wrapper around Picamera2 to provide a cap.read()-like interface.

    This lets us swap between cv2.VideoCapture and picamera2 without changing
    the rest of the detection loop.

    Attributes:
        cam: The underlying Picamera2 instance.
    """

    def __init__(self, resolution: tuple):
        """Initialize the picamera2 camera at the given resolution.

        Args:
            resolution: (width, height) tuple for the video stream.
        """
        from picamera2 import Picamera2

        self.cam = Picamera2()
        cfg = self.cam.create_video_configuration(
            main={"size": resolution, "format": "RGB888"}
        )
        self.cam.configure(cfg)
        self.cam.start()

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


# ---------------------------------------------------------------------------
# Main viewer loop
# ---------------------------------------------------------------------------

def run_viewer(
    camera_index: int = -1,
    resolution: tuple = (DEFAULT_WIDTH, DEFAULT_HEIGHT),
    video_path: str | None = None,
):
    """Run the terminal phase viewer.

    Opens a camera (or video file), detects the traffic light phase in each
    frame, and prints the current phase to the terminal with color coding.

    Args:
        camera_index: Camera device index (only used on Windows/macOS).
                      On Raspberry Pi, this is ignored — picamera2 auto-detects
                      the CSI camera.
        resolution: Target (width, height) for live camera.
        video_path: Path to a video file to process instead of live camera.
    """
    # Determine if we're on a Raspberry Pi (CSI camera needs picamera2,
    # not cv2.VideoCapture which defaults to V4L2 /dev/video0)
    is_pi = _is_raspberry_pi()

    # Start background keyboard listener for 'q' to quit
    kb = KeyboardListener()
    kb.start()

    # Open camera or video source
    if video_path:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"ERROR: Could not open video file: {video_path}")
            sys.exit(1)
        is_video_source = True
    else:
        if is_pi:
            # On Raspberry Pi, use picamera2 for the CSI camera (IMX708).
            # cv2.VideoCapture(-1) fails because the CSI camera is managed
            # by libcamera, not exposed as a standard V4L2 device.
            print("[INFO] Detected Raspberry Pi — using picamera2 for CSI camera.")
            cap = _Picamera2Camera(resolution)
            print(f"[INFO] Camera configured: {resolution[0]}x{resolution[1]} @ ~30 fps")
        else:
            print(f"[INFO] Opening camera (index={camera_index})...")
            cap = cv2.VideoCapture(camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            if not cap.isOpened():
                print(
                    f"ERROR: Could not open camera index {camera_index}. "
                    f"Make sure the camera is connected and enabled."
                )
                sys.exit(1)
            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"[INFO] Camera resolution: {actual_w}x{actual_h}")
        is_video_source = False

    print("[INFO] Press 'q' to quit at any time...")
    viewer = PhaseViewer()

    try:
        while True:
            # Capture one frame
            ret, frame = cap.read()
            if not ret or frame is None:
                print("\n[WARN] Could not read frame.")
                if is_video_source:
                    break  # end of video file
                continue

            # Detect traffic light housing (bounding box)
            bbox = find_traffic_light_housing(frame)

            # Detect phase inside the bounding box
            result = detect_phase_from_bbox(frame, bbox)
            current_phase = result["phase"]  # 'off', 'green', 'yellow',
                                              # 'red', 'red_yellow',
                                              # 'no_detection'

            # Update terminal display (debounced, colored)
            viewer.update(current_phase)

            # Check if user pressed 'q'
            if kb.should_quit:
                print("\n[INFO] User pressed 'q' to quit.")
                break

            # Brief sleep to avoid CPU spinning during live camera mode
            if not is_video_source:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        kb.stop()
        cap.release()
        # Print a final newline (the viewer uses \\r, so cursor stays at
        # end of the last line — we need a newline to move to next line)
        print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """Parse arguments and launch the phase viewer."""
    parser = argparse.ArgumentParser(
        description="Terminal frontend for traffic light detection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Phase color coding:\n"
            "  GREEN  -> green text\n"
            "  YELLOW -> yellow text\n"
            "  RED    -> red text\n"
            "  RED+YELLOW -> \"RED\" in red + \"YELLOW\" in yellow\n"
            "  OFF    -> grey text\n"
            "\n"
            "Press 'q' to quit at any time.\n"
            "\n"
            "Examples:\n"
            "  # Live camera on Pi (auto-detect CSI):\n"
            "    python src/view_traffic_light.py\n"
            "\n"
            "  # Custom camera index:\n"
            "    python src/view_traffic_light.py --camera 0\n"
            "\n"
            "  # Process a recorded video file:\n"
            "    python src/view_traffic_light.py --video data/captured/my_run.mp4\n"
            "\n"
            "  # Custom resolution:\n"
            "    python src/view_traffic_light.py --resolution 800x600\n"
        ),
    )

    parser.add_argument(
        "--camera", "-c",
        type=int,
        default=-1,
        help=(
            "Camera device index. Only used on Windows/macOS. "
            "On Raspberry Pi, picamera2 auto-detects the CSI camera."
        ),
    )

    parser.add_argument(
        "--resolution", "-r",
        type=str,
        default=f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}",
        help=(
            f"Frame resolution in WxH format. Default: "
            f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}"
        ),
    )

    parser.add_argument(
        "--video", "-v",
        type=str,
        default=None,
        help="Process a video file instead of live camera.",
    )

    args = parser.parse_args()

    # Parse resolution string "WxH" -> (W, H)
    try:
        w, h = map(int, args.resolution.split("x"))
        resolution = (w, h)
    except ValueError:
        print(
            f"ERROR: Invalid resolution format: '{args.resolution}'. "
            f"Use WxH (e.g., '800x600')."
        )
        sys.exit(1)

    run_viewer(
        camera_index=args.camera,
        resolution=resolution,
        video_path=args.video,
    )


if __name__ == "__main__":
    main()
