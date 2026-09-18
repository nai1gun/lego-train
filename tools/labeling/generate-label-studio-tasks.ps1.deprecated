# Generate Label Studio Task JSON from LEGO Train Dataset
# This script creates task files from your downloaded Hugging Face dataset
# so you can import them directly into Label Studio

param(
    [string]$DatasetPath = "",
    [string]$OutputPath = "",
    [int]$FrameInterval = 10,
    [int]$MaxFrames = 50
)

# Set default paths if not provided
$scriptDir = $PSScriptRoot
$projectRoot = Split-Path $scriptDir -Parent  # tools/
if (-not $DatasetPath) {
    $DatasetPath = Join-Path $projectRoot "..\data\labeled"
}
if (-not $OutputPath) {
    $OutputPath = Join-Path $scriptDir "tasks_label_studio.json"
}

Write-Host "Generating Label Studio tasks..." -ForegroundColor Cyan
Write-Host "Dataset path: $DatasetPath" -ForegroundColor Gray
Write-Host "Output path: $OutputPath" -ForegroundColor Gray
Write-Host "Frame interval: every $FrameInterval frames" -ForegroundColor Gray
Write-Host "Max frames: $MaxFrames" -ForegroundColor Gray

# Check if dataset exists
if (-not (Test-Path $DatasetPath)) {
    Write-Host "`nError: Dataset not found at $DatasetPath" -ForegroundColor Red
    Write-Host "Please download the dataset first: .\download-dataset.ps1" -ForegroundColor Yellow
    exit 1
}

# Read frames.csv metadata
$framesCsvPath = Join-Path $DatasetPath "frames.csv"
if (Test-Path $framesCsvPath) {
    Write-Host "`nReading frames.csv metadata..." -ForegroundColor Gray
    $framesMetadata = Import-Csv $framesCsvPath
    Write-Host "Found $($framesMetadata.Count) frames in metadata" -ForegroundColor Gray
} else {
    Write-Host "`nWarning: frames.csv not found. Will use frame directory." -ForegroundColor Yellow
    $framesMetadata = $null
}

# Get frame files
$framesDir = Join-Path $DatasetPath "frames"
if (Test-Path $framesDir) {
    $frameFiles = Get-ChildItem $framesDir -Filter "*.jpg" | Sort-Object Name
    Write-Host "Found $($frameFiles.Count) frame images" -ForegroundColor Gray
} else {
    Write-Host "`nError: frames directory not found at $framesDir" -ForegroundColor Red
    exit 1
}

# Generate tasks
$tasks = @()
$frameCount = 0
$taskIndex = 0

foreach ($frame in $frameFiles) {
    if ($frameCount -ge $MaxFrames) {
        break
    }
    
    if ($frameCount % $FrameInterval -ne 0 -and $frameCount -ne 0) {
        $frameCount++
        continue
    }
    
    # Extract frame number from filename (frame_000000.jpg -> 0)
    $frameNum = [int]($frame.BaseName -replace "frame_", "")
    
    # Build Label Studio local file path
    # Format: /data/local-files/?d=data/labeled/frames/frame_000000.jpg
    $datasetName = [System.IO.Path]::GetFileName($DatasetPath.TrimEnd('\',' '))
    $localPath = "data/labeled/$datasetName/frames/$($frame.Name)"
    
    $task = [PSCustomObject]@{
        id = $taskIndex + 1
        predictions = @()
        annotations = @()
        file_upload = $null
        data = @{
            image = "/data/local-files/?d=$localPath"
            frames_csv = "/data/local-files/?d=data/labeled/$datasetName/frames.csv"
            frame_idx = $frameNum
            session = $datasetName
        }
        meta = @{
            frame_number = $frameNum
            filename = $frame.Name
            total_frames = $frameFiles.Count
        }
    }
    
    # Add metadata from frames.csv if available
    if ($framesMetadata -and $frameCount -lt $framesMetadata.Count) {
        $meta = $framesMetadata[$frameCount]
        $task.meta | Add-Member -MemberType NoteProperty -Name "timestamp" -Value $meta.wall_timestamp
        $task.meta | Add-Member -MemberType NoteProperty -Name "exposure_us" -Value $meta.exposure_us
        $task.meta | Add-Member -MemberType NoteProperty -Name "analogue_gain" -Value $meta.analogue_gain
    }
    
    $tasks += $task
    $frameCount++
    $taskIndex++
    
    Write-Progress -Activity "Generating tasks" -Status "Processing frame $($frame.Name)" -PercentComplete (($frameCount / $MaxFrames) * 100)
}

# Convert to JSON and save
$jsonOutput = $tasks | ConvertTo-Json -Depth 10

# Write to file with UTF-8 encoding
[System.IO.File]::WriteAllText($OutputPath, $jsonOutput, [System.Text.UTF8]::new())

Write-Progress -Activity "Generating tasks" -Completed

Write-Host "`nSuccessfully generated $($tasks.Count) tasks!" -ForegroundColor Green
Write-Host "Saved to: $OutputPath" -ForegroundColor Green
Write-Host "`nTo import into Label Studio:" -ForegroundColor Cyan
Write-Host "1. Start Label Studio: .\start-label-studio.bat" -ForegroundColor White
Write-Host "2. Create a new project or open existing one" -ForegroundColor White
Write-Host "3. Go to Data Manager > Import" -ForegroundColor White
Write-Host "4. Upload the file: $OutputPath" -ForegroundColor White
Write-Host "5. Set up local storage: Settings > Cloud Storage > Add Target Storage > Local Files" -ForegroundColor White
Write-Host "6. Set path to: /data/labeled" -ForegroundColor White
