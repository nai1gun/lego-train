#!/usr/bin/env python3
"""Quick test to find the right exposure value for indoor lighting."""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_video_configuration(main={'format': 'RGB888', 'size': (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(5.0)  # Let AE converge

# Test with AE locked values (what the current code does)
print("Simulating current code: AE converges, then we lock with gain=1.0:")
md = picam2.capture_metadata()
exp_ns = md.get("ExposureTime", 33333)
exp_us = exp_ns // 1000
gain = md.get("AnalogueGain", 1.0)
print(f"  AE converged: exp={exp_us}us  gain={gain:.2f}")

# Now lock at AE values but with gain clamped to 1.0
picam2.set_controls({
    'ExposureTime': exp_us,
    'AnalogueGain': 1.0,
    'AeEnable': False,
    'AwbEnable': False
})
time.sleep(0.5)
frame = picam2.capture_array()
print(f"  Locked (gain=1.0): frame_mean={frame.mean():.1f}")

# Test with higher gain (what AE was using)
picam2.set_controls({
    'ExposureTime': exp_us,
    'AnalogueGain': gain,
    'AeEnable': False,
    'AwbEnable': False
})
time.sleep(0.5)
frame = picam2.capture_array()
print(f"  Locked (gain={gain:.2f}): frame_mean={frame.mean():.1f}")

# Test with forced higher exposure and max gain
picam2.set_controls({
    'ExposureTime': 40000,
    'AnalogueGain': 16.0,
    'AeEnable': False,
    'AwbEnable': False
})
time.sleep(0.5)
frame = picam2.capture_array()
print(f"  Forced (exp=40000us, gain=16.0): frame_mean={frame.mean():.1f}")

# Test the sweet spot: higher exposure + moderate gain
for exp_us in [20000, 30000, 40000, 50000]:
    for g in [4.0, 8.0, 16.0]:
        picam2.set_controls({
            'ExposureTime': exp_us,
            'AnalogueGain': g,
            'AeEnable': False,
            'AwbEnable': False
        })
        time.sleep(0.3)
        frame = picam2.capture_array()
        print(f"  exp={exp_us:>5d}us, gain={g:>4.1f} -> mean={frame.mean():>6.1f}")

picam2.stop()
print("\nDone.")
