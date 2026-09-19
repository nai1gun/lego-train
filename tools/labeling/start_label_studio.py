#!/usr/bin/env python3
"""
Start Label Studio with local file serving enabled.

Replaces the old start-label-studio.bat with a cross-platform Python equivalent.

Usage:
    python tools/labeling/start_label_studio.py
"""

import os
import subprocess
import sys
from pathlib import Path

# Colors for terminal output (ANSI escape codes — work on Windows 10+, macOS, Linux)
CYAN = "\033[96m"
GREEN = "\033[92m"
RESET = "\033[0m"


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{code}{text}{RESET}"


def main():
    # Resolve project root (two levels up from this script)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    # Set environment variables for Label Studio
    os.environ["LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED"] = "true"
    os.environ["LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT"] = str(project_root)
    # Disable online version check (avoids errors when offline)
    os.environ["LABEL_STUDIO_DISABLE_INSTALLATION_CHECKS"] = "true"

    print(color("Setting Label Studio environment variables...", CYAN))
    print(f"  LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED={os.environ['LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED']}")
    print(f"  LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT={os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT']}")
    print()

    # Start Label Studio
    print(color("Starting Label Studio...", GREEN))
    subprocess.run(["label-studio"], check=True)


if __name__ == "__main__":
    main()