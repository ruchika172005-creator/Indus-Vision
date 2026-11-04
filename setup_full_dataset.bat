@echo off
title IndusVision - Complete Dataset Setup
echo ============================================================
echo   Installing Complete Industrial Defect Dataset
echo ============================================================
echo.
cd /d "%~dp0backend"

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python scripts\setup_full_dataset.py
echo.
pause

