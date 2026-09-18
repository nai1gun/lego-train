# HuggingFace Upload Tools

Scripts for managing LEGO Train datasets on Hugging Face Hub.

## Setup

1. **Get a Hugging Face token** at https://huggingface.co/settings/tokens
2. **Set the token** as an environment variable:
   ```powershell
   $env:HF_TOKEN = "your_token_here"
   ```
   Or permanently:
   ```powershell
   setx HF_TOKEN "your_token_here"
   ```

## Usage

### Upload Dataset

Uploads from `data/curated/` by default:

```powershell
python tools\hf_upload\upload_dataset.py upload --dataset-name lev/lego-train-datasets
```

### Download Dataset

Downloads to `data/labeled/`:

```powershell
.\tools\hf_upload\download-dataset.ps1
```

### List Datasets

```powershell
python tools\hf_upload\upload_dataset.py list
```

### Explore Dataset (Example)

```powershell
python tools\hf_upload\example_load_dataset.py
```

## File Structure

```
hf_upload/
├── upload_dataset.py            # Upload to Hugging Face
├── download-dataset.ps1         # Download from Hugging Face
└── example_load_dataset.py      # Dataset exploration example
```