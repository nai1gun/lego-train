#!/usr/bin/env python3
"""Short-output end-to-end check: housing localization AND phase.

Runs the full detection (scripts/benchmark_traffic_light.run_detection_on_image,
i.e. housing detection -> lamp decisions) on every labeled frame of both
datasets and prints one summary line per dataset:
  n          labeled frames (all, incl. frames without a GT box)
  loc@0.5    % of GT-box frames with IoU >= 0.5
  meanIoU    mean IoU over GT-box frames
  center     % of GT-box frames whose predicted box center is inside the GT box
  w/h        median predicted/GT width and height ratios (1.00 = right size)
  phase      % of frames where the set of lit lamps exactly matches the label
  lamps      % of individual lamp decisions (3 per frame) that are correct
Add --frames to also print one line per frame.

Usage: python scripts/eval_housing.py [--frames]
"""
import faulthandler
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
import benchmark_traffic_light as B  # noqa: E402

RUNS = {"dynamic": "20260917_065933", "static": "20260925_182442"}
LAMPS = ("red", "yellow", "green")


def main():
    # Normal run takes a few seconds. If detector code hangs (e.g. infinite loop),
    # abort after 60 s and print where it is stuck instead of hanging silently.
    faulthandler.dump_traceback_later(60, exit=True)
    per_frame = "--frames" in sys.argv
    for name, run in RUNS.items():
        d = ROOT / "data/labeled/LEGO-Train-Traffic-Lights" / run
        ious, hits, rw, rh = [], [], [], []
        phase_ok, lamp_ok = [], []
        for f in sorted(p for p in (d / "frames").iterdir() if p.is_file() and not p.name.endswith(".jpg")):
            a = B.load_annotation(f)
            if not a:
                continue
            res = B.run_detection_on_image(d / "frames" / a["image_filename"])
            p, g = res["housing_bbox"], a["bbox_px"]
            lit = res.get("detected_lamps") or {}
            pred_set = {k for k in LAMPS if lit.get(k)}
            gt_set = a["gt_phases"]
            phase_ok.append(pred_set == gt_set)
            lamp_ok.extend((k in pred_set) == (k in gt_set) for k in LAMPS)
            iou, hit = 0.0, False
            if g:
                iou = B.compute_iou(g, p) if p else 0.0
                if p:
                    cx, cy = p[0] + p[2] / 2, p[1] + p[3] / 2
                    hit = g[0] <= cx <= g[0] + g[2] and g[1] <= cy <= g[1] + g[3]
                    if hit:
                        rw.append(p[2] / g[2])
                        rh.append(p[3] / g[3])
                ious.append(iou)
                hits.append(hit)
            if per_frame:
                gbox = tuple(int(v) for v in g) if g else None
                print(f"  {name} {a['frame_idx']:4d} iou={iou:.2f} center_in_gt={int(hit)} "
                      f"gt_lamps={sorted(gt_set)} pred_lamps={sorted(pred_set)} pred={p} gt={gbox}")
        ious = np.array(ious)
        print(f"{name:8s} n={len(phase_ok):3d} loc@0.5={100 * (ious >= 0.5).mean():5.1f}% meanIoU={ious.mean():.3f} "
              f"center={100 * np.mean(hits):5.1f}% "
              f"w/h={np.median(rw) if rw else 0:.2f}/{np.median(rh) if rh else 0:.2f} "
              f"phase={100 * np.mean(phase_ok):5.1f}% lamps={100 * np.mean(lamp_ok):5.1f}%")


if __name__ == "__main__":
    main()
