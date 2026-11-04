# IndusVision - Backend PowerShell Launcher
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Starting IndusVision FastAPI Backend Server on port 8000..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\backend"

# Automatically free port 8000 if occupied by a stale/orphaned process
$staleConnections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($staleConnections) {
    $staleConnections | ForEach-Object {
        Write-Host "Freeing port 8000 from lingering process PID $($_.OwningProcess)..." -ForegroundColor Yellow
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}

if (Test-Path "$PSScriptRoot\backend\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating .venv virtual environment..." -ForegroundColor Yellow
    & "$PSScriptRoot\backend\.venv\Scripts\Activate.ps1"
} elseif (Test-Path "$PSScriptRoot\backend\venv\Scripts\Activate.ps1") {
    Write-Host "Activating venv virtual environment..." -ForegroundColor Yellow
    & "$PSScriptRoot\backend\venv\Scripts\Activate.ps1"
}

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
