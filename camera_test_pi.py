#!/usr/bin/env python3
"""
Camera Smoke Test - Raspberry Pi (Picamera2)
Tests the Pi Camera Module using the official Picamera2 API (libcamera-based).

Why Picamera2?
- Pi Camera Module 3 uses libcamera, not V4L2. OpenCV's cv2.VideoCapture
  cannot access it directly.
- Picamera2 is the official Raspberry Pi camera API — it gives numpy arrays
  that work perfectly with OpenCV.
- Runs headless (no display needed) — perfect for a train on tracks!

Usage on Pi:
    python3 camera_test_pi.py
"""

import cv2
import sys
import time
from pathlib import Path


def test_camera(preview_seconds=5):
    """Test the camera by capturing frames and saving a screenshot."""

    print("=" * 60)
    print("📷 Camera Smoke Test (Raspberry Pi - Picamera2)")
    print("=" * 60)

    # Step 1: Import and initialize Picamera2
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
    except ImportError:
        print("\n❌ ERROR: picamera2 is not installed!")
        print("   Install it on the Pi with:")
        print("   sudo apt install python3-picamera2")
        sys.exit(1)

    # Step 2: Get available sensor modes
    sensor_modes = picam2.sensor_modes
    print(f"\n📊 Available Sensor Modes:")
    for i, mode in enumerate(sensor_modes):
        print(f"   Mode {i}: {mode['size'][0]}x{mode['size'][1]} "
              f"@ {mode['fps']:.1f} fps")

    # Choose a fast mode for real-time track following
    target_width, target_height = 640, 480
    target_fps = 30.0

    print(f"\n🎯 Target mode: {target_width}x{target_height} @ {target_fps} fps")
    print(f"   (Optimized for speed — the train needs fast frames!)")

    # Step 3: Configure the camera for video capture
    # We configure a video stream for fast frame capture during the test
    config = picam2.create_video_configuration(
        main={"size": (target_width, target_height)},
    )
    picam2.configure(config)

    # Step 4: Start the camera
    try:
        picam2.start()
    except RuntimeError as e:
        print(f"\n❌ ERROR: Could not start camera!")
        print(f"   {e}")
        print("\n   Possible causes:")
        print("   1. Camera cable not connected firmly to CSI port")
        print("   2. Another program is using the camera — close it first")
        print("   3. Camera not detected — check 'rpicam-still --list-cameras'")
        sys.exit(1)

    print("✅ Camera started successfully!")

    # Step 5: Capture frames in a loop
    frame_count = 0
    start_time = time.time()
    output_path = Path("camera_test_screenshot.jpg")

    print(f"\n📸 Capturing for {preview_seconds} seconds...")
    print("-" * 60)

    while True:
        # Get the latest frame as a numpy array
        frame = picam2.capture_array()

        # Picamera2 returns BGRA (4 channels). OpenCV expects BGR (3 channels).
        # Strip the alpha channel to get clean BGR for OpenCV processing.
        if frame.shape[2] == 4:
            frame = frame[:, :, :3].copy()  # .copy() ensures contiguous memory
        else:
            frame = frame.copy()

        frame_count += 1

        # Add frame counter text overlay (using OpenCV)
        cv2.putText(
            frame,
            f"Frames: {frame_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        # Add countdown timer
        elapsed = time.time() - start_time
        remaining = max(0, preview_seconds - elapsed)
        cv2.putText(
            frame,
            f"Saving in {remaining:.1f}s",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2,
        )

        # Add FPS counter
        if elapsed > 0:
            current_fps = frame_count / elapsed
            cv2.putText(
                frame,
                f"FPS: {current_fps:.1f}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 150, 255),
                2,
            )

        # Save every 10th frame as preview (avoids filling disk)
        if frame_count % 10 == 0:
            preview_name = f"camera_test_preview_{frame_count:04d}.jpg"
            cv2.imwrite(preview_name, frame)

        # Auto-quit when timer expires
        if elapsed >= preview_seconds:
            break

    # Step 6: Save a final screenshot at high resolution
    print(f"\n✅ Captured {frame_count} frames total.")
    print(f"   Preview frames saved as camera_test_preview_*.jpg")

    # Capture a high-res still image using switch_mode_and_capture_array
    # This temporarily switches the camera to still mode and returns a numpy array
    still_config = picam2.create_still_configuration(main={"size": (2304, 1296)})
    still_frame = picam2.switch_mode_and_capture_array(still_config)
    picam2.stop()  # Return to stopped state

    # Strip alpha channel if present (convert BGRA -> BGR for OpenCV)
    if still_frame.shape[2] == 4:
        still_frame = still_frame[:, :, :3]
    cv2.imwrite(str(output_path), still_frame)
    print(f"📸 Screenshot saved to: {output_path.absolute()}")

    # Step 7: Calculate final stats
    total_time = time.time() - start_time
    actual_fps = frame_count / total_time if total_time > 0 else 0
    print("-" * 60)
    print(f"📊 Results:")
    print(f"   Total frames: {frame_count}")
    print(f"   Duration: {total_time:.1f}s")
    print(f"   Average FPS: {actual_fps:.1f}")
    print(f"   Frame size: {target_width}x{target_height}")
    print("-" * 60)

    # Step 8: Clean up
    picam2.stop()
    picam2.close()
    print("✅ Camera stopped. Test complete!")


if __name__ == "__main__":
    test_camera(preview_seconds=5)
