# Download LEGO Train Dataset from Hugging Face
# This script downloads your dataset to the local data/labeled/ folder
# so you can use it with Label Studio's local file storage

Write-Host "Downloading LEGO-Train-Traffic-Lights dataset..." -ForegroundColor Cyan

# Create download directory in data/labeled/
$projectRoot = Split-Path $PSScriptRoot -Parent  # tools/
$downloadDir = Join-Path $projectRoot "..\data\labeled\LEGO-Train-Traffic-Lights"
if (!(Test-Path $downloadDir)) {
    New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null
    Write-Host "Created directory: $downloadDir" -ForegroundColor Green
}

# Download using huggingface-cli (requires: pip install huggingface_hub)
$huggingfaceCmd = "huggingface-cli download nai1gun/LEGO-Train-Traffic-Lights --local-dir $downloadDir"
Write-Host "Running: $huggingfaceCmd" -ForegroundColor Yellow

try {
    & cmd /c $huggingfaceCmd
    Write-Host "`nDownload complete!" -ForegroundColor Green
    Write-Host "Files are in: $downloadDir" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Start Label Studio: .\..\labeling\start-label-studio.bat" -ForegroundColor White
    Write-Host "2. In Label Studio: Settings > Cloud Storage > Add Target Storage" -ForegroundColor White
    Write-Host "3. Select 'Local Files' and set path to: /data/labeled" -ForegroundColor White
}
catch {
    Write-Host "`nError downloading dataset. Make sure huggingface_hub is installed:" -ForegroundColor Red
    Write-Host "  pip install huggingface_hub" -ForegroundColor Yellow
    Write-Host "`nAlternative: Download manually from https://huggingface.co/datasets/nai1gun/LEGO-Train-Traffic-Lights" -ForegroundColor Yellow
}
