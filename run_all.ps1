# IndusVision - All-in-One PowerShell Launcher
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "          IndusVision - Industrial Quality Inspector" -ForegroundColor Green
Write-Host "          Final-Year B.Tech Capstone Project Demonstration" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Launching Backend Server (FastAPI on http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\run_backend.ps1"

Write-Host "[2/2] Launching Frontend Server (Vite React on http://127.0.0.1:5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\run_frontend.ps1"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Both servers are running in separate windows:" -ForegroundColor White
Write-Host "   - Backend API:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   - Swagger Docs:   http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "   - Frontend UI:    http://127.0.0.1:5173" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
