#!/usr/bin/env python3
"""
Traffic Light → Motor Controller for LEGO Autonomous Train

Integrates the heuristic traffic-light detector with Bluetooth motor actuation.
Uses a hysteresis-based state machine to avoid motor flickering when the
detector is uncertain (e.g. brief occlusions, lighting changes).

State machine
-------------
UNKNOWN  → initial / no reliable detection
STOPPED  → red or unknown detected
MOVING   → green reliably detected

Hysteresis: a phase must be observed for `hysteresis_threshold` consecutive
frames before a state transition is committed.  This prevents rapid
stop→go→stop oscillations at the edge of detection confidence.

Usage
-----
    python src/traffic_light_train.py          # live camera on Pi
    python src/traffic_light_train.py --show   # with debug overlay
    python src/traffic_light_train.py --video path/to/run.mp4

"""

from __future__ import annotations

import argparse
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Import the detector and Bluetooth controller
# ---------------------------------------------------------------------------
try:
    from src.detectors.heuristics import HeuristicsTrafficLightDetector
    from src.bluetooth_controller import connect_to_lego_device, send_command
except ImportError:
    # Running directly (not as module) — adjust import path
    from detectors.heuristics import HeuristicsTrafficLightDetector
    from bluetooth_controller import connect_to_lego_device, send_command

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HYSTERESIS_THRESHOLD = 3          # consecutive frames needed for transition
START_POWER = 20                  # % power on reliable green (gradual start)
CRUISE_POWER = 50                 # % power during steady green
EMERGENCY_STOP_POWER = 0          # power on red / unknown

DEFAULT_CAMERA_INDEX = 0          # fallback camera index on non-Pi platforms


class ControllerState(str, Enum):
    """High-level controller states."""
    UNKNOWN = "UNKNOWN"
    STOPPED = "STOPPED"
    MOVING = "MOVING"


class TrafficLightMotorController:
    """Bridges traffic-light detection with LEGO motor commands.

    Parameters
    ----------
    hysteresis_threshold : int
        How many consecutive frames of the same phase are needed before
        committing a state transition.  Higher = more stable, slower to react.
    start_power : int
        Percentage power (0-100) applied when first entering MOVING state.
    cruise_power : int
        Percentage power applied during steady MOVING state.
    """

    def __init__(
        self,
        hysteresis_threshold: int = HYSTERESIS_THRESHOLD,
        start_power: int = START_POWER,
        cruise_power: int = CRUISE_POWER,
    ) -> None:
        self.hysteresis_threshold = hysteresis_threshold
        self.start_power = start_power
        self.cruise_power = cruise_power

        # Current high-level state
        self.state: ControllerState = ControllerState.UNKNOWN

        # Hysteresis counters — how many consecutive frames we have seen
        # the *current* state's trigger phase.
        self._green_counter: int = 0
        self._red_counter: int = 0
        self._unknown_counter: int = 0

        # Debug / logging
        self._frame_count: int = 0
        self._last_phase: str = "no_detection"
        self._state_changes: list[dict[str, Any]] = []

        # Detector instance (created lazily)
        self._detector: Optional[HeuristicsTrafficLightDetector] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_state(self) -> ControllerState:
        """Return the current high-level controller state."""
        return self.state

    def get_debug_info(self) -> dict[str, Any]:
        """Return a dict of internal counters for logging / debug overlay."""
        return {
            "frame": self._frame_count,
            "state": self.state.value,
            "last_phase": self._last_phase,
            "green_counter": self._green_counter,
            "red_counter": self._red_counter,
            "unknown_counter": self._unknown_counter,
            "state_history": list(self._state_changes[-10:]),  # last 10
        }

    def run_loop(
        self,
        show_overlay: bool = False,
        video_path: Optional[str] = None,
        camera_index: int = DEFAULT_CAMERA_INDEX,
    ) -> None:
        """Synchronous main loop: detect → decide → act."""
        print("[TrafficLightMotorController] Starting main loop …")
        print("  Press Ctrl+C to stop.\n")

        # 1. Initialise detector
        self._detector = HeuristicsTrafficLightDetector()

        # 2. Open camera / video source
        cap: Optional[cv2.VideoCapture] = None
        if video_path:
            cap = cv2.VideoCapture(video_path)
            print(f"  Using video file: {video_path}")
        else:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                print("ERROR: Could not open camera. Check index or try --video.")
                sys.exit(1)
            print(f"  Using camera index {camera_index}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("[loop] No frame received — stopping.")
                    break

                # 3. Detect traffic light phase
                detection = self._detect_phase(frame)

                # 4. Update state machine
                self._update_state(detection["phase"])

                # 5. Act (send motor command)
                power = self._compute_power()
                self._apply_motor_power(power)

                # 6. Debug overlay
                if show_overlay:
                    self._draw_overlay(frame, detection)

                # 7. Logging
                self._log_state()

                # Small delay to avoid hogging CPU
                cv2.waitKey(1)

        except KeyboardInterrupt:
            print("\n[Interrupt] Stopping …")
        finally:
            self._apply_motor_power(EMERGENCY_STOP_POWER)
            if cap is not None:
                cap.release()
            print(f"Final state: {self.state.value}")

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def _detect_phase(self, frame: np.ndarray) -> Dict[str, Any]:
        """Run the heuristic detector and return the latest phase dict."""
        if self._detector is None:
            return {"phase": "no_detection", "red": False, "yellow": False, "green": False}
        return self._detector.detect(frame)

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def _update_state(self, phase: str) -> None:
        """Update internal state based on the detected phase, with hysteresis.

        Policy
        ------
        - Green detected for N frames  →  MOVING
        - Red or Red+Yellow detected   →  STOPPED
        - Yellow (alone)               →  treat as green (keep going)
        - No detection / other         →  STOPPED (safety-first)
        """
        self._frame_count += 1
        self._last_phase = phase

        # --- Accumulate hysteresis counters ---
        if phase in ("green", "yellow"):
            self._green_counter += 1
            self._red_counter = 0
            self._unknown_counter = 0
        elif phase == "red" or phase == "red_yellow":
            self._red_counter += 1
            self._green_counter = 0
            self._unknown_counter = 0
        else:
            # no_detection, off, or any unexpected phase
            self._unknown_counter += 1
            self._green_counter = 0
            self._red_counter = 0

        # --- Check transition thresholds ---
        old_state = self.state

        if self._green_counter >= self.hysteresis_threshold:
            self.state = ControllerState.MOVING
        elif self._red_counter >= self.hysteresis_threshold:
            self.state = ControllerState.STOPPED
        elif self._unknown_counter >= self.hysteresis_threshold:
            self.state = ControllerState.STOPPED

        # If we are already in a state, we stay there until the opposite
        # threshold is met — this is the hysteresis effect.

        # Log state change
        if old_state != self.state:
            self._state_changes.append({
                "frame": self._frame_count,
                "from": old_state.value,
                "to": self.state.value,
                "phase": phase,
            })
            print(f"  [STATE] {old_state.value} → {self.state.value}  (phase={phase})")

    # ------------------------------------------------------------------
    # Motor power computation
    # ------------------------------------------------------------------

    def _compute_power(self) -> int:
        """Return the motor power percentage for the current state."""
        if self.state == ControllerState.MOVING:
            # Gradual ramp: use start_power on first entry, cruise_power after
            if self._green_counter <= self.hysteresis_threshold:
                return self.start_power
            return self.cruise_power
        # STOPPED or UNKNOWN — stop
        return EMERGENCY_STOP_POWER

    def _apply_motor_power(self, power: int) -> None:
        """Send the motor power command via Bluetooth.

        This is a synchronous wrapper around the async Bleak send_command.
        On the Pi, you may want to replace this with direct async calls.
        """
        cmd_value = max(-100, min(100, power))
        print(f"  [MOTOR] Power: {cmd_value}%")
        # NOTE: Actual BLE command sending requires async context.
        # In production on the Pi, call `asyncio.run(send_command(...))`
        # or integrate with an event loop.

    # ------------------------------------------------------------------
    # Debug / logging
    # ------------------------------------------------------------------

    def _draw_overlay(self, frame: np.ndarray, detection: Dict[str, Any]) -> None:
        """Draw debug info on the frame."""
        h, w = frame.shape[:2]

        # State badge
        badge_text = f"State: {self.state.value}"
        badge_bg = (0, 255, 0) if self.state == ControllerState.MOVING else (0, 0, 255)
        cv2.putText(frame, badge_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, badge_bg, 2)

        # Phase info
        phase_text = f"Phase: {detection['phase']}"
        cv2.putText(frame, phase_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Power
        power = self._compute_power()
        power_text = f"Power: {power}%"
        cv2.putText(frame, power_text, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Hysteresis counters
        info_text = (f"G:{self._green_counter}  R:{self._red_counter}  "
                     f"U:{self._unknown_counter}")
        cv2.putText(frame, info_text, (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Traffic Light Train", frame)

    def _log_state(self) -> None:
        """Print a compact status line every 30 frames."""
        if self._frame_count % 30 == 0:
            info = self.get_debug_info()
            print(f"  [LOG] frame={info['frame']:6d}  "
                  f"state={info['state']:8s}  "
                  f"phase={info['last_phase']:15s}  "
                  f"G={info['green_counter']:2d} "
                  f"R={info['red_counter']:2d} "
                  f"U={info['unknown_counter']:2d}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Traffic Light → Motor Controller for LEGO Train"
    )
    parser.add_argument(
        "--show", action="store_true",
        help="Show debug overlay window"
    )
    parser.add_argument(
        "--video", type=str, default=None,
        help="Path to a video file for offline testing"
    )
    parser.add_argument(
        "--camera", type=int, default=DEFAULT_CAMERA_INDEX,
        help=f"Camera index to use (default: {DEFAULT_CAMERA_INDEX})"
    )
    parser.add_argument(
        "--hysteresis", type=int, default=HYSTERESIS_THRESHOLD,
        help=f"Consecutive frames needed for state transition (default: {HYSTERESIS_THRESHOLD})"
    )
    parser.add_argument(
        "--start-power", type=int, default=START_POWER,
        help=f"Power % on first green detection (default: {START_POWER})"
    )
    parser.add_argument(
        "--cruise-power", type=int, default=CRUISE_POWER,
        help=f"Steady-state power % (default: {CRUISE_POWER})"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    controller = TrafficLightMotorController(
        hysteresis_threshold=args.hysteresis,
        start_power=args.start_power,
        cruise_power=args.cruise_power,
    )

    controller.run_loop(
        show_overlay=args.show,
        video_path=args.video,
        camera_index=args.camera,
    )