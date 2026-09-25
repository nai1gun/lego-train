#!/usr/bin/env python3
"""
Run the camera smoke test on the Pi and copy results back to this PC.

Usage:
    python scripts/run_camera_test_on_pi.py

Requires:
    - SSH access to the Pi (ssh lev@levpi)
    - scp available on this machine
    - The Pi must have camera_smoke_test.py at /home/lev/lego-train/scripts/
"""

import subprocess
import sys
from pathlib import Path

# Colors for terminal output (ANSI escape codes — work on Windows 10+, macOS, Linux)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{code}{text}{RESET}"


def run_command(cmd, label: str) -> subprocess.CompletedProcess:
    """Run a shell command and print its output."""
    print(color(f"\n=== {label} ===", CYAN))
    print(f"  Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(color(f"  Command returned exit code {result.returncode}", YELLOW))
    return result


def main():
    # Resolve paths relative to this script's location
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir.parent / "debug_out"

    # Step 1: Run the camera test on the Pi
    ssh_cmd = [
        "ssh", "lev@levpi",
        "cd /home/lev/lego-train && rm -f camera_test_preview_*.jpg camera_test_screenshot.jpg && python3 scripts/camera_smoke_test.py",
    ]
    run_command(ssh_cmd, "Running camera test on Pi")

    # Step 2: Create local output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: Copy the high-res screenshot
    scp_cmd1 = ["scp", "lev@levpi:/home/lev/lego-train/camera_test_screenshot.jpg", str(output_dir)]
    run_command(scp_cmd1, "Copying screenshot")

    # Step 4: Copy preview frames (glob pattern)
    scp_cmd2 = ["scp", "lev@levpi:/home/lev/lego-train/camera_test_preview_*.jpg", str(output_dir)]
    run_command(scp_cmd2, "Copying preview frames")

    # Step 5: Report results
    screenshot = output_dir / "camera_test_screenshot.jpg"
    preview_files = list(output_dir.glob("camera_test_preview_*.jpg"))

    print(color(f"\n=== Done! ===", GREEN))
    print(f"  Screenshot: {color(str(screenshot), GREEN)}")
    print(f"  Preview frames: {color(str(len(preview_files)), GREEN)} copied to {color(str(output_dir), GREEN)}")
    print(f"\n  Open the images in {output_dir}")


if __name__ == "__main__":
    main()