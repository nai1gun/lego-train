#!/usr/bin/env python3
"""
Download LEGO Train Dataset from Hugging Face.

Downloads your dataset to the local data/labeled/ folder so you can use it
with Label Studio's local file storage.

Usage:
    python tools/hf_upload/download_dataset.py
"""

import subprocess
import sys
from pathlib import Path

# Colors for terminal output (ANSI escape codes — work on Windows 10+, macOS, Linux)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{code}{text}{RESET}"


def main():
    print(color("Downloading LEGO-Train-Traffic-Lights dataset...", CYAN))

    # Resolve paths relative to this script's location
    # Script is at tools/hf_upload/download_dataset.py, so parent is tools/
    project_root = Path(__file__).resolve().parent.parent
    download_dir = project_root / ".." / "data" / "labeled" / "LEGO-Train-Traffic-Lights"
    download_dir = download_dir.resolve()

    # Create download directory if it doesn't exist
    if not download_dir.exists():
        download_dir.mkdir(parents=True, exist_ok=True)
        print(color(f"Created directory: {download_dir}", GREEN))

    # Download using huggingface_hub Python library (preferred approach)
    try:
        from huggingface_hub import snapshot_download
        print(color("Using huggingface_hub Python library...", YELLOW))
        snapshot_download(
            repo_id="nai1gun/LEGO-Train-Traffic-Lights",
            local_dir=str(download_dir),
            repo_type="dataset",
        )
        print(color("\nDownload complete!", GREEN))
        print(color(f"Files are in: {download_dir}", GREEN))
        print(color("\nNext steps:", CYAN))
        print("  1. Start Label Studio: python tools/labeling/start_label_studio.py")
        print('  2. In Label Studio: Settings > Cloud Storage > Add Target Storage')
        print('  3. Select "Local Files" and set path to: /data/labeled')
        return
    except Exception as e:
        print(color(f"\nError using Python library: {e}", RED))
        print(color("Falling back to CLI...", YELLOW))

    # Fallback: try the hf CLI
    huggingface_cmd = [
        "hf", "datasets", "download",
        "nai1gun/LEGO-Train-Traffic-Lights",
        "--local-dir", str(download_dir),
    ]
    print(color(f"Running: {' '.join(huggingface_cmd)}", YELLOW))
    try:
        result = subprocess.run(huggingface_cmd, check=True)
        print(color("\nDownload complete!", GREEN))
        print(color(f"Files are in: {download_dir}", GREEN))
        print(color("\nNext steps:", CYAN))
        print("  1. Start Label Studio: python tools/labeling/start_label_studio.py")
        print('  2. In Label Studio: Settings > Cloud Storage > Add Target Storage')
        print('  3. Select "Local Files" and set path to: /data/labeled')
    except subprocess.CalledProcessError:
        print(color("\nError downloading dataset. Try installing huggingface_hub:", RED))
        print(color("  pip install huggingface_hub", YELLOW))
        print(color("\nAlternative: Download manually from https://huggingface.co/datasets/nai1gun/LEGO-Train-Traffic-Lights", YELLOW))
        sys.exit(1)
    except FileNotFoundError:
        print(color("\nError: hf CLI not found. Install huggingface_hub:", RED))
        print(color("  pip install huggingface_hub", YELLOW))
        sys.exit(1)


if __name__ == "__main__":
    main()