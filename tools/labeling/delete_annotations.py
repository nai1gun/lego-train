#!/usr/bin/env python3
"""
Delete annotations from Label Studio for a specific run/task.

Use this when you need to remove bad annotations before re-labeling or
re-running a benchmark. The Label Studio web UI does not provide a
one-click delete button for submitted annotations, so we use the REST API.

Usage:
    # List annotations for a task (shows IDs to identify which to delete)
    python tools/labeling/delete_annotations.py --project-id 1 --task-id 42 --list

    # Delete specific annotations by ID
    python tools/labeling/delete_annotations.py --project-id 1 --task-id 42 --delete-ids 5 7 12

    # Delete ALL annotations for a task (useful to re-label a run from scratch)
    python tools/labeling/delete_annotations.py --project-id 1 --task-id 42 --delete-all

    # Delete annotations for ALL tasks in a project
    python tools/labeling/delete_annotations.py --project-id 1 --delete-all

Environment variables (optional):
    LABEL_STUDIO_URL     - Label Studio URL (default: http://localhost:8080)
    LABEL_STUDIO_API_KEY - Your Personal Access Token (found in Settings -> Account & Settings -> Personal Access Token)

    If LABEL_STUDIO_API_KEY is not set, you will be prompted interactively.

Authentication:
    Personal Access Tokens are JWT *refresh* tokens. Label Studio rejects them
    as a Bearer header (HTTP 401); they must first be exchanged at
    /api/token/refresh/ for a short-lived access token. This script does that
    automatically. Legacy 40-character tokens are sent with the "Token" scheme.
"""

import argparse
import os
import sys
import time

import requests

# ANSI color codes for terminal output (cross-platform)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{code}{text}{RESET}"


def get_api_key() -> str:
    """Get the API key from environment or prompt the user."""
    api_key = os.environ.get("LABEL_STUDIO_API_KEY", "").strip()
    if api_key:
        return api_key

    print(color("\n⚠ LABEL_STUDIO_API_KEY not set.", YELLOW))
    print(color("  Get it from: Label Studio -> Settings -> Account & Settings -> Personal Access Token", GRAY))
    print(color("  Or set it: export LABEL_STUDIO_API_KEY='your-token' (Linux/Mac)", GRAY))
    print(color("             set LABEL_STUDIO_API_KEY='your-token' (Windows CMD)", GRAY))
    print(color("             $env:LABEL_STUDIO_API_KEY='your-token' (PowerShell)", GRAY))
    print()
    api_key = input("  Paste your API key: ").strip()
    if not api_key:
        print(color("Error: API key is required.", RED))
        sys.exit(1)
    return api_key


def get_base_url() -> str:
    """Get the Label Studio base URL from environment or prompt."""
    url = os.environ.get("LABEL_STUDIO_URL", "").strip()
    if not url:
        print(color("\n⚠ LABEL_STUDIO_URL not set.", YELLOW))
        url = input("  Label Studio URL (default: http://localhost:8080): ").strip()
    if not url:
        url = "http://localhost:8080"
    return url.rstrip("/")


def exit_connection_error(base_url: str):
    print(color(f"\nError: Could not connect to Label Studio at {base_url}", RED))
    print(color("  Make sure Label Studio is running: python tools/labeling/start_label_studio.py", YELLOW))
    sys.exit(1)


def exit_http_error(response: requests.Response):
    print(color(f"\nError: HTTP {response.status_code} -", RED))
    if response.status_code == 404:
        print(color("  Not found. Check that the project/task ID exists.", RED))
    elif response.status_code == 401:
        print(color("  Authentication failed. Check your LABEL_STUDIO_API_KEY.", RED))
    elif response.status_code == 403:
        print(color("  Permission denied. Check your API key permissions.", RED))
    else:
        preview = response.text[:500]
        msg = color(f"  Response preview: {preview}...", RED) if len(response.text) > 500 else color(f"  Response: {response.text}", RED)
        print(msg)
    sys.exit(1)


class LabelStudioAuth(requests.auth.AuthBase):
    """Attach Label Studio credentials to each request, refreshing the JWT access token as needed."""

    # Label Studio issues 5-minute access tokens; refresh a bit early
    ACCESS_TOKEN_MAX_AGE = 240

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.is_jwt = api_key.count(".") == 2
        self._access_token = None
        self._fetched_at = 0.0

    def _get_access_token(self) -> str:
        if self._access_token and time.monotonic() - self._fetched_at < self.ACCESS_TOKEN_MAX_AGE:
            return self._access_token

        try:
            response = requests.post(
                f"{self.base_url}/api/token/refresh/", json={"refresh": self.api_key}, timeout=10
            )
        except requests.exceptions.ConnectionError:
            exit_connection_error(self.base_url)

        if response.status_code != 200:
            print(color(f"\nError: Could not exchange LABEL_STUDIO_API_KEY for an access token (HTTP {response.status_code}).", RED))
            print(color("  The token may have been revoked. Revoke it in Label Studio -> Account & Settings ->", YELLOW))
            print(color("  Personal Access Token, then create a new one.", YELLOW))
            sys.exit(1)

        self._access_token = response.json()["access"]
        self._fetched_at = time.monotonic()
        return self._access_token

    def __call__(self, request):
        if self.is_jwt:
            request.headers["Authorization"] = f"Bearer {self._get_access_token()}"
        else:
            request.headers["Authorization"] = f"Token {self.api_key}"
        return request


def fetch_task_annotations(base_url: str, task_id: int, auth: LabelStudioAuth) -> list[dict]:
    """Fetch all annotations for a task. The endpoint returns a plain JSON list."""
    response = requests.get(f"{base_url}/api/tasks/{task_id}/annotations/", auth=auth, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_project_tasks(base_url: str, project_id: int, auth: LabelStudioAuth) -> list[dict]:
    """Fetch all tasks in a project, following Label Studio's page-based pagination."""
    url = f"{base_url}/api/projects/{project_id}/tasks/"
    page_size = 100
    tasks = []
    page = 1
    while True:
        response = requests.get(url, auth=auth, params={"page": page, "page_size": page_size}, timeout=10)
        # Label Studio answers 404 when asked for a page past the last one
        if response.status_code == 404 and page > 1:
            break
        response.raise_for_status()
        batch = response.json()
        tasks.extend(batch)
        if len(batch) < page_size:
            break
        page += 1
    return tasks


def list_annotations(base_url: str, project_id: int, task_id: int, auth: LabelStudioAuth):
    """List all annotations for a specific task."""
    print(color(f"\nFetching annotations for project {project_id}, task {task_id}...", GRAY))
    print(color(f"  URL: {base_url}/api/tasks/{task_id}/annotations/", GRAY))

    try:
        annotations = fetch_task_annotations(base_url, task_id, auth)
    except requests.exceptions.ConnectionError:
        exit_connection_error(base_url)
    except requests.exceptions.HTTPError as e:
        exit_http_error(e.response)

    if not annotations:
        print(color(f"\n  No annotations found for task {task_id}.", GREEN))
        return annotations

    print(color(f"\n  Found {len(annotations)} annotation(s):\n", BOLD))
    print(f"  {'ID':<8} {'Created':<22} {'Updated':<22} {'Cancelled':<10} {'State':<12} {'Lead Time':<12}")
    print(f"  {'-'*8} {'-'*22} {'-'*22} {'-'*10} {'-'*12} {'-'*12}")

    for ann in annotations:
        created = ann.get("created_at", "N/A")[:19].replace("T", " ")
        updated = ann.get("updated_at", "N/A")[:19].replace("T", " ")
        cancelled = "YES" if ann.get("was_cancelled") else "no"
        state = ann.get("status", "N/A")
        lead = ann.get("lead_time", 0)
        if lead:
            minutes = int(lead // 60)
            seconds = int(lead % 60)
            lead_str = f"{minutes}m {seconds}s"
        else:
            lead_str = "N/A"

        status_color = GREEN if state == "completed" else YELLOW if state == "skipped" else RED
        print(
            f"  {ann['id']:<8} {created:<22} {updated:<22} {cancelled:<10} "
            f"{color(status_color + state + RESET, status_color):<12} {lead_str:<12}"
        )

    print(color(f"\n  To delete annotations, use:", CYAN))
    print(f"    python {sys.argv[0]} --project-id {project_id} --task-id {task_id} --delete-ids <id1> <id2> ...")
    print(f"    python {sys.argv[0]} --project-id {project_id} --task-id {task_id} --delete-all")
    print()

    return annotations


def delete_annotations(base_url: str, annotation_ids: list[int], auth: LabelStudioAuth):
    """Delete specific annotations by ID."""
    deleted_count = 0
    errors = []

    for ann_id in annotation_ids:
        url = f"{base_url}/api/annotations/{ann_id}/"
        try:
            response = requests.delete(url, auth=auth, timeout=10)
            if response.status_code in (200, 204):
                deleted_count += 1
                print(color(f"  Deleted annotation {ann_id}", GREEN))
            else:
                errors.append((ann_id, response.status_code, response.text.strip()))
                print(color(f"  Failed to delete annotation {ann_id}: HTTP {response.status_code}", RED))
        except requests.exceptions.RequestException as e:
            errors.append((ann_id, None, str(e)))
            print(color(f"  Error deleting annotation {ann_id}: {e}", RED))

    # Summary
    print()
    if deleted_count > 0:
        print(color(f"  Successfully deleted {deleted_count} annotation(s).", GREEN))
    if errors:
        print(color(f"  Failed to delete {len(errors)} annotation(s):", RED))
        for ann_id, code, msg in errors:
            detail = f"HTTP {code}" if code else msg
            print(f"    Annotation {ann_id}: {detail}")
    if deleted_count == 0 and not errors:
        print(color("  No annotations were deleted.", YELLOW))
    print()


def delete_all_annotations(base_url: str, project_id: int, auth: LabelStudioAuth):
    """Delete ALL annotations for ALL tasks in a project."""
    total_deleted = 0

    print(color(f"\nFetching all tasks for project {project_id}...", GRAY))

    try:
        tasks = fetch_project_tasks(base_url, project_id, auth)
    except requests.exceptions.ConnectionError:
        exit_connection_error(base_url)
    except requests.exceptions.HTTPError as e:
        exit_http_error(e.response)

    if not tasks:
        print(color(f"\n  No tasks found in project {project_id}.", YELLOW))
        return

    print(color(f"  Found {len(tasks)} task(s) in project {project_id}.", GRAY))
    print()

    for task in tasks:
        task_id = task["id"]
        task_name = task.get("file_upload", f"task-{task_id}")
        print(color(f"  Processing task {task_id} ({task_name})...", GRAY))

        try:
            annotations = fetch_task_annotations(base_url, task_id, auth)
        except requests.exceptions.RequestException:
            print(color(f"    Could not fetch annotations for task {task_id}.", YELLOW))
            continue

        if not annotations:
            print(color(f"    No annotations for task {task_id}.", GRAY))
            continue

        print(color(f"    Found {len(annotations)} annotation(s) - deleting all...", YELLOW))

        for ann in annotations:
            del_url = f"{base_url}/api/annotations/{ann['id']}/"
            try:
                del_resp = requests.delete(del_url, auth=auth, timeout=10)
                if del_resp.status_code in (200, 204):
                    total_deleted += 1
                else:
                    print(color(f"    Failed to delete annotation {ann['id']}: HTTP {del_resp.status_code}", RED))
            except requests.exceptions.RequestException as e:
                print(color(f"    Error deleting annotation {ann['id']}: {e}", RED))

    print()
    if total_deleted > 0:
        print(color(f"  Deleted {total_deleted} annotation(s) across {len(tasks)} task(s).", GREEN))
    else:
        print(color("  No annotations were deleted.", YELLOW))
    print()


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Delete annotations from Label Studio for LEGO Train dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List annotations for a task
  python tools/labeling/delete_annotations.py --project-id 1 --task-id 42 --list

  # Delete specific annotations
  python tools/labeling/delete_annotations.py --project-id 1 --task-id 42 --delete-ids 5 7 12

  # Delete all annotations for a task
  python tools/labeling/delete_annotations.py --project-id 1 --task-id 42 --delete-all

  # Delete all annotations for all tasks in a project
  python tools/labeling/delete_annotations.py --project-id 1 --delete-all
        """,
    )
    parser.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="Label Studio project ID (found in URL: /projects/#/projects/<ID>/)",
    )
    parser.add_argument(
        "--task-id",
        type=int,
        help="Task ID to delete annotations from (required with --delete-all or --delete-ids)",
    )
    parser.add_argument(
        "--delete-ids",
        type=int,
        nargs="+",
        help="Annotation IDs to delete (use --list first to find IDs)",
    )
    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="Delete ALL annotations for the specified task (or all tasks if --task-id is omitted)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all annotations for the specified task (useful to find IDs)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate arguments
    if args.delete_ids and not args.task_id:
        print(color("Error: --task-id is required when using --delete-ids", RED))
        sys.exit(1)

    if args.delete_all and not args.list:
        # Bulk delete all - confirm first
        scope = "all tasks in the project" if args.task_id is None else f"task {args.task_id}"
        print()
        confirmation = input(
            color(f"  WARNING: This will delete ALL annotations for {scope}. Continue? (yes/no): ", RED)
        ).strip().lower()
        if confirmation not in ("yes", "y"):
            print(color("  Cancelled. No annotations were deleted.", YELLOW))
            sys.exit(0)

    # Get credentials
    base_url = get_base_url()
    auth = LabelStudioAuth(base_url, get_api_key())

    # Execute the requested action
    if args.list:
        if not args.task_id:
            print(color("Error: --task-id is required with --list", RED))
            sys.exit(1)
        list_annotations(base_url, args.project_id, args.task_id, auth)

    elif args.delete_ids:
        print(color(f"\nDeleting annotation IDs: {args.delete_ids}", YELLOW))
        delete_annotations(base_url, args.delete_ids, auth)

    elif args.delete_all:
        if args.task_id:
            print(color(f"\nDeleting ALL annotations for task {args.task_id}...", YELLOW))
            try:
                annotations = fetch_task_annotations(base_url, args.task_id, auth)
            except requests.exceptions.RequestException as e:
                print(color(f"\nError fetching annotations: {e}", RED))
                sys.exit(1)
            ids_to_delete = [a["id"] for a in annotations]
            if not ids_to_delete:
                print(color(f"\n  No annotations found for task {args.task_id}.", YELLOW))
                return
            print(color(f"  Found {len(ids_to_delete)} annotation(s) - proceeding with deletion.", YELLOW))
            delete_annotations(base_url, ids_to_delete, auth)
        else:
            delete_all_annotations(base_url, args.project_id, auth)

    else:
        print(color("\nNo action specified. Use --list, --delete-ids, or --delete-all.", YELLOW))
        print(color("\nRun with --help for usage information.", GRAY))


if __name__ == "__main__":
    main()
