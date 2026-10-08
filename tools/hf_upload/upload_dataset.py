#!/usr/bin/env python3
"""
Helper script to upload LEGO train datasets to Hugging Face.

Usage:
    # First, login to Hugging Face (one-time setup):
    #   python tools/hf_upload/upload_dataset.py login

    # Upload a dataset from the data/ folder:
    #   python tools/hf_upload/upload_dataset.py upload --dataset-name traffic-light-classification

    # Incremental upload (only a new session):
    #   python tools/hf_upload/upload_dataset.py upload --dataset-name lev/LEGO-Train-Traffic-Lights --session 20260928_161408

    # List your datasets:
    #   python tools/hf_upload/upload_dataset.py list

Author: Lev & AI Assistant
"""

import argparse
import os
import sys
from pathlib import Path

# Go up 3 levels: tools/hf_upload/ → tools/ → project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_hf_token() -> bool:
    """Check if Hugging Face token is configured."""
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not hf_token:
        print("⚠️  Hugging Face token not found!")
        print()
        print("To set your token, run one of these:")
        print()
        print("  Windows PowerShell:")
        print('    $env:HF_TOKEN="your_token_here"')
        print()
        print("  Or permanently:")
        print('    setx HF_TOKEN "your_token_here"')
        print()
        print("  Linux/Mac:")
        print('    export HF_TOKEN="your_token_here"')
        print()
        print("Get your token at: https://huggingface.co/settings/tokens")
        return False
    return True


def cmd_login(args):
    """Interactive login to Hugging Face."""
    print("🔐 Hugging Face Login")
    print("=" * 50)
    print()
    
    token = input("Enter your Hugging Face token: ").strip()
    if not token:
        print("❌ Token cannot be empty.")
        return False
    
    # Save token to environment
    os.environ["HF_TOKEN"] = token
    
    # Test the token by trying to get user info
    try:
        from huggingface_hub import whoami
        user = whoami(token)
        username = user["name"]
        print(f"✅ Successfully logged in as: @{username}")
        print()
        print("Token saved to current environment.")
        print("To make it permanent, add it to your system environment variables:")
        print()
        print("  Windows PowerShell (permanent):")
        print('    setx HF_TOKEN "your_token_here"')
        print()
        print("  Linux/Mac (add to ~/.bashrc or ~/.zshrc):")
        print('    export HF_TOKEN="your_token_here"')
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False


def cmd_upload(args):
    """Upload a dataset to Hugging Face."""
    if not check_hf_token():
        return False
    
    # Default to 'labeled' data (includes JSON annotations from Label Studio)
    # Use --source curated for inference-ready frames only (no annotations)
    dataset_name = args.dataset_name or "lego-train-datasets"
    source = args.source or "labeled"
    session_name = args.session  # None means full project upload
    
    if source == "curated":
        dataset_dir = PROJECT_ROOT / "data" / "curated"
        commit_msg = "Upload dataset from local curated data"
    else:
        # labeled data has structure: data/labeled/{project_name}/{session}/
        # Extract project name from --dataset-name (e.g., "nai1gun/LEGO-Train-Traffic-Lights" -> "LEGO-Train-Traffic-Lights")
        labeled_dir = PROJECT_ROOT / "data" / "labeled"
        if not labeled_dir.exists():
            print(f"❌ Labeled data directory not found: {labeled_dir}")
            return False
        # Derive the project folder name from --dataset-name
        project_name = dataset_name.split("/")[-1]
        project_dir = labeled_dir / project_name
        if not project_dir.exists():
            print(f"❌ Project folder not found: {project_dir}")
            print(f"   Hint: make sure '{project_name}' exists in {labeled_dir}")
            return False
        
        if session_name:
            # Incremental: upload only the specified session
            dataset_dir = project_dir / session_name
            if not dataset_dir.exists():
                print(f"❌ Session folder not found: {dataset_dir}")
                print(f"   Available sessions in {project_dir}:")
                for item in sorted(project_dir.iterdir()):
                    if item.is_dir():
                        print(f"     - {item.name}")
                return False
            commit_msg = f"Upload session '{session_name}' to dataset '{project_name}'"
        else:
            # Full project upload
            dataset_dir = project_dir
            commit_msg = f"Upload labeled dataset '{project_name}' from local data"
    
    if not dataset_dir.exists():
        print(f"❌ Dataset directory not found: {dataset_dir}")
        return False
    
    print(f"📤 Uploading dataset to: {dataset_name}")
    print(f"   Dataset location: {dataset_dir}")
    print(f"   Source: {source}")
    print()
    
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        
        # The repo may have corrupted paths from previous Windows uploads (backslashes in paths).
        # Delete and recreate to ensure a clean state.
        print("Checking repo state...")
        try:
            existing_files = api.list_repo_files(repo_id=dataset_name, repo_type="dataset")
            bad_files = [f for f in existing_files if "\\" in f]
            if bad_files:
                print(f"⚠️  Found {len(bad_files)} files with corrupted (backslash) paths. Deleting repo...")
                api.delete_repo(repo_id=dataset_name, repo_type="dataset")
                print("✅ Repo deleted. Recreating...")
                api.create_repo(
                    repo_id=dataset_name,
                    repo_type="dataset",
                    exist_ok=False,
                )
            else:
                print(f"✅ Repo clean ({len(existing_files)} files). Uploading to existing repo...")
        except Exception as list_err:
            # Repo doesn't exist — create it fresh
            print("⚠️  Repo not found. Creating new repo...")
            api.create_repo(
                repo_id=dataset_name,
                repo_type="dataset",
                exist_ok=False,
            )
            print("✅ Repo created.")
        
        # Compute which remote files don't exist locally — these need deletion
        # Only compare files that belong to this project (scoped to the project folder name)
        project_folder_name = dataset_dir.name
        local_files_relative = set()
        for filepath in dataset_dir.rglob("*"):
            if filepath.is_file():
                rel = filepath.relative_to(dataset_dir)
                local_files_relative.add(str(rel))
        
        # For incremental uploads (--session), don't delete any existing remote files
        delete_patterns = None
        if session_name is None and existing_files:
            # Only consider remote files that start with the project folder name
            project_files = [f for f in existing_files if f.startswith(project_folder_name + "/") or f == project_folder_name]
            missing_from_local = [f for f in project_files if f not in local_files_relative]
            if missing_from_local:
                print(f"🗑️  Found {len(missing_from_local)} file(s) in repo that no longer exist locally, will remove from HF:")
                for f in missing_from_local[:20]:  # show first 20 only
                    print(f"      - {f}")
                if len(missing_from_local) > 20:
                    print(f"      ... and {len(missing_from_local) - 20} more")
                delete_patterns = missing_from_local
            else:
                print("✅ No deleted files to sync.")
        elif session_name:
            print(f"ℹ️  Incremental upload: not checking for deletions (old data preserved)")
        else:
            delete_patterns = None
        
        # Upload the dataset folder with sync (delete) support
        # Note: upload_folder uses the local folder's name as the repo root prefix.
        # For incremental uploads we must pass path_in_repo to place files in the
        # correct session subdirectory (e.g., 20260928_161408/...).
        print("Uploading files...")
        if session_name:
            # Incremental: tell upload_folder the correct repo subdirectory
            # The existing dataset root is already LEGO-Train-Traffic-Lights/,
            # so we only need the session folder name as path_in_repo.
            repo_subdir = session_name
        else:
            repo_subdir = None  # let upload_folder use the folder name

        upload_kwargs = dict(
            folder_path=str(dataset_dir),
            repo_id=dataset_name,
            repo_type="dataset",
            commit_message=commit_msg,
            delete_patterns=delete_patterns,  # remove remote files that no longer exist locally
        )
        if repo_subdir:
            upload_kwargs["path_in_repo"] = repo_subdir

        api.upload_folder(**upload_kwargs)
        
        print()
        print("✅ Upload complete!")
        print(f"🔗 View your dataset: https://huggingface.co/datasets/{dataset_name}")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def cmd_list(args):
    """List datasets owned by the user."""
    if not check_hf_token():
        return False
    
    try:
        from huggingface_hub import HfApi, whoami
        
        # Auto-detect the authenticated user's username
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        user_info = whoami(token)
        username = user_info["name"]
        print(f"🔍 Fetching datasets for @{username}...")
        
        api = HfApi()
        datasets = api.list_datasets(author=username)
        
        if not datasets:
            print("No datasets found. Create one first!")
            return False
        
        print("📚 Your Hugging Face Datasets:")
        print("=" * 60)
        for ds in datasets:
            print(f"  • {ds.id}")
            if ds.description:
                print(f"    {ds.description[:80]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to list datasets: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Upload LEGO train datasets to Hugging Face",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Login to Hugging Face
  python upload_dataset.py login

  # Upload your dataset (default: labeled data with annotations)
  python upload_dataset.py upload --dataset-name lev/lego-train-datasets

  # Or upload curated frames only (no annotations)
  python upload_dataset.py upload --dataset-name lev/lego-train-datasets --source curated

  # Incremental upload: only a new session (fast, no deletions)
  python upload_dataset.py upload --dataset-name lev/LEGO-Train-Traffic-Lights --session 20260928_161408

  # List your datasets
  python upload_dataset.py list
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Login command
    subparsers.add_parser("login", help="Login to Hugging Face")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload dataset to Hugging Face")
    upload_parser.add_argument(
        "--dataset-name",
        type=str,
        help="Dataset name (e.g., lev/lego-train-datasets)",
    )
    upload_parser.add_argument(
        "--source",
        type=str,
        choices=["labeled", "curated"],
        default="labeled",
        help="Data source: 'labeled' (default, includes JSON annotations) or 'curated' (frames only)",
    )
    upload_parser.add_argument(
        "--session",
        type=str,
        default=None,
        help="Incremental upload: only upload this session folder (e.g., 20260928_161408). Skips deletion of existing remote data.",
    )
    
    # List command
    subparsers.add_parser("list", help="List your Hugging Face datasets")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # Map commands to functions
    commands = {
        "login": cmd_login,
        "upload": cmd_upload,
        "list": cmd_list,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
