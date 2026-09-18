#!/usr/bin/env python3
"""
Data Collection Script - Train-Mounted Camera Capture (IMX708 / Picamera2)

Records per-frame JPEGs into an H.264 video file (via picamera2 native
recording), with sidecar metadata
(frames.csv, session_meta.json) for later annotation with LabelImg, CVAT,
Label Studio, or similar tools.

Designed to run remotely on the Raspberry Pi via SSH:
    ssh lev@levpi
    cd ~/lego-train
    python3 tools/data_collection/collect_data.py --duration 120 --run "inner curve, speed 40%"

After collection, retrieve from your dev machine:
    scp -r lev@levpi:~/lego-train/runs/* ./data/captured/raw/

Key design decisions:
- Locks AE/AWB/AF after auto-convergence to prevent defocus during capture.
- Uses picamera2 native H.264 recording (hardware-accelerated on Pi) — no silent codec failures.
- Writes per-frame JPEG (q=95) into a 'frames/' directory — frames stay independent.
- Muxes raw H.264 into MP4 via ffmpeg for VLC compatibility.
- Logs frame-level camera metadata for debugging.
- Never mode-switches: only ever captures from the runtime video config.
"""

import argparse
import csv
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Maximum safe duration to prevent runaway runs on the Pi
MAX_DURATION = 300  # 5 minutes

# ANSI escape for carriage-return line updates (works on Pi terminal)
_CR = "\033[1G\033[K"  # move to column 1, clear to end of line


def _signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global _shutdown_requested
    _shutdown_requested = True
    print("\n[collect_data] Shutdown requested (Ctrl+C). Finishing current frame...")


_shutdown_requested = False
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def _lock_camera_controls(picam2, max_exposure_us=6000, fps=30):
    """
    Let AE/AWB/AF converge on the current scene, then freeze them.

    On a moving train, autofocus hunting or auto-exposure drift will defocus
    or overexpose the traffic light at exactly the wrong moment.

    Parameters
    ----------
    picam2 : Picamera2
        Already-started camera instance.
    max_exposure_us : int
        Maximum exposure time in microseconds. Shorter exposure = less motion blur.

    Returns
    -------
    dict
        Locked control values for recording in session_meta.json.
    """
    from picamera2 import Picamera2
    from libcamera import controls

    print("[lock] Letting AE/AWB/AF converge for 5.0 s ...")
    time.sleep(5.0)
    md = picam2.capture_metadata()

    # Extract converged values
    # NOTE: libcamera ExposureTime is in NANOSECONDS, convert to microseconds
    exposure_ns = int(md.get("ExposureTime", 33333))
    exposure_us = exposure_ns // 1000

    # Clamp exposure to a reasonable range:
    # - Minimum 20000 us (20 ms) to ensure sufficient light for indoor scenes.
    #   The IMX708's AE can converge to very short exposures (e.g., 32µs)
    #   optimized for bright conditions; in indoor lighting this produces
    #   severely underexposed frames even at maximum gain.
    # - Maximum max_exposure_us to limit motion blur.
    MIN_EXPOSURE_US = 20000
    exposure_us = max(MIN_EXPOSURE_US, min(exposure_us, max_exposure_us))

    # Clamp analogue gain to ensure sufficient brightness.
    # The converged gain may be too low for indoor scenes when AE
    # relies on gain compensation; enforce a minimum of 4.0x.
    MIN_ANALOGUE_GAIN = 4.0
    analogue_gain = max(MIN_ANALOGUE_GAIN, float(md.get("AnalogueGain", 1.0)))
    colour_gains = md.get("ColourGains", (1.0, 1.0))
    lens_position = float(md.get("LensPosition", 0.0))

    # Compute dynamic frame duration limits based on the converged exposure.
    # Use 3x the exposure as minimum frame duration to leave headroom,
    # capped at the target frame period (1_000_000 / fps).
    target_frame_period = 1_000_000 // fps
    min_frame_us = max(exposure_us * 3, 33333)  # at least 30fps worth of headroom
    frame_duration = (min_frame_us, target_frame_period)

    print(f"[lock] Converged: exp={exposure_us}us gain={analogue_gain:.3f} "
          f"CWG={colour_gains[0]:.3f}/{colour_gains[1]:.3f} lens={lens_position:.4f}")
    print(f"[lock] FrameDurationLimits: {frame_duration}")

    # CRITICAL: All controls must be set in a SINGLE call.
    # If split across two calls, AE re-runs and overrides you.
    locked = {
        "AeEnable": False,
        "AwbEnable": False,
        "ExposureTime": exposure_us,
        "AnalogueGain": analogue_gain,
        "ColourGains": colour_gains,
        "AfMode": controls.AfModeEnum.Manual,
        "LensPosition": lens_position,
        "Brightness": 0.0,
        "Contrast": 1.0,
        "Saturation": 1.0,
        "Sharpness": 1.0,
        "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Fast,
        "FrameDurationLimits": frame_duration,  # dynamic, based on converged exposure
    }

    # Guard: disable HDR if available (not all libcamera builds support it)
    if "HdrMode" in picam2.camera_controls:
        locked["HdrMode"] = controls.HdrModeEnum.Off

    print(f"[lock] Applying {len(locked)} locked controls ...")
    picam2.set_controls(locked)

    # Discard first 10 frames -- controls take a few frames to fully apply
    for _ in range(10):
        picam2.capture_array()

    # Verify the lock actually held
    verify_md = picam2.capture_metadata()
    print("[lock] Verifying lock (next frame metadata):")
    print(f"       ExposureTime : {verify_md.get('ExposureTime', 'N/A')}")
    print(f"       AnalogueGain : {verify_md.get('AnalogueGain', 'N/A')}")
    print(f"       LensPosition : {verify_md.get('LensPosition', 'N/A')}")
    print("[lock] Camera locked. Proceeding to capture.\n")

    return locked


def _collect_with_picamera2(duration_s, resolution, fps, max_exposure_us,
                            output_dir, run_note):
    """Record data using Picamera2 (IMX708 / Pi Camera Module 3)."""
    import cv2
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder

    picam2 = Picamera2()
    cfg = picam2.create_video_configuration(
        main={"size": resolution, "format": "RGB888"}
    )
    picam2.configure(cfg)

    print("[camera] Starting Picamera2 ...")
    picam2.start()
    print(f"[camera] Configured: {resolution[0]}x{resolution[1]} @ {fps} fps")

    # Lock camera controls (AE/AWB/AF)
    locked_controls = _lock_camera_controls(picam2, max_exposure_us)

    # Write session metadata
    session_meta = {
        "backend": "picamera2",
        "controls": {k: str(v) for k, v in locked_controls.items()},
        "config": str(picam2.camera_configuration()),
        "run_note": run_note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resolution": list(resolution),
        "fps": fps,
        "max_exposure_us": max_exposure_us,
    }
    meta_path = output_dir / "session_meta.json"
    with open(meta_path, "w") as f:
        json.dump(session_meta, f, indent=2)
    print(f"[meta] session_meta.json -> {meta_path}")

    # Write run note
    note_path = output_dir / "run_note.txt"
    with open(note_path, "w") as f:
        f.write(run_note)
    print(f"[meta] run_note.txt -> {note_path}")

    # Use picamera2's native H.264 video recording (hardware-accelerated on Pi).
    # This avoids OpenCV's broken MJPEG codec entirely and produces a standard
    # H.264 elementary stream that we mux into MP4 after capture.
    #
    # How it works:
    #   1. Configure picamera2 with 'encode' = 'main' (already done above).
    #   2. Create an H264Encoder and start recording to a file.
    #   3. Continue capturing frames for per-frame JPEGs + metadata (unchanged).
    #   4. Stop recording when done.
    #   5. Mux the raw H.264 into a proper MP4 container
    #      using ffmpeg (runs on the Pi).
    h264_path = output_dir / "train.h264"
    mp4_path = output_dir / "train.mp4"

    # Create H.264 encoder (bitrate in bps) — ~3 Mbps is good for 640x480@30
    bitrate = 3_000_000
    h264_encoder = H264Encoder(bitrate)

    # Start recording — writes raw H.264 frames directly to file
    picam2.start_recording(h264_encoder, str(h264_path))
    print(f"[h264] Writing H.264 stream to {h264_path}")

    # Also keep per-frame JPEG directory for sidecar metadata
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    mjpeg_path = mp4_path  # alias for backward compat — returns .mp4 now

    # Open CSV sidecar
    csv_path = output_dir / "frames.csv"
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "frame_idx", "filename", "wall_timestamp", "sensor_timestamp",
        "exposure_us", "analogue_gain", "colour_gains_red",
        "colour_gains_blue", "lens_position", "duration_us",
    ])
    print(f"[csv] Sidecar -> {csv_path}")

    # Capture loop
    frame_idx = 0
    start_time = time.time()
    last_status = start_time
    lens_position_warnings = 0
    locked_lens = locked_controls['LensPosition']
    sep = '=' * 60

    print(f'\n{sep}')
    print(f'  Capturing for {duration_s} seconds ...')
    print(sep)

    try:
        while True:
            if _shutdown_requested:
                print('[collect] Shutdown requested - stopping capture.')
                break

            # Capture frame
            frame = picam2.capture_array()
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]

            # Capture metadata for this frame
            # NOTE: libcamera ExposureTime is in NANOSECONDS
            md = picam2.capture_metadata()
            exposure_ns = md.get('ExposureTime', 0)
            if isinstance(exposure_ns, int) and exposure_ns > 1_000_000:
                exposure_us = exposure_ns // 1000  # ns -> us
            else:
                exposure_us = int(exposure_ns)  # already in us

            analogue_gain = float(md.get('AnalogueGain', 0))
            colour_gains = md.get('ColourGains', (0.0, 0.0))
            lens_pos = float(md.get('LensPosition', 0.0))
            sensor_ts = md.get('SensorTimestamp', 0)
            frame_duration = int(md.get('FrameDuration', 0))

            # Warn if AF is still moving
            if abs(lens_pos - locked_lens) > 0.01:
                lens_position_warnings += 1
                if lens_position_warnings <= 10 or lens_position_warnings % 100 == 0:
                    print(f'[WARN] LensPosition drifted to {lens_pos:.4f} '
                          f'(was {locked_lens:.4f}). '
                          f'AF may not be fully locked! (count: {lens_position_warnings})')

            # Encode JPEG and write as individual frame file
            frame_path = frames_dir / f'frame_{frame_idx:06d}.jpg'
            cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

            # The H.264 video stream is handled automatically by picamera2's
            # start_video_stream() — frames are encoded and written to the file
            # by the camera's hardware encoder in the background. No manual
            # write() call needed.

            # Write CSV row
            wall_ts = datetime.now(timezone.utc).isoformat()
            csv_writer.writerow([
                frame_idx,
                f'frame_{frame_idx:06d}.jpg',
                wall_ts,
                int(sensor_ts),
                exposure_us,
                f'{analogue_gain:.4f}',
                f'{colour_gains[0]:.4f}',
                f'{colour_gains[1]:.4f}',
                f'{lens_pos:.6f}',
                frame_duration,
            ])

            # Status output every 1 second
            now = time.time()
            if now - last_status >= 1.0:
                elapsed = now - start_time
                fps_actual = frame_idx / elapsed if elapsed > 0 else 0
                file_size_mb = h264_path.stat().st_size / (1024 * 1024)
                extra = ''
                if lens_position_warnings > 0:
                    extra = f'  [lens drifts: {lens_position_warnings}]'
                status_line = (
                    f'  [{elapsed:6.1f}s / {duration_s}s] '
                    f'frames={frame_idx:6d}  '
                    f'fps={fps_actual:5.1f}  '
                    f'size={file_size_mb:7.1f} MB  '
                    f'exp={exposure_us:>5d}us  '
                    f'gain={analogue_gain:.2f}  '
                    f'lens={lens_pos:.4f}'
                )
                print(f'{_CR}{status_line}{extra}')
                last_status = now

            frame_idx += 1
            elapsed = time.time() - start_time
            if elapsed >= duration_s:
                break

    finally:
        print(f'\n[collect] Shutting down ...')
        csv_file.flush()
        csv_file.close()
        # Stop the H.264 recording — this flushes remaining frames to disk
        picam2.stop_recording()
        picam2.stop()

    # Mux raw H.264 into MP4 container using ffmpeg
    if h264_path.exists() and h264_path.stat().st_size > 0:
        print(f'[mux] Converting {h264_path.name} -> {mp4_path.name} via ffmpeg ...')
        import subprocess
        try:
            result = subprocess.run(
                [
                    'ffmpeg', '-y',
                    '-r', str(fps),
                    '-i', str(h264_path),
                    '-c:v', 'copy',
                    '-movflags', '+faststart',
                    str(mp4_path),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                mp4_size = mp4_path.stat().st_size / (1024 * 1024)
                print(f'[mux] MP4 created: {mp4_size:.1f} MB')
            else:
                print(f'[mux] ffmpeg warning: {result.stderr.strip()}')
                # Fallback: keep the raw .h264 file — most players still handle it
                mp4_path = None
        except FileNotFoundError:
            print('[mux] ffmpeg not found — keeping raw .h264 file (playable in VLC).')
            mp4_path = None
        except subprocess.TimeoutExpired:
            print('[mux] ffmpeg timed out — keeping raw .h264 file.')
            mp4_path = None

    # Final stats
    total_time = time.time() - start_time
    actual_fps = frame_idx / total_time if total_time > 0 else 0
    final_size = h264_path.stat().st_size / (1024 * 1024) if h264_path.exists() else 0
    frame_count = len(list(frames_dir.iterdir())) if frames_dir.exists() else 0
    frame_total_size = sum(f.stat().st_size for f in frames_dir.iterdir()) / (1024 * 1024) if frames_dir.exists() else 0

    # Validate H.264 output
    h264_ok = final_size > 0
    if not h264_ok:
        print("[WARN] H.264 file is empty - hardware encoding may have failed.")
        print("[WARN] Per-frame JPEG files in 'frames/' directory are the valid output.")

    print(f'\n{sep}')
    print(f'  Capture complete!')
    print(f'  Frames   : {frame_idx}')
    print(f'  Duration : {total_time:.1f}s')
    print(f'  Average  : {actual_fps:.1f} fps')
    print(f'  H.264 size: {final_size:.1f} MB')
    print(f'  Frame files: {frame_count} ({frame_total_size:.2f} MB)')
    print(f'  Lens drifts: {lens_position_warnings}')
    if mp4_path and mp4_path.exists():
        mp4_size = mp4_path.stat().st_size / (1024 * 1024)
        print(f'  Output (MP4): {mp4_path} ({mp4_size:.1f} MB)')
    else:
        print(f'  Output (H.264): {h264_path}')
    print(f'  Frames dir: {frames_dir}')
    print(sep + '\n')
    return mjpeg_path


def _collect_with_opencv(duration_s, resolution, fps, max_exposure_us,
                         output_dir, run_note):
    """Record data using OpenCV (USB webcam fallback)."""
    import cv2

    cap = cv2.VideoCapture(-1)
    if not cap.isOpened():
        print("[ERROR] Could not open USB webcam!")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    cap.set(cv2.CAP_PROP_FPS, fps)
    print(f"[camera] USB webcam: {resolution[0]}x{resolution[1]} @ {fps} fps")

    session_meta = {
        "backend": "opencv",
        "run_note": run_note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resolution": list(resolution),
        "fps": fps,
        "note": "USB webcam - no AE/AWB/AF locking available.",
    }
    meta_path = output_dir / "session_meta.json"
    with open(meta_path, "w") as f:
        json.dump(session_meta, f, indent=2)
    print(f"[meta] session_meta.json -> {meta_path}")

    note_path = output_dir / "run_note.txt"
    with open(note_path, "w") as f:
        f.write(run_note)
    print(f"[meta] run_note.txt -> {note_path}")

    mjpeg_path = output_dir / "train.mjpeg"
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(mjpeg_path), fourcc, fps, resolution)
    if not writer.isOpened():
        print("[ERROR] Could not open MJPEG writer!")
        cap.release()
        sys.exit(1)
    print(f"[mjpeg] Writing to {mjpeg_path}")

    csv_path = output_dir / "frames.csv"
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "frame_idx", "filename", "wall_timestamp", "sensor_timestamp",
        "exposure_us", "analogue_gain", "colour_gains_red",
        "colour_gains_blue", "lens_position", "duration_us",
    ])
    print(f"[csv] Sidecar -> {csv_path}")

    frame_idx = 0
    start_time = time.time()
    last_status = start_time
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  Capturing for {duration_s} seconds ...")
    print(sep)

    try:
        while True:
            if _shutdown_requested:
                print("[collect] Shutdown requested - stopping capture.")
                break

            ret, frame = cap.read()
            if not ret:
                print("[WARN] Failed to read frame, skipping.")
                continue

            wall_ts = datetime.now(timezone.utc).isoformat()

            # VideoWriter.write() expects a raw numpy array frame (BGR), not JPEG bytes.
            # Writing the raw frame directly avoids the black-frame corruption bug.
            writer.write(frame)

            csv_writer.writerow([
                frame_idx,
                f"frame_{frame_idx:06d}.jpg",
                wall_ts,
                0, 0, 0, 0, 0, 0, 0,
            ])

            now = time.time()
            if now - last_status >= 1.0:
                elapsed = now - start_time
                fps_actual = frame_idx / elapsed if elapsed > 0 else 0
                file_size_mb = mjpeg_path.stat().st_size / (1024 * 1024)
                status_line = (
                    f"  [{elapsed:6.1f}s / {duration_s}s] "
                    f"frames={frame_idx:6d}  "
                    f"fps={fps_actual:5.1f}  "
                    f"size={file_size_mb:7.1f} MB"
                )
                print(f"{_CR}{status_line}")
                last_status = now

            frame_idx += 1
            elapsed = time.time() - start_time
            if elapsed >= duration_s:
                break

    finally:
        print(f"\n[collect] Shutting down ...")
        csv_file.flush()
        csv_file.close()
        writer.release()
        cap.release()

    total_time = time.time() - start_time
    actual_fps = frame_idx / total_time if total_time > 0 else 0
    final_size = mjpeg_path.stat().st_size / (1024 * 1024)

    print(f"\n{sep}")
    print(f"  Capture complete!")
    print(f"  Frames   : {frame_idx}")
    print(f"  Duration : {total_time:.1f}s")
    print(f"  Average  : {actual_fps:.1f} fps")
    print(f"  File size: {final_size:.1f} MB")
    print(f"  Output   : {mjpeg_path}")
    print(sep + "\n")
    return mjpeg_path


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Data collection script for LEGO train camera.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--duration", "-d",
        type=int, default=60,
        help="Capture duration in seconds (default: 60, max: 300).",
    )
    parser.add_argument(
        "--resolution", "-r",
        type=str, default="640x480",
        help="Capture resolution as WxH (default: 640x480).",
    )
    parser.add_argument(
        "--fps", "-f",
        type=int, default=30,
        help="Target frame rate (default: 30).",
    )
    parser.add_argument(
        "--run", "-n",
        type=str, required=True,
        help="Run description/note (e.g. 'inner curve, speed 40%%').",
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str, default=None,
        help="Output directory (default: runs/YYYYMMDD_HHMMSS).",
    )
    parser.add_argument(
        "--max-exposure-us",
        type=int, default=6000,
        help="Max exposure time in microseconds (default: 6000).",
    )
    return parser.parse_args()


def main():
    """CLI entry point."""
    args = parse_args()

    # Validate duration
    duration = min(args.duration, MAX_DURATION)
    if duration < args.duration:
        print(f"[WARN] Duration capped at {MAX_DURATION}s (requested {args.duration}s).")

    # Parse resolution
    try:
        parts = args.resolution.split("x")
        if len(parts) != 2:
            raise ValueError
        resolution = (int(parts[0]), int(parts[1]))
    except ValueError:
        print(f"[ERROR] Invalid resolution format: {args.resolution}. Use WxH (e.g., 640x480).")
        sys.exit(1)

    # Create output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("runs") / ts
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[output] Collecting to: {output_dir.absolute()}")
    print()

    # Detect backend
    try:
        from picamera2 import Picamera2  # noqa: F401
        backend = "picamera2"
    except ImportError:
        backend = "opencv"

    if backend == "picamera2":
        print("[backend] Picamera2 (IMX708 camera module)")
        mjpeg_path = _collect_with_picamera2(
            duration_s=duration,
            resolution=resolution,
            fps=args.fps,
            max_exposure_us=args.max_exposure_us,
            output_dir=output_dir,
            run_note=args.run,
        )
    else:
        print("[backend] OpenCV (USB webcam fallback)")
        print("[WARN] No AE/AWB/AF locking available on USB webcam.")
        mjpeg_path = _collect_with_opencv(
            duration_s=duration,
            resolution=resolution,
            fps=args.fps,
            max_exposure_us=args.max_exposure_us,
            output_dir=output_dir,
            run_note=args.run,
        )

    print(f"\nDone! Video file: {mjpeg_path.absolute()}")
    print(f"Sidecars: {output_dir}/frames.csv, {output_dir}/session_meta.json, {output_dir}/run_note.txt")


if __name__ == "__main__":
    main()
