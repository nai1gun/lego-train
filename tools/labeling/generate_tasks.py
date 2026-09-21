#!/usr/bin/env python3
"""
Generate Label Studio Task JSON from LEGO Train Dataset.

Creates task files from your downloaded Hugging Face dataset so you can
import them directly into Label Studio.

Usage:
    python tools/labeling/generate_tasks.py
    python tools/labeling/generate_tasks.py --dataset-path ./my-data --output-path ./my-tasks.json --frame-interval 5 --max-frames 100
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# ANSI color codes for terminal output (cross-platform)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
GRAY = "\033[90m"
RESET = "\033[0m"


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{code}{text}{RESET}"


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Label Studio tasks from LEGO Train dataset frames.",
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="",
        help="Path to the curated dataset (default: tools/../data/curated/)",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="",
        help="Path for the output JSON file (default: tasks_label_studio.json)",
    )
    parser.add_argument(
        "--frame-interval",
        type=int,
        default=10,
        help="Extract every Nth frame (default: 10)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=50,
        help="Maximum number of frames to process (default: 50)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Set default paths if not provided
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent  # tools/

    if not args.dataset_path:
        dataset_path = project_root / ".." / "data" / "curated"
    else:
        dataset_path = Path(args.dataset_path)
        # Resolve relative paths against the repo root (two levels up from tools/labeling/)
        if not dataset_path.is_absolute():
            repo_root = project_root.parent  # go from tools/ to repo root
            dataset_path = (repo_root / dataset_path).resolve()
        else:
            dataset_path = dataset_path.resolve()

    if not args.output_path:
        output_path = script_dir / "tasks_label_studio.json"
    else:
        output_path = Path(args.output_path)

    print(color("Generating Label Studio tasks...", CYAN))
    print(color(f"  Dataset path: {dataset_path}", GRAY))
    print(color(f"  Output path: {output_path}", GRAY))
    print(color(f"  Frame interval: every {args.frame_interval} frames", GRAY))
    print(color(f"  Max frames: {args.max_frames}", GRAY))

    # Check if dataset exists
    if not dataset_path.exists():
        print(color(f"Error: Dataset not found at {dataset_path}", RED))
        print(color("Please download the dataset first: python tools/hf_upload/download_dataset.py", YELLOW))
        sys.exit(1)

    # Read frames.csv metadata if available
    frames_csv_path = dataset_path / "frames.csv"
    frames_metadata = None
    if frames_csv_path.exists():
        print(color("Reading frames.csv metadata...", GRAY))
        with open(frames_csv_path, "r", encoding="utf-8") as f:
            frames_metadata = list(csv.DictReader(f))
        print(color(f"  Found {len(frames_metadata)} frames in metadata", GRAY))
    else:
        print(color("Warning: frames.csv not found. Will use frame directory.", YELLOW))

    # Get frame files
    frames_dir = dataset_path / "frames"
    if not frames_dir.exists():
        print(color(f"Error: frames directory not found at {frames_dir}", RED))
        sys.exit(1)

    frame_files = sorted(frames_dir.glob("*.jpg"))
    print(color(f"  Found {len(frame_files)} frame images", GRAY))

    # Generate tasks
    tasks = []
    frame_count = 0
    task_index = 0

    for frame in frame_files:
        if frame_count >= args.max_frames:
            break

        if frame_count % args.frame_interval != 0 and frame_count != 0:
            frame_count += 1
            continue

        # Extract frame number from filename (frame_000000.jpg -> 0)
        frame_num = int(frame.stem.replace("frame_", ""))

        # Build Label Studio local file path
        dataset_name = dataset_path.resolve().name
        local_path = f"data/curated/{dataset_name}/frames/{frame.name}"

        task = {
            "id": task_index + 1,
            "predictions": [],
            "annotations": [],
            "file_upload": None,
            "data": {
                "image": f"/data/local-files/?d={local_path}",
                "frames_csv": f"/data/local-files/?d=data/curated/{dataset_name}/frames.csv",
                "frame_idx": frame_num,
                "session": dataset_name,
            },
            "meta": {
                "frame_number": frame_num,
                "filename": frame.name,
                "total_frames": len(frame_files),
            },
        }

        # Add metadata from frames.csv if available
        if frames_metadata and frame_count < len(frames_metadata):
            meta = frames_metadata[frame_count]
            task["meta"]["timestamp"] = meta.get("wall_timestamp", "")
            task["meta"]["exposure_us"] = meta.get("exposure_us", "")
            task["meta"]["analogue_gain"] = meta.get("analogue_gain", "")

        tasks.append(task)
        frame_count += 1
        task_index += 1

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")

    print(color(f"\nSuccessfully generated {len(tasks)} tasks!", GREEN))
    print(color(f"Saved to: {output_path}", GREEN))
    print(color("\nTo import into Label Studio:", CYAN))
    print("  1. Start Label Studio: python tools/labeling/start_label_studio.py")
    print("  2. Create a new project or open existing one")
    print("  3. Go to Data Manager > Import")
    print(f"  4. Upload the file: {output_path}")
    print("  5. Set up local storage: Settings > Cloud Storage > Add Target Storage > Local Files")
    print("  6. Set path to: /data/curated")


if __name__ == "__main__":
    main()