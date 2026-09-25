#!/usr/bin/env python3
"""
Camera Smoke Test (Auto Mode)
Tests the camera by capturing frames and saving a screenshot.

Auto-detects hardware:
- Raspberry Pi (picamera2 available) -> uses Picamera2 API
- Windows / other -> uses OpenCV cv2.VideoCapture (USB webcam)

Usage:
    python scripts/camera_smoke_test.py              # default 5s preview
    python scripts/camera_smoke_test.py --seconds 10  # custom preview time
"""

import argparse
import cv2
import sys
import time
from pathlib import Path


def _draw_text(frame, text, position, color):
    """Draw text on a frame with a semi-transparent background."""
    cv2.putText(
        frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2,
    )


def _ensure_debug_out() -> Path:
    """Create and return the debug_out directory (relative to project root)."""
    output_dir = Path("debug_out")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _capture_with_picamera2(preview_seconds: int) -> Path:
    """Capture frames using Picamera2 (Pi Camera Module 3)."""
    try:
        from picamera2 import Picamera2
    except ImportError:
        print("\nERROR: picamera2 is not installed!")
        print("   Install on the Pi with: sudo apt install python3-picamera2")
        sys.exit(1)

    picam2 = Picamera2()
    sensor_modes = picam2.sensor_modes

    print("\nAvailable Sensor Modes:")
    for i, mode in enumerate(sensor_modes):
        print(f"   Mode {i}: {mode['size'][0]}x{mode['size'][1]} @ {mode['fps']:.1f} fps")

    target_width, target_height = 640, 480
    target_fps = 30.0
    print(f"\nTarget mode: {target_width}x{target_height} @ {target_fps} fps")

    config = picam2.create_video_configuration(main={"size": (target_width, target_height)})
    picam2.configure(config)

    try:
        picam2.start()
    except RuntimeError as e:
        print(f"\nERROR: Could not start camera!")
        print(f"   {e}")
        sys.exit(1)

    print("Camera started successfully!")
    frame_count = 0
    start_time = time.time()
    output_dir = _ensure_debug_out()
    output_path = output_dir / "camera_test_screenshot.jpg"

    print(f"\nCapturing for {preview_seconds} seconds...")
    print("-" * 60)

    while True:
        frame = picam2.capture_array()
        if frame.shape[2] == 4:
            frame = frame[:, :, :3].copy()
        else:
            frame = frame.copy()

        # Picamera2 returns RGB; OpenCV expects BGR — convert before saving
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        frame_count += 1
        _draw_text(frame, f"Frames: {frame_count}", (10, 30), (0, 255, 0))

        elapsed = time.time() - start_time
        remaining = max(0, preview_seconds - elapsed)
        _draw_text(frame, f"Saving in {remaining:.1f}s", (10, 60), (255, 255, 0))

        if elapsed > 0:
            current_fps = frame_count / elapsed
            _draw_text(frame, f"FPS: {current_fps:.1f}", (10, 90), (0, 150, 255))

        if frame_count % 10 == 0:
            preview_name = output_dir / f"camera_test_preview_{frame_count:04d}.jpg"
            cv2.imwrite(str(preview_name), frame)

        if elapsed >= preview_seconds:
            break

    print(f"\nCaptured {frame_count} frames total.")
    print(f"   Preview frames saved in {output_dir}/")

    still_config = picam2.create_still_configuration(main={"size": (2304, 1296)})
    still_frame = picam2.switch_mode_and_capture_array(still_config)
    picam2.stop()

    if still_frame.shape[2] == 4:
        still_frame = still_frame[:, :, :3]
    # Picamera2 returns RGB; OpenCV expects BGR — convert before saving
    still_frame = cv2.cvtColor(still_frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(output_path), still_frame)
    print(f"Screenshot saved to: {output_path.absolute()}")

    total_time = time.time() - start_time
    actual_fps = frame_count / total_time if total_time > 0 else 0
    print("-" * 60)
    print("Results:")
    print(f"   Total frames: {frame_count}")
    print(f"   Duration: {total_time:.1f}s")
    print(f"   Average FPS: {actual_fps:.1f}")
    print(f"   Frame size: {target_width}x{target_height}")
    print("-" * 60)

    return output_path

def _capture_with_opencv(preview_seconds: int) -> Path:
    """Capture frames using OpenCV's cv2.VideoCapture (USB webcam)."""
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not open camera!")
        print("   Please check that the camera is properly connected.")
        sys.exit(1)

    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = camera.get(cv2.CAP_PROP_FPS)

    print(f"Camera opened successfully!")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps:.1f}")
    print("-" * 60)
    print("Press 'q' to quit and save a screenshot.")
    print("-" * 60)

    frame_count = 0
    output_dir = _ensure_debug_out()
    output_path = output_dir / "camera_test_screenshot.jpg"
    start_time = time.time()

    print(f"Auto mode: Previewing for {preview_seconds} seconds...")
    print("-" * 60)

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Failed to capture frame!")
            break

        frame_count += 1
        _draw_text(frame, f"Frames: {frame_count}", (10, 30), (0, 255, 0))

        elapsed = time.time() - start_time
        remaining = max(0, preview_seconds - elapsed)
        _draw_text(frame, f"Saving in {remaining:.1f}s", (10, 60), (255, 255, 0))

        cv2.imshow("Camera Test", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("\nUser pressed 'q' to quit early.")
            break

        if elapsed >= preview_seconds:
            print(f"\nCaptured {frame_count} frames total.")
            break

    ret, save_frame = camera.read()
    if ret:
        cv2.imwrite(str(output_path), save_frame)
        print(f"Screenshot saved to: {output_path.absolute()}")
    else:
        print("Could not save screenshot.")

    camera.release()
    cv2.destroyAllWindows()

    print("-" * 60)
    print("Camera test complete!")
    print("-" * 60)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Camera smoke test (auto-detects hardware)")
    parser.add_argument(
        "--seconds", type=int, default=5, help="Preview duration in seconds (default: 5)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Camera Smoke Test")
    print("=" * 60)

    # Auto-detect hardware backend
    try:
        from picamera2 import Picamera2  # noqa: F401
        backend = "picamera2"
    except ImportError:
        backend = "opencv"

    if backend == "picamera2":
        print("\nDetected: Raspberry Pi (using Picamera2)")
        output_path = _capture_with_picamera2(args.seconds)
    else:
        print("\nDetected: USB webcam (using OpenCV cv2.VideoCapture)")
        output_path = _capture_with_opencv(args.seconds)

    print(f"\nDone! Output: {output_path.absolute()}")


if __name__ == "__main__":
    main()
