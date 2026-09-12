#!/usr/bin/env python3
"""
Camera Smoke Test (Auto Mode) - Raspberry Pi Compatible
This script tests the Pi Camera Module by capturing frames and verifying
the camera is working correctly.

How it works:
1. Opens the default camera (index 0) using libcamera backend if available
2. Displays a live preview window for 5 seconds with countdown
3. Automatically saves a screenshot
4. Reports camera properties (resolution, FPS)

For Lev: This is our first step to make the train "see" the track!
"""

import cv2
import sys
import time
from pathlib import Path


def test_camera(preview_seconds=5):
    """Test the camera by capturing frames and saving a screenshot."""
    
    print("=" * 60)
    print("📷 Camera Smoke Test (Raspberry Pi)")
    print("=" * 60)
    
    # Try to open the camera with auto-detect backend
    print("Opening camera with auto-detect backend...")
    camera = cv2.VideoCapture(0)
    
    # Verify the camera opened successfully
    if not camera.isOpened():
        print("\n❌ ERROR: Could not open camera!")
        print("   Possible solutions:")
        print("   1. Check camera cable connection to CSI port")
        print("   2. Run: sudo raspi-config → Interface Options → Camera")
        print("   3. Reboot the Raspberry Pi")
        sys.exit(1)
    
    print("✅ Successfully opened camera!")
    
    # Read camera properties (resolution, FPS)
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = camera.get(cv2.CAP_PROP_FPS)
    
    print(f"\n📊 Camera Properties:")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps:.1f}")
    print("-" * 60)
    print(f"Auto mode: Previewing for {preview_seconds} seconds...")
    print("-" * 60)
    
    # Start the live preview loop
    frame_count = 0
    output_path = Path("camera_test_screenshot.jpg")
    start_time = time.time()
    
    while True:
        # Capture a frame from the camera
        ret, frame = camera.read()
        
        # Check if frame was captured successfully
        if not ret:
            print("⚠️ Failed to capture frame, retrying...")
            time.sleep(0.1)
            continue
        
        frame_count += 1
        
        # Add frame counter text to the image
        # This helps us verify the camera is live
        cv2.putText(
            frame,
            f"Frames: {frame_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),  # Green text
            2  # Line thickness
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
            (255, 255, 0),  # Yellow text
            2
        )
        
        # Display the live preview window
        cv2.imshow("Camera Test", frame)
        
        # Auto-quit when timer expires
        if elapsed >= preview_seconds:
            print(f"\n✅ Captured {frame_count} frames total.")
            break
        
        # Small delay to prevent high CPU usage
        time.sleep(0.01)
    
    # Save a screenshot for verification
    ret, save_frame = camera.read()
    if ret:
        cv2.imwrite(str(output_path), save_frame)
        print(f"📸 Screenshot saved to: {output_path.absolute()}")
    else:
        print("⚠️ Could not save screenshot.")
    
    # Clean up resources
    camera.release()
    cv2.destroyAllWindows()
    
    print("=" * 60)
    print("✅ Camera test complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Run in auto mode (no manual input needed)
    test_camera(preview_seconds=5)
