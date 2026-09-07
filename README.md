# Autonomous LEGO Train Project

This project implements an autonomous LEGO train using Raspberry Pi, camera vision, and Bluetooth controls.

## Project Structure

```
.
├── bluetooth_controller.py     # Bluetooth controller for LEGO motors
├── ip_finder.py                # Tool to find Raspberry Pi IP address
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
pip install bleak pybluez
```

### 3. Connect to Raspberry Pi

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