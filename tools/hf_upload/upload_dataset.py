#!/usr/bin/env python3
"""
Helper script to upload LEGO train datasets to Hugging Face.

Usage:
    # First, login to Hugging Face (one-time setup):
    #   python tools/hf_upload/upload_dataset.py login

    # Upload a dataset from the data/ folder:
    #   python tools/hf_upload/upload_dataset.py upload --dataset-name traffic-light-classification

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
    
    dataset_name = args.dataset_name or "lego-train-datasets"
    # Upload from data/curated/ by default (the curated/step with annotated frames)
    dataset_dir = PROJECT_ROOT / "data" / "curated"
    
    if not dataset_dir.exists():
        print(f"❌ Dataset directory not found: {dataset_dir}")
        return False
    
    print(f"📤 Uploading dataset to: {dataset_name}")
    print(f"   Dataset location: {dataset_dir}")
    print()
    
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        
        # Create repo if it doesn't exist
        repo_url = api.create_repo(
            repo_id=dataset_name,
            repo_type="dataset",
            exist_ok=True,
        )
        print(f"✅ Repository ready: {repo_url}")
        print()
        
        # Upload the dataset folder
        print("Uploading files...")
        api.upload_folder(
            folder_path=str(dataset_dir),
            repo_id=dataset_name,
            repo_type="dataset",
        )
        
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

  # Upload your dataset
  python upload_dataset.py upload --dataset-name lev/lego-train-datasets

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
