# Autonomous LEGO Train Project

This project implements an autonomous LEGO train using Raspberry Pi, camera vision, and Bluetooth controls.

## Project Structure

```
.
├── bluetooth_controller.py     # Bluetooth controller for LEGO motors
├── camera_test.py              # Camera smoke test script
├── README.md                   # This file
└── .clinerules                 # Project documentation and guidelines
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
```

### 3. Camera Setup

Before using the camera, make sure:
1. The Pi Camera Module is properly connected to the CSI port
2. Camera is enabled on Raspberry Pi (`raspi-config` → Interface Options → Camera)

#### Test the Camera

Run the camera smoke test to verify everything works:

```bash
# On Windows (development host)
python camera_test.py

# On Raspberry Pi (via SSH)
ssh lev@levpi
cd ~/lego-train
source .venv/bin/activate
python camera_test.py
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

The `bluetooth_controller.py` script provides:

1. **Device Discovery**: Automatically scans for LEGO devices
2. **Connection Management**: Establishes connection to LEGO motors
3. **Command Interface**: Sends commands like forward, backward, and stop

### Usage

```bash
python bluetooth_controller.py
```

## Project Components

- `bluetooth_controller.py`: Main Bluetooth controller with device discovery and command sending
- `camera_test.py`: Camera smoke test - verifies camera is working correctly
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