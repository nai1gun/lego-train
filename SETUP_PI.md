# Raspberry Pi Setup Guide

## Quick Start

```bash
# Connect to the Pi
ssh lev@levpi

# Run the camera test (uses Picamera2 — no venv needed!)
python3 camera_test_pi.py
```

## Virtual Environment on Pi

On Raspberry Pi OS Bookworm, **do NOT** create a plain venv — it won't see system-installed packages like `picamera2`, `libcamera`, and `opencv-python-headless`.

**Option A: Use system Python directly (recommended for the Pi)**
```bash
python3 camera_test_pi.py
```

**Option B: Create a venv that includes system packages**
```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 camera_test_pi.py
```

⚠️ **Never** use `pip install` without a venv on Bookworm — it will fail with "externally-managed-environment". Use `sudo apt install python3-*` instead.

## Camera Troubleshooting

### Camera not detected
```bash
rpicam-still --list-cameras
```
Should show: `0 : imx708`

### "Device or resource busy" error
Another program is using the camera. Close it first:
```bash
fuser /dev/video0  # shows PIDs using the camera
kill <PID>         # stop the process
```

### Picamera2 not found
```bash
sudo apt install python3-picamera2
```

## Picamera2 + OpenCV Notes

- `picam2.capture_array()` returns a **numpy array** — ready for OpenCV!
- The array is BGRA (4 channels). Strip the alpha for OpenCV: `frame = frame[:, :, :3]`
- Picamera2 returns **BGR byte order** despite the naming — exactly what OpenCV expects
- Camera test uses 640×480 for speed (not megapixels — the train needs fast frames!)

## Available Sensor Modes (IMX708)

| Resolution | FPS | Notes |
|-----------|-----|-------|
| 1536×864 | 120 | Fastest — good for high-speed tracking |
| 2304×1296 | 56 | Binned mode — great balance |
| 4608×2592 | 14.4 | Full sensor — only for photos |

We use **640×480** (scaled from the sensor) for real-time processing.