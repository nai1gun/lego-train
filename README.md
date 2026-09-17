# Autonomous LEGO Train Project

This project implements an autonomous LEGO train using Raspberry Pi, camera vision, and Bluetooth controls.

## Hardware Overview

Here's an annotated view of our LEGO train showing the key components:

![LEGO Train Components](./lego_train_annotated.png)

### Component Breakdown

The numbers match the badges on the photo above:

| # | Component | Location | Description |
|---|-----------|----------|-------------|
| 1 | 🔋 **Power bank** | On the roof of the first carriage | Portable 5V supply for the Raspberry Pi, so the train runs untethered |
| 2 | 📷 **Raspberry Pi Camera** | In the nose of the first carriage | Looks down the track ahead and feeds frames to the Pi for autonomous navigation |
| 3 | 🖥️ **Raspberry Pi** | Inside the first carriage (visible through the windows) | The brain of the train — runs the Python code, processes camera frames, and sends motor commands |
| 4 | ⚙️ **LEGO train motor** | Front half of the second carriage | Drives the train forward and backward, controlled over Bluetooth from the Raspberry Pi |

The annotated image is generated from the original photo by
[`scripts/annotate_train.py`](./scripts/annotate_train.py) — edit the coordinates
in that script and re-run it to adjust the labels:

```bash
python scripts/annotate_train.py
```

## Project Structure

```
.
├── src/
│   └── bluetooth_controller.py     # Bluetooth controller for LEGO motors
├── scripts/
│   ├── camera_smoke_test.py        # Camera smoke test (auto-detects Pi / USB)
│   ├── annotate_train.py           # Regenerates lego_train_annotated.png
│   ├── test_and_copy.ps1           # Helper: run test on Pi, copy results back
│   ├── upload_dataset.py           # Upload datasets to Hugging Face
│   └── example_load_dataset.py     # Example: load and explore datasets
├── datasets/                       # Local dataset storage (synced to HF)
├── tests/                          # Unit tests (reserved for future)
├── README.md                       # This file
└── .clinerules                     # Project documentation and guidelines
```

## Virtual Environment

This project uses a Python virtual environment located at `.venv`. All development and package installations should be done within this environment.

To activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

If the `.venv` directory doesn't exist, it should be created using `python -m venv .venv`

## Getting Started

### 1. Prerequisites

- Python 3.x installed on development machine
- Bluetooth support enabled
- Raspberry Pi with SSH access (hostname: `levpi`)

### 2. Install Required Packages

First, activate the virtual environment:
```bash
# On Windows
.venv\Scripts\activate

# On Linux/Mac
source .venv/bin/activate
```

Then install required packages:
```bash
pip install bleak
pip install opencv-python       # For local development on Windows
pip install opencv-python-headless  # For Raspberry Pi (no GUI needed)
pip install pillow              # Only needed to regenerate the annotated photo
```

### 3. Camera Setup

Before using the camera, make sure:
1. The Pi Camera Module is properly connected to the CSI port
2. Camera is enabled on Raspberry Pi (`raspi-config` → Interface Options → Camera)

#### Test the Camera

Run the camera smoke test to verify everything works:

```bash
# On Windows (development host)
python scripts/camera_smoke_test.py

# On Raspberry Pi (via SSH)
ssh lev@levpi
cd ~/lego-train
source .venv/bin/activate
python scripts/camera_smoke_test.py
```

The test will:
- Open the camera and display a live preview
- Show resolution and FPS information
- Capture a screenshot automatically after 5 seconds
- Save it as `camera_test_screenshot.jpg`

### 4. Connect to Raspberry Pi

```bash
ssh lev@levpi
```

## Bluetooth Control

The `src/bluetooth_controller.py` script provides:

1. **Device Discovery**: Automatically scans for LEGO devices
2. **Connection Management**: Establishes connection to LEGO motors
3. **Command Interface**: Sends commands like forward, backward, and stop

### Usage

```bash
python src/bluetooth_controller.py
```

## Dataset Management

This project uses [Hugging Face Datasets](https://huggingface.co/datasets) to store and manage labeled training data.

### Why Hugging Face?
- **Built for ML data** — handles images, labels, and metadata cleanly
- **Easy code integration** — load datasets with one line of Python
- **Version control** — track dataset changes alongside model changes
- **Free hosting** — generous free tier for private datasets
- **Team-friendly** — easy to share with Lev for collaborative work

### Setup (One-Time)

1. **Create a Hugging Face account** at [huggingface.co](https://huggingface.co/join)

2. **Get your API token**:
   - Go to Settings → Access Tokens
   - Create a new token (type: "Write")
   - Copy the token

3. **Set the token on your computer**:
   ```powershell
   # Windows (current session)
   $env:HF_TOKEN="your_token_here"
   
   # Windows (permanent)
   setx HF_TOKEN "your_token_here"
   
   # Linux/Mac
   export HF_TOKEN="your_token_here"
   ```

4. **Login via the helper script**:
   ```bash
   python scripts/upload_dataset.py login
   ```

### Uploading Your Dataset

1. **Organize your data** in the `datasets/` folder:
   ```
   datasets/
   ├── traffic_light_red/
   │   ├── image1.jpg
   │   └── image2.jpg
   ├── traffic_light_green/
   │   ├── image1.jpg
   │   └── image2.jpg
   └── README.md
   ```

2. **Upload to Hugging Face**:
   ```bash
   python scripts/upload_dataset.py upload --dataset-name lev/lego-train-datasets
   ```

### Loading the Dataset in Code

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("lev/lego-train-datasets")

# Access training data
train_images = dataset["train"]["image"]
train_labels = dataset["train"]["label"]

print(f"Training samples: {len(train_images)}")
```

### Dataset Structure
See [datasets/README.md](./datasets/README.md) for detailed documentation.

---

## Project Components

- `src/bluetooth_controller.py`: Main Bluetooth controller with device discovery and command sending
- `scripts/camera_smoke_test.py`: Camera smoke test - verifies camera is working correctly (auto-detects Pi / USB)
- `scripts/annotate_train.py`: Redraws the component labels on `lego_train.jpg` (needs `pillow`)
- `tests/`: Unit tests (reserved for future)
- `README.md`: Project documentation
- `.clinerules`: Project documentation and guidelines

## Troubleshooting

### Bluetooth Issues
If you encounter Bluetooth connection problems:

1. Ensure Bluetooth is enabled on both devices
2. Check that your Raspberry Pi has the necessary Bluetooth support
3. Verify permissions for accessing Bluetooth devices

### SSH Connection Issues
If SSH connection fails:

1. Verify that the Raspberry Pi is running and connected to network
2. Check firewall settings
3. Confirm correct hostname (`levpi`) and username (`lev`)

## License

This project is created for educational purposes as part of pair-programming with 11-year-old Lev.