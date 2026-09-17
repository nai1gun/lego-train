#!/usr/bin/env python3
"""
Example: How to load and use the LEGO train dataset from Hugging Face.

This script demonstrates how to:
1. Load the dataset from Hugging Face
2. Explore the data
3. Prepare it for training

Usage:
    python scripts/example_load_dataset.py
"""

from datasets import load_dataset


def load_and_explore():
    """Load the dataset and show basic info."""
    print("🚂 Loading LEGO Train Dataset")
    print("=" * 60)
    
    # Load the dataset from Hugging Face
    # Replace 'lev/lego-train-datasets' with your actual dataset name
    dataset_name = "lev/lego-train-datasets"
    
    try:
        dataset = load_dataset(dataset_name)
    except Exception as e:
        print(f"⚠️  Could not load from Hugging Face: {e}")
        print("   This is expected if the dataset hasn't been uploaded yet.")
        print("   The script will create a sample dataset for demonstration.")
        dataset = create_sample_dataset()
    
    # Show dataset structure
    print(f"\n📊 Dataset splits: {list(dataset.keys())}")
    
    for split_name, split_data in dataset.items():
        print(f"\n  Split: {split_name}")
        print(f"    Samples: {len(split_data)}")
        print(f"    Columns: {split_data.column_names}")
    
    return dataset


def create_sample_dataset():
    """Create a small sample dataset for demonstration."""
    from datasets import Dataset, DatasetDict
    from PIL import Image
    import numpy as np
    
    print("\n📝 Creating sample dataset for demonstration...")
    
    # Create dummy images (small colored squares)
    images = []
    labels = []
    
    # Red images
    for _ in range(10):
        img = Image.fromarray(np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8))
        images.append(img)
        labels.append("red")
    
    # Green images
    for _ in range(10):
        img = Image.fromarray(np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8))
        images.append(img)
        labels.append("green")
    
    # Yellow images
    for _ in range(10):
        img = Image.fromarray(np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8))
        images.append(img)
        labels.append("yellow")
    
    # Split into train/val/test (70/15/15)
    split_point_train = int(0.7 * len(images))
    split_point_val = int(0.85 * len(images))
    
    dataset_dict = DatasetDict({
        "train": Dataset.from_dict({"image": images[:split_point_train], "label": labels[:split_point_train]}),
        "validation": Dataset.from_dict({"image": images[split_point_train:split_point_val], "label": labels[split_point_train:split_point_val]}),
        "test": Dataset.from_dict({"image": images[split_point_val:], "label": labels[split_point_val:]}),
    })
    
    print("✅ Sample dataset created!")
    return dataset_dict


def explore_labels(dataset):
    """Show label distribution."""
    print("\n📈 Label Distribution")
    print("=" * 60)
    
    for split_name, split_data in dataset.items():
        print(f"\n  Split: {split_name}")
        
        # Count labels
        label_counts = {}
        for label in split_data["label"]:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        for label, count in sorted(label_counts.items()):
            percentage = (count / len(split_data)) * 100
            print(f"    {label:15s}: {count:3d} ({percentage:5.1f}%)")


def example_training_prep(dataset):
    """Show how to prepare data for training."""
    print("\n🔧 Example: Preparing Data for Training")
    print("=" * 60)
    
    train_data = dataset["train"]
    
    print("\n  1. Accessing individual samples:")
    print(f"     First image size: {train_data[0]['image'].size}")
    print(f"     First label: {train_data[0]['label']}")
    
    print("\n  2. Iterating through samples:")
    print("     for i, sample in enumerate(train_data):")
    print("         image = sample['image']    # PIL Image")
    print("         label = sample['label']    # String label")
    print("         # Process image with OpenCV, PyTorch, etc.")
    
    print("\n  3. Converting to numpy (for OpenCV):")
    import numpy as np
    first_image = np.array(train_data[0]['image'])
    print(f"     Shape: {first_image.shape}")  # (height, width, channels)
    print(f"     Dtype: {first_image.dtype}")
    
    print("\n  4. Converting to PyTorch tensor:")
    print("     import torch")
    print("     from torchvision import transforms")
    print("     transform = transforms.Compose([")
    print("         transforms.Resize((224, 224)),")
    print("         transforms.ToTensor(),")
    print("     ])")
    print("     tensor = transform(image)")


def main():
    """Main function."""
    # Load and explore the dataset
    dataset = load_and_explore()
    
    # Show label distribution
    explore_labels(dataset)
    
    # Show training preparation example
    example_training_prep(dataset)
    
    print("\n" + "=" * 60)
    print("✅ Example complete!")
    print("\nNext steps:")
    print("  1. Upload your real dataset using:")
    print("     python scripts/upload_dataset.py upload")
    print("  2. Replace the dataset name with your actual repo")
    print("  3. Use this data to train your traffic light classifier!")


if __name__ == "__main__":
    main()
