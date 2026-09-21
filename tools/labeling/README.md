# Labeling Tools

Tools for annotating LEGO Train traffic light data using Label Studio.

## Setup

1. **Start Label Studio:**
   ```bash
   python tools/labeling/start_label_studio.py
   ```
   Label Studio opens at `http://localhost:8080`.

## Annotation Workflow

> **Before you start:** Your camera data must be collected from the Raspberry Pi and copied to `data/captured/raw/` on your dev machine. See [tools/data_collection/](../data_collection/) for the capture scripts. Once you have raw runs, select the frames you want to annotate and copy them into `data/curated/<run-name>/`.

### Step 1: Prepare Data (Manual)

Before generating tasks, you need to place the frames you want to annotate into `data/curated/<run-name>/frames/`:

1. Copy your selected runs from `data/captured/raw/` into `data/curated/<run-name>/`
2. Each run should have a `frames/` subdirectory containing the JPEG images
3. Optionally include a `frames.csv` metadata file alongside the `frames/` directory

```
data/curated/
└── my-run-name/
    ├── frames/
    │   ├── frame_000000.jpg
    │   ├── frame_000001.jpg
    │   └── ...
    └── frames.csv          # optional: camera metadata per frame
```

### Step 2: Set Up the Label Studio Project

Create a new project in Label Studio and paste the annotation config:

1. **Create a new project** — go to Projects → New Project
2. **Paste the config XML** — in the "Configuration" tab, switch to the code editor (`</>` icon) and paste the contents of [`label_studio_config.xml`](./label_studio_config.xml) directly into the config editor. There's no file import option for configs — copy-paste is the intended workflow.

### Step 3: Import Your Data (Two Options)

#### Option A: Auto-generated tasks (recommended for multi-run projects)

Use `generate_tasks.py` to create a task JSON from your curated frames, then upload it:

```bash
python tools/labeling/generate_tasks.py --dataset-path "data/curated/my-run-name"
```

Then in Label Studio: **Data Manager > Import** → upload the generated `tasks_label_studio.json`.

This approach supports frame sampling (`--frame-interval`) and limiting total frames (`--max-frames`). Use it when you want more control (e.g. skipping every Nth frame, or injecting camera metadata from `frames.csv`).

#### Option B: Manual task setup (no script needed)

If you'd rather skip `generate_tasks.py`, set up your data source directly in Label Studio:

1. In Label Studio, go to **Data Import**
2. Change the source type to **"Directory"**
3. Set the path to your curated folder, e.g. `data/curated/my-run-name/frames/`
4. Label Studio will read all images from that folder as individual tasks

> This is simpler for a single run of frames. Use Option A when you need frame sampling or want to combine multiple runs in one project.

### Common Setup Step (Both Options)

After importing your data source, set up local file serving so Label Studio can read the images:

1. Go to **Settings > Cloud Storage > Add Source Storage > Local Files**
2. Set the path to: `data/curated` (relative to your project root)

> This is a **Source Storage**, not a Target Storage. It tells Label Studio where to **read** the unlabelled images from. Annotations are stored in Label Studio's database and exported as JSON separately — no Target Storage needed.

### Step 4: Annotate

The annotation config (`label_studio_config.xml`) provides:
- **Rectangle Labels** — draw bounding boxes around traffic lights
- **Choices** — select the phase: Red, Yellow, Green, or Off

### Step 5: Export Annotations

Export from Label Studio in COCO or YOLO format for training.

## File Structure

```
labeling/
├── start_label_studio.py    # Launch Label Studio
├── label_studio_config.xml  # Annotation config
└── generate_tasks.py        # Generate task JSON
```
