@echo off
title IndusVision - Backend Service
echo ============================================================
echo Starting IndusVision FastAPI Backend Server on port 8000...
echo ============================================================
cd /d "%~dp0backend"

:: Automatically free port 8000 if occupied by a stale/orphaned process
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Freeing port 8000 from lingering process PID %%a...
    taskkill /f /pid %%a >nul 2>&1
)

:: Auto-detect and activate virtual environment if present
if exist ".venv\Scripts\activate.bat" (
    echo Activating .venv virtual environment...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo Activating venv virtual environment...
    call venv\Scripts\activate.bat
)

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
