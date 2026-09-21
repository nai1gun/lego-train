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
- **`label_studio_config.xml`** — Annotation config for traffic light phase classification. Paste into Label Studio's config editor when creating a new project (no XML import button exists — copy-paste is the workflow).
- **`generate_tasks.py`** — Generates Label Studio task JSON from curated frames (**optional** — you can also import frames directly via Label Studio's Directory import).

**Quick start (auto-generated tasks):**
```powershell
# 1. Manually copy selected runs into data/curated/<run-name>/
#    (from data/captured/raw/ or wherever your raw frames live)

# 2. Generate tasks from curated data
python tools\labeling\generate_tasks.py --dataset-path "data\curated\LEGO-Train-Traffic-Lights"

# 3. Start Label Studio and import the generated JSON
python tools\labeling\start_label_studio.py
```

**Or skip task generation** — use Label Studio's **Data Import → Directory** option to point directly at `data/curated/<run-name>/frames/`. No script needed for single runs.

> **Note:** `data/curated/` is the staging area for frames *before* labeling. Curation (copying frames here) is manual, but task generation is automatic via `generate_tasks.py`. For simple single-run projects you can skip it entirely and use Label Studio's Directory import instead.

### 3. HuggingFace Upload (`hf_upload/`)

Scripts for uploading and downloading datasets to/from Hugging Face Hub.

- **`upload_dataset.py`** — Uploads annotated data from `data/curated/` to Hugging Face.
- **`download_dataset.py`** — Downloads a dataset from Hugging Face to `data/labeled/` for labeling.
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
├── curated/          # Selected runs ready for labeling (manual copy)
└── labeled/          # Post-annotation datasets (from HF download or export)
```

| Directory | Purpose | When populated |
|---|---|---|
| `data/captured/raw/` | Raw camera data from Pi | After `scp` from Pi |
| `data/curated/<run>/` | Frames selected for annotation | **Manual** — copy from captured/raw/ |
| `data/labeled/<dataset>/` | Post-annotation data → HF | After Label Studio export |
