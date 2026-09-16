#!/usr/bin/env python3
"""Compare brightness across ALL test runs."""
import cv2, glob, numpy as np, os, sys

runs = sorted(glob.glob("runs/20260916_*/"))
notes = {
    "runs/20260916_180914/": "test_fix_v4 (local)",
    "runs/20260916_181053/": "baseline",
    "runs/20260916_194155/": "AE_converged_test",
    "runs/20260916_194352/": "test_fix_v4 (remote)",
    "runs/20260916_201220/": "black_frame_final_test (6000us)",
    "runs/20260916_202405/": "high_exposure_test (60k)",
    "runs/20260916_202913/": "FIXED: min_exp=20ms min_gain=4",
}

print(f"{'Run':<35} {'Frames':>6} {'Size':>8} {'Mean':>7} {'Min':>7} {'Max':>7}")
print("-" * 80)

for run in runs:
    frames = sorted(glob.glob(f"{run}frames/*.jpg"))
    if not frames:
        print(f"{run:<35} NO FRAMES")
        continue
    means = [cv2.imread(f, cv2.IMREAD_COLOR).mean() for f in frames[:50]]
    sizes = [os.path.getsize(f) for f in frames]
    note = notes.get(run, "")
    print(f"{run:<35} {len(frames):>6} {sum(sizes)/1024/1024:>7.1f}MB {np.mean(means):>7.1f} {np.min(means):>7.1f} {np.max(means):>7.1f}  {note}")


