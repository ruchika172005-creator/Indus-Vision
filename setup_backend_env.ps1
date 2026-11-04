# IndusVision - Backend Virtual Environment Setup (PowerShell)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   IndusVision - Backend Virtual Environment Setup" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "$PSScriptRoot\backend"

Write-Host "[1/3] Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
python -m venv .venv

Write-Host "[2/3] Activating virtual environment..." -ForegroundColor Yellow
& "$PSScriptRoot\backend\.venv\Scripts\Activate.ps1"

Write-Host "[3/3] Upgrading pip and installing requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Virtual Environment Setup Complete!" -ForegroundColor Green
Write-Host " You can now run 'run_backend.ps1' or 'run_all.ps1'." -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
