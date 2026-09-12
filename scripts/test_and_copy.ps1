# test_and_copy.ps1
# Runs the camera test on the Pi and copies results back to this PC
# Usage: .\test_and_copy.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Running camera test on Pi ===" -ForegroundColor Cyan
ssh lev@levpi 'cd /home/lev && rm -f camera_test_preview_*.jpg camera_test_screenshot.jpg && python3 camera_smoke_test.py'

Write-Host "`n=== Copying results to local machine ===" -ForegroundColor Cyan

# Create output directory
$outputDir = Join-Path $scriptDir "camera_test_results"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Copy the high-res screenshot
scp lev@levpi:/home/lev/camera_test_screenshot.jpg $outputDir
Write-Host "  Screenshot copied to: $outputDir\camera_test_screenshot.jpg" -ForegroundColor Green

# Copy preview frames
scp lev@levpi:/home/lev/camera_test_preview_*.jpg $outputDir
$previewCount = (Get-ChildItem "$outputDir\camera_test_preview_*.jpg" -ErrorAction SilentlyContinue).Count
Write-Host "  $previewCount preview frames copied to: $outputDir" -ForegroundColor Green

Write-Host "`n=== Done! Open the images in $outputDir ===" -ForegroundColor Green
