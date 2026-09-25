#!/usr/bin/env python3
"""Benchmark traffic light detection against labeled dataset."""

import argparse
from datetime import datetime
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
PROJECT_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from detect_traffic_light import (
    find_traffic_light_housing,
    _detect_lamps_lit,
    _compute_phase_from_lamps,
    LAMP_Y_FRACTIONS,
    LAMP_RADIUS_FRACTION,
)


# ============================================================================
# GIT COMMIT HELPER
# ============================================================================


def _get_git_commit() -> str:
    """Get the current git commit hash (short form), or 'unknown' if not in a git repo."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:12]  # short hash
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return "unknown"


# ============================================================================
# I/O HELPERS
# ============================================================================


def load_annotation(annotation_path: Path) -> Optional[Dict[str, Any]]:
    """Load a Label Studio annotation JSON file (no extension, named by ID)."""
    try:
        with open(annotation_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] Could not load annotation {annotation_path}: {e}")
        return None

    results = data.get("result", [])

    # Find bbox result (rectanglelabels type) and phase result (choices type)
    bbox_value = None
    choices_value = None
    original_width = 640
    original_height = 480

    for r in results:
        rtype = r.get("type", "")
        rvalue = r.get("value", {})
        if rtype == "rectanglelabels":
            bbox_value = rvalue
            original_width = r.get("original_width", 640)
            original_height = r.get("original_height", 480)
        elif rtype == "choices":
            choices_value = rvalue.get("choices", [])

    # Extract bbox coordinates (Label Studio stores as percentages 0-100)
    if bbox_value:
        x_pct = bbox_value.get("x", 0)
        y_pct = bbox_value.get("y", 0)
        w_pct = bbox_value.get("width", 0)
        h_pct = bbox_value.get("height", 0)

        # Convert percentages to pixel coordinates
        x_px = x_pct * original_width / 100.0
        y_px = y_pct * original_height / 100.0
        w_px = w_pct * original_width / 100.0
        h_px = h_pct * original_height / 100.0

        if w_px > 0 and h_px > 0:
            bbox_px = (x_px, y_px, w_px, h_px)
        else:
            bbox_px = None
    else:
        bbox_px = None

    # Extract phase label — normalize to lowercase for consistent comparison
    if choices_value and len(choices_value) > 0:
        phase = choices_value[0].lower()
    else:
        phase = "off"

    # Extract image reference from task data
    image_url = data.get("task", {}).get("data", {}).get("image", "")
    image_filename = None
    if image_url:
        # Decode Label Studio URL: /data/local-files/?d=data%5Cto_label%5C...%5Cframe_XXXXXX.jpg
        import urllib.parse
        decoded = urllib.parse.unquote(image_url)
        # Normalise backslashes to forward slashes (Label Studio may store Windows paths)
        decoded = decoded.replace("\\", "/")
        # Extract filename from decoded path
        for part in decoded.split("/"):
            if part.startswith("frame_") and part.endswith(".jpg"):
                image_filename = part
                break

    # Extract frame index from annotation ID
    frame_idx = int(data.get("id", 0))

    # Warn if image_filename could not be resolved (will trigger fallback later)
    if not image_filename:
        print(f"[WARN] Could not extract image_filename from annotation {data.get('id', '?')}: image_url was '{image_url}'")

    return {
        "bbox_px": bbox_px,
        "phase": phase,
        "frame_idx": frame_idx,
        "image_filename": image_filename,
        "annotation_id": frame_idx,
    }


def load_frames_csv(csv_path: Path) -> Dict[int, str]:
    """Load the frames.csv mapping file."""
    mapping = {}
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            f.readline()
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    mapping[int(parts[0])] = parts[1]
    except OSError as e:
        print(f"[WARN] Could not load CSV {csv_path}: {e}")
    return mapping


# ============================================================================
# BENCHMARK CORE
# ============================================================================


def compute_iou(box_a, box_b):
    """Compute Intersection over Union between two bounding boxes."""
    x1, y1, w1, h1 = box_a
    x2, y2, w2, h2 = box_b
    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1 + w1, x2 + w2)
    inter_y2 = min(y1 + h1, y2 + h2)
    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area
    if union_area == 0:
        return 0.0
    return inter_area / union_area


def run_detection_on_image(image_path):
    """Run the traffic light detection algorithm on a single image."""
    frame = cv2.imread(str(image_path))
    if frame is None:
        return {"housing_bbox": None, "phase": "unknown", "housing_found": False, "detected_lamps": {}}
    housing_bbox = find_traffic_light_housing(frame)
    housing_found = housing_bbox is not None
    result = {"housing_bbox": housing_bbox, "housing_found": housing_found, "detected_lamps": {}, "phase": "off"}
    if not housing_found:
        return result
    x, y, w, h = housing_bbox
    lamp_positions = []
    for label, y_frac in LAMP_Y_FRACTIONS.items():
        cx = x + w / 2
        cy = y + h * y_frac
        radius = h * LAMP_RADIUS_FRACTION
        lamp_positions.append((label, cx, cy, radius))
    lit_states, lamp_brightnesses, lamp_hues, hue_warnings = _detect_lamps_lit(frame, housing_bbox, lamp_positions)
    result["detected_lamps"] = lit_states
    result["lamp_brightnesses"] = lamp_brightnesses
    phase = _compute_phase_from_lamps(lit_states)
    result["phase"] = phase
    result["hue_warnings"] = hue_warnings
    return result


def benchmark_one_frame(annotation, image_path):
    """Benchmark detection on a single frame."""
    gt_phase = annotation["phase"]
    gt_bbox = annotation["bbox_px"]
    start_time = time.time()
    prediction = run_detection_on_image(image_path)
    elapsed_ms = (time.time() - start_time) * 1000
    pred_phase = prediction["phase"]
    pred_bbox = prediction["housing_bbox"]
    iou = 0.0
    localization_correct = False
    if gt_bbox is not None and pred_bbox is not None:
        iou = compute_iou(gt_bbox, pred_bbox)
        localization_correct = iou >= 0.5
    phase_correct = gt_phase == pred_phase
    if gt_bbox is None:
        if pred_bbox is not None:
            failure_mode = "false_positive (phantom detection)"
        else:
            failure_mode = "correct (no detection)"
    else:
        if pred_bbox is None:
            failure_mode = "false_negative (missed detection)"
        elif iou < 0.5:
            failure_mode = "poor_localization (IoU < 0.5)"
        elif not phase_correct:
            failure_mode = f"phase_mismatch (GT={gt_phase}, pred={pred_phase})"
        else:
            failure_mode = "correct"
    return {
        "frame_idx": annotation["frame_idx"],
        "image_filename": annotation["image_filename"],
        "image_path": str(image_path),
        "ground_truth": {"phase": gt_phase, "bbox_px": gt_bbox},
        "prediction": {"phase": pred_phase, "bbox_px": pred_bbox, "detected_lamps": {k: v for k, v in prediction["detected_lamps"].items()}},
        "metrics": {"iou": round(iou, 4), "localization_correct": localization_correct, "phase_correct": phase_correct, "housing_found": prediction["housing_found"], "elapsed_ms": round(elapsed_ms, 2)},
        "failure_mode": failure_mode,
    }


# ============================================================================
# REPORTING
# ============================================================================


def generate_report(results, generated_at=None, git_commit=None, session_meta=None):
    """Generate a comprehensive benchmark report from the results."""
    total = len(results)
    if total == 0:
        return {
            "error": "No results to report",
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "git_commit": git_commit or "unknown",
            },
        }

    # Build metadata
    if generated_at is None:
        generated_at = datetime.now().isoformat()
    if git_commit is None:
        git_commit = _get_git_commit()
    metadata = {
        "generated_at": generated_at,
        "git_commit": git_commit,
    }

    # Extract key session/run info
    if session_meta:
        resolution = session_meta.get("resolution", [])
        if len(resolution) == 2:
            metadata["resolution"] = f"{resolution[0]}x{resolution[1]}"
        fps = session_meta.get("fps")
        if fps is not None:
            metadata["fps"] = fps
        backend = session_meta.get("backend")
        if backend:
            metadata["camera_backend"] = backend
        controls = session_meta.get("controls", {})
        if controls:
            # Key exposure/camera settings that impact detection quality
            metadata["exposure_time_us"] = controls.get("ExposureTime")
            metadata["analogue_gain"] = controls.get("AnalogueGain")
            metadata["hdr_mode"] = controls.get("HdrMode")
            metadata["nr_mode"] = controls.get("NoiseReductionMode")
            # Extract run note if present
            run_note = session_meta.get("run_note")
            if run_note:
                metadata["run_note"] = run_note

    phase_counts = defaultdict(lambda: {"total": 0, "correct": 0, "ious": []})
    failure_modes = defaultdict(int)
    all_ious = []
    housing_found_count = 0
    housing_missed_as_gt = 0

    for r in results:
        gt_phase = r["ground_truth"]["phase"]
        metrics = r["metrics"]
        iou = metrics["iou"]
        phase_correct = metrics["phase_correct"]
        housing_found = metrics["housing_found"]
        gt_bbox = r["ground_truth"]["bbox_px"]

        if gt_bbox is not None:
            all_ious.append(iou)
            if housing_found:
                housing_found_count += 1
            else:
                housing_missed_as_gt += 1

        phase_counts[gt_phase]["total"] += 1
        if phase_correct:
            phase_counts[gt_phase]["correct"] += 1
        if gt_bbox is not None and iou > 0:
            phase_counts[gt_phase]["ious"].append(iou)

        failure_modes[r["failure_mode"]] += 1

    total_correct_phase = sum(1 for r in results if r["metrics"]["phase_correct"])
    total_correct_localization = sum(1 for r in results if r["metrics"]["localization_correct"])
    mean_iou = float(np.mean(all_ious)) if all_ious else 0.0
    median_iou = float(np.median(all_ious)) if all_ious else 0.0
    std_iou = float(np.std(all_ious)) if all_ious else 0.0
    min_iou = float(np.min(all_ious)) if all_ious else 0.0
    max_iou = float(np.max(all_ious)) if all_ious else 0.0
    p50_iou = float(np.percentile(all_ious, 50)) if all_ious else 0.0
    p90_iou = float(np.percentile(all_ious, 90)) if all_ious else 0.0
    p95_iou = float(np.percentile(all_ious, 95)) if all_ious else 0.0
    avg_time_ms = float(np.mean([r["metrics"]["elapsed_ms"] for r in results]))

    per_phase = {}
    for phase, data in phase_counts.items():
        ious = data["ious"]
        per_phase[phase] = {
            "count": data["total"],
            "phase_accuracy": data["correct"] / data["total"] if data["total"] > 0 else 0.0,
            "mean_iou": float(np.mean(ious)) if ious else 0.0,
            "median_iou": float(np.median(ious)) if ious else 0.0,
            "min_iou": float(np.min(ious)) if ious else 0.0,
            "max_iou": float(np.max(ious)) if ious else 0.0,
        }

    return {
        "metadata": metadata,
        "summary": {
            "total_frames": total,
            "frames_with_gt_bbox": sum(1 for r in results if r["ground_truth"]["bbox_px"] is not None),
            "frames_without_gt_bbox": sum(1 for r in results if r["ground_truth"]["bbox_px"] is None),
            "housing_detected_count": housing_found_count,
            "housing_missed_as_gt": housing_missed_as_gt,
            "phase_accuracy": total_correct_phase / total if total > 0 else 0.0,
            "localization_accuracy": total_correct_localization / total if total > 0 else 0.0,
            "mean_iou": round(mean_iou, 4),
            "median_iou": round(median_iou, 4),
            "std_iou": round(std_iou, 4),
            "min_iou": round(min_iou, 4),
            "max_iou": round(max_iou, 4),
            "p50_iou": round(p50_iou, 4),
            "p90_iou": round(p90_iou, 4),
            "p95_iou": round(p95_iou, 4),
            "avg_detection_time_ms": round(avg_time_ms, 2),
        },
        "per_phase": per_phase,
        "failure_modes": dict(failure_modes),
        "per_frame_results": results,
    }


def print_report(report):
    """Print a human-readable benchmark report to the console."""
    summary = report["summary"]
    per_phase = report["per_phase"]
    failure_modes = report["failure_modes"]
    metadata = report.get("metadata", {})

    print("\n" + "=" * 70)
    print("  TRAFFIC LIGHT DETECTION BENCHMARK REPORT")
    print("=" * 70)

    # Print metadata
    if metadata:
        generated_at = metadata.get("generated_at", "unknown")
        git_commit = metadata.get("git_commit", "unknown")
        print(f"\n  Generated at: {generated_at}")
        print(f"  Git commit:   {git_commit}")

    print(f"\n  Dataset: {summary['total_frames']} annotated frames")
    print(f"  GT with bbox: {summary['frames_with_gt_bbox']} | GT without bbox: {summary['frames_without_gt_bbox']}")

    print("\n" + "-" * 70)
    print("  OVERALL METRICS")
    print("-" * 70)
    print(f"  Phase Accuracy:       {summary['phase_accuracy'] * 100:.1f}% ({int(summary['phase_accuracy'] * summary['total_frames'])}/{summary['total_frames']})")
    print(f"  Localization Accuracy: {summary['localization_accuracy'] * 100:.1f}% ({int(summary['localization_accuracy'] * summary['total_frames'])}/{summary['total_frames']})")
    print(f"  Mean IoU:             {summary['mean_iou']:.4f}")
    print(f"  Median IoU:           {summary['median_iou']:.4f}")
    print(f"  IoU Std Dev:          {summary['std_iou']:.4f}")
    print(f"  IoU Range:            [{summary['min_iou']:.4f}, {summary['max_iou']:.4f}]")
    print(f"  IoU P50:              {summary['p50_iou']:.4f}")
    print(f"  IoU P90:              {summary['p90_iou']:.4f}")
    print(f"  IoU P95:              {summary['p95_iou']:.4f}")
    print(f"  Avg Detection Time:   {summary['avg_detection_time_ms']:.2f} ms")

    print("\n" + "-" * 70)
    print("  PER-PHASE BREAKDOWN")
    print("-" * 70)
    print(f"  {'Phase':<10} {'Count':>6} {'Acc%':>8} {'Mean IoU':>10} {'Med IoU':>10}")
    print(f"  {'-'*10} {'-'*6} {'-'*8} {'-'*10} {'-'*10}")
    for phase in sorted(per_phase.keys()):
        data = per_phase[phase]
        acc_pct = data["phase_accuracy"] * 100
        print(f"  {phase:<10} {data['count']:>6} {acc_pct:>7.1f}% {data['mean_iou']:>10.4f} {data['median_iou']:>10.4f}")

    print("\n" + "-" * 70)
    print("  FAILURE MODES")
    print("-" * 70)
    for mode, count in sorted(failure_modes.items(), key=lambda x: -x[1]):
        pct = count / summary["total_frames"] * 100
        print(f"  {mode:<45} {count:>4} ({pct:5.1f}%)")

    print("\n" + "=" * 70)
    print()


def print_failure_details(results, top_n=10):
    """Print detailed failure case information."""
    failures = [r for r in results if r["failure_mode"] != "correct"]
    if not failures:
        print("\n  No failures detected! All frames passed.")
        return

    print(f"\n  TOP {min(top_n, len(failures))} FAILURE CASES")
    print(f"  {'Frame':<8} {'GT Phase':<10} {'Pred Phase':<10} {'IoU':>8} {'Failure Mode'}")
    print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*8} {'-'*30}")

    sorted_failures = sorted(failures, key=lambda r: r["metrics"]["iou"])
    for r in sorted_failures[:top_n]:
        metrics = r["metrics"]
        print(f"  {r['frame_idx']:<8} {r['ground_truth']['phase']:<10} {r['prediction']['phase']:<10} {metrics['iou']:>8.4f} {r['failure_mode']}")


# ============================================================================
# MARKDOWN REPORT GENERATION
# ============================================================================


def generate_markdown_report(report):
    """Generate a human-readable Markdown benchmark report."""
    lines = []

    def add(text=""):
        lines.append(text)

    metadata = report.get("metadata", {})
    summary = report["summary"]
    per_phase = report["per_phase"]
    failure_modes = report["failure_modes"]
    per_frame = report["per_frame_results"]

    # Title
    add("# Traffic Light Detection Benchmark Report")

    # Metadata
    add("## Metadata")
    add("")
    add("| Field | Value |")
    add("|-------|-------|")
    add(f'| Generated at | {metadata.get("generated_at", "unknown")} |')
    add(f'| Git commit   | `{metadata.get("git_commit", "unknown")}` |')

    # Session/run info (camera settings, resolution, etc.)
    session_fields = [
        ("Resolution", "resolution"),
        ("FPS", "fps"),
        ("Camera backend", "camera_backend"),
        ("Exposure (us)", "exposure_time_us"),
        ("Analogue gain", "analogue_gain"),
        ("HDR mode", "hdr_mode"),
        ("NR mode", "nr_mode"),
        ("Run note", "run_note"),
    ]
    for label, key in session_fields:
        val = metadata.get(key)
        if val is not None:
            add(f"| {label} | {val} |")

    add("")

    # Dataset overview
    add("## Dataset Overview")
    add("")
    add(f"- **Total frames**: {summary['total_frames']}")
    add(f"- **Ground truth with bbox**: {summary['frames_with_gt_bbox']}")
    add(f"- **Ground truth without bbox**: {summary['frames_without_gt_bbox']}")
    add(f"- **Housing detected**: {summary['housing_detected_count']}")
    add(f"- **Housing missed as GT**: {summary['housing_missed_as_gt']}")
    add("")

    # Overall metrics
    add("## Overall Metrics")
    add("")
    add("| Metric | Value |")
    add("|--------|-------|")
    add(f"| Phase Accuracy | {summary['phase_accuracy'] * 100:.1f}% ({int(summary['phase_accuracy'] * summary['total_frames'])}/{summary['total_frames']}) |")
    add(f"| Localization Accuracy | {summary['localization_accuracy'] * 100:.1f}% ({int(summary['localization_accuracy'] * summary['total_frames'])}/{summary['total_frames']}) |")
    add(f"| Mean IoU | {summary['mean_iou']:.4f} |")
    add(f"| Median IoU | {summary['median_iou']:.4f} |")
    add(f"| IoU Std Dev | {summary['std_iou']:.4f} |")
    add(f"| IoU Range | [{summary['min_iou']:.4f}, {summary['max_iou']:.4f}] |")
    add(f"| IoU P50 | {summary['p50_iou']:.4f} |")
    add(f"| IoU P90 | {summary['p90_iou']:.4f} |")
    add(f"| IoU P95 | {summary['p95_iou']:.4f} |")
    add(f"| Avg Detection Time | {summary['avg_detection_time_ms']:.2f} ms |")
    add("")

    # Per-phase breakdown
    add("## Per-Phase Breakdown")
    add("")
    add("| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |")
    add("|-------|-------|----------------|----------|------------|---------|---------|")
    for phase in sorted(per_phase.keys()):
        data = per_phase[phase]
        acc = data["phase_accuracy"] * 100
        add(f"| {phase} | {data['count']} | {acc:.1f}% | {data['mean_iou']:.4f} | {data['median_iou']:.4f} | {data['min_iou']:.4f} | {data['max_iou']:.4f} |")
    add("")

    # Failure modes
    add("## Failure Modes")
    add("")
    add("| Failure Mode | Count | Percentage |")
    add("|--------------|-------|------------|")
    for mode, count in sorted(failure_modes.items(), key=lambda x: -x[1]):
        pct = count / summary["total_frames"] * 100
        add(f"| {mode} | {count} | {pct:.1f}% |")
    add("")

    # Per-frame results
    add("## Per-Frame Results")
    add("")
    add("| Frame | GT Phase | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |")
    add("|-------|----------|-----------|-----|---------------------|---------------|--------------|")
    for r in per_frame:
        metrics = r["metrics"]
        add(f"| {r['frame_idx']} | {r['ground_truth']['phase']} | {r['prediction']['phase']} | {metrics['iou']:.4f} | {metrics['localization_correct']} | {metrics['housing_found']} | {r['failure_mode']} |")
    add("")

    return "\n".join(lines)


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Run the benchmark and save results."""
    parser = argparse.ArgumentParser(description="Benchmark traffic light detection")
    parser.add_argument("--dataset-dir", type=str, default=None, help="Path to dataset directory")
    parser.add_argument("--output", type=str, default="benchmark_report.json", help="Output report path")
    parser.add_argument("--dry-run", action="store_true", help="Run only first 5 frames for testing")
    args = parser.parse_args()

    # Determine dataset directory
    if args.dataset_dir:
        dataset_dir = Path(args.dataset_dir)
    else:
        # Default: labeled dataset root
        dataset_dir = PROJECT_ROOT / "data" / "labeled" / "LEGO-Train-Traffic-Lights"

    # Look for the run subdirectory (e.g. 20260917_065933)
    runs = [d for d in dataset_dir.iterdir() if d.is_dir() and not d.name.startswith(('.', '_'))]
    if not runs:
        print(f"[ERROR] No run directories found in {dataset_dir}")
        return
    run_dir = runs[0]  # Use first (and likely only) run

    annotations_dir = run_dir / "frames"
    images_dir = run_dir / "frames"  # Images are in same 'frames' dir
    csv_path = run_dir / "frames.csv"

    print(f"[INFO] Dataset directory: {dataset_dir}")
    print(f"[INFO] Run directory: {run_dir}")
    print(f"[INFO] Annotations dir: {annotations_dir}")
    print(f"[INFO] Images dir: {images_dir}")
    print(f"[INFO] CSV path: {csv_path}")

    # Load frames.csv mapping
    frame_mapping = load_frames_csv(csv_path) if csv_path.exists() else {}
    if frame_mapping:
        print(f"[INFO] Loaded {len(frame_mapping)} frame mappings from CSV")

    # Load all annotations (files with numeric names, no .jpg extension)
    if not annotations_dir.exists():
        print(f"[ERROR] Annotations directory not found: {annotations_dir}")
        return

    annotation_files = sorted([
        f for f in annotations_dir.iterdir()
        if f.is_file() and not f.name.startswith('.') and not f.name.endswith('.jpg')
    ])
    if not annotation_files:
        print(f"[ERROR] No annotation files found in {annotations_dir}")
        return

    print(f"[INFO] Found {len(annotation_files)} annotation files")

    # Load session metadata if available
    session_meta = None
    session_meta_path = run_dir / "session_meta.json"
    if session_meta_path.exists():
        try:
            with open(session_meta_path, "r", encoding="utf-8") as f:
                session_meta = json.load(f)
            print(f"[INFO] Loaded session metadata from {session_meta_path.name}")
        except Exception as e:
            print(f"[WARN] Failed to load session metadata: {e}")

    # Initialize annotations list
    annotations = []
    for ann_file in annotation_files:
        ann = load_annotation(ann_file)
        if ann:
            # Resolve image path using annotation's image_filename or CSV mapping
            image_filename = ann.get("image_filename")
            frame_idx = ann["frame_idx"]

            if not image_filename and frame_idx in frame_mapping:
                image_filename = frame_mapping[frame_idx]

            # Fallback: derive frame filename from annotation ID
            if not image_filename:
                image_filename = f"frame_{frame_idx:06d}.jpg"
                print(f"[WARN] Fallback: using frame_{frame_idx:06d}.jpg for annotation {ann_file.name} (no image_filename found)")

            if image_filename:
                # Try to find the image file
                possible_paths = [
                    images_dir / image_filename,
                    run_dir / "frames" / image_filename,
                    dataset_dir / run_dir.name / "frames" / image_filename,
                ]
                image_path = None
                for pp in possible_paths:
                    if pp.exists():
                        image_path = pp
                        break

                if image_path:
                    ann["image_path"] = image_path
                    ann["image_filename"] = image_filename
                    annotations.append(ann)
                else:
                    print(f"[WARN] Image not found for {ann_file.name}: {image_filename}")
            else:
                print(f"[WARN] Could not resolve image for annotation {ann_file.name}")

    if not annotations:
        print("[ERROR] No valid annotations with resolvable images found.")
        return

    print(f"[INFO] Running benchmark on {len(annotations)} frames...")
    if args.dry_run:
        print("[INFO] Dry run mode: limiting to 5 frames")
        annotations = annotations[:5]

    results = []
    for i, ann in enumerate(annotations):
        image_path = ann["image_path"]
        frame_idx = ann["frame_idx"]
        gt_phase = ann["phase"]

        # Run benchmark
        result = benchmark_one_frame(ann, image_path)
        results.append(result)

        # Progress indicator
        if (i + 1) % 10 == 0 or i == len(annotations) - 1:
            status = "PASS" if result["failure_mode"] == "correct" else "FAIL"
            print(f"  [{i+1:3d}/{len(annotations)}] Frame {frame_idx:06d} (GT={gt_phase:6s}) -> {result['prediction']['phase']:6s} IoU={result['metrics']['iou']:.4f} [{status}]")

    # Generate report with metadata
    generated_at = datetime.now().isoformat()
    git_commit = _get_git_commit()
    report = generate_report(results, generated_at=generated_at, git_commit=git_commit, session_meta=session_meta)

    # Determine report output directory
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Default output filename
    output_filename = "benchmark_report"

    # JSON
    json_path = reports_dir / f"{output_filename}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n[INFO] JSON report saved to {json_path}")

    # Markdown
    md_report = generate_markdown_report(report)
    md_path = reports_dir / f"{output_filename}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"[INFO] Markdown report saved to {md_path}")

    # Print report
    print_report(report)

    # Print failure details
    print_failure_details(results, top_n=10)

    return report


if __name__ == "__main__":
    main()

