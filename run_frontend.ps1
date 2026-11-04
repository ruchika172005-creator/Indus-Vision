# IndusVision - Frontend PowerShell Launcher
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Starting IndusVision React / Vite Frontend on port 5173..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\frontend"
npm run dev
