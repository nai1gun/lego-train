# Data Pipeline Tools

This directory contains all tools for the LEGO Train data pipeline: collecting, labeling, and uploading datasets.

## Pipeline Overview

```
Collection → Curate → Label → Upload
```

### 1. Data Collection (`data_collection/`)

Scripts for capturing video and frames from the train-mounted camera on the Raspberry Pi.

- **`collect_data.py`** — Records per-frame JPEGs + H.264 video with camera metadata (AE/AWB/AF lock).
  - Run on Pi: `python3 tools/data_collection/collect_data.py --duration 60 --run "inner curve, speed 40%"`
  - Output goes to `runs/` on the Pi; scp to `data/captured/raw/` on your dev machine.

### 2. Labeling (`labeling/`)

Tools for setting up and running data annotation with Label Studio.

- **`start_label_studio.py`** — Launches Label Studio with local file serving enabled.
- **`label_studio_config.xml`** — Annotation config for traffic light phase classification.
- **`generate_tasks.py`** — Generates Label Studio task JSON from labeled data.

**Usage:**
```powershell
# Start Label Studio
python tools\labeling\start_label_studio.py

# Generate tasks from labeled data
python tools\labeling\generate_tasks.py --dataset-path "data\labeled\LEGO-Train-Traffic-Lights"
```

### 3. HuggingFace Upload (`hf_upload/`)

Scripts for uploading and downloading datasets to/from Hugging Face Hub.

- **`upload_dataset.py`** — Uploads `data/curated/` to Hugging Face.
- **`download-dataset.ps1`** — Downloads a dataset from Hugging Face to `data/labeled/`.
- **`example_load_dataset.py`** — Example of how to load and explore the dataset.

**Usage:**
```powershell
# Upload curated data to Hugging Face
python tools\hf_upload\upload_dataset.py upload --dataset-name lev/lego-train-datasets

# Download dataset for labeling
.\tools\hf_upload\download-dataset.ps1
```

## Data Directory Structure

```
data/
├── captured/
│   └── raw/          # Raw video runs from Pi (scp from runs/)
├── curated/          # Curated/filtered runs ready for labeling
└── labeled/          # Labeled datasets (ready for HF upload)
```
