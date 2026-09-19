# Labeling Tools

Tools for annotating LEGO Train traffic light data using Label Studio.

## Setup

1. **Configure local file serving** — copy the example env file:
   ```powershell
   copy .env.label-studio.example .env.label-studio
   ```
   Update `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT` if needed (defaults to project root).

2. **Start Label Studio:**
   ```bash
   python tools/labeling/start_label_studio.py
   ```
   Label Studio opens at `http://localhost:8080`.

## Annotation Workflow

### Step 1: Import Data

1. Place your labeled frames in `data/labeled/<run-name>/frames/`
2. Generate task JSON:
   ```bash
   python tools/labeling/generate_tasks.py --dataset-path "data/labeled/LEGO-Train-Traffic-Lights"
   ```
3. In Label Studio: **Data Manager > Import** → upload the generated `tasks_label_studio.json`

### Step 2: Annotate

The annotation config (`label_studio_config.xml`) provides:
- **Rectangle Labels** — draw bounding boxes around traffic lights
- **Choices** — select the phase: Red, Yellow, Green, or Off

### Step 3: Export

Export from Label Studio in COCO or YOLO format for training.

## File Structure

```
labeling/
├── start_label_studio.py         # Launch Label Studio
├── label_studio_config.xml       # Annotation config
├── generate_tasks.py             # Generate task JSON
└── .env.label-studio.example     # Local file storage config template
```
