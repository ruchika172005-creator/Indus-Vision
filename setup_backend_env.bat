@echo off
title IndusVision - Backend Virtual Environment Setup
echo ============================================================
echo   IndusVision - Backend Virtual Environment Setup
echo ============================================================
echo.
cd /d "%~dp0backend"

echo [1/3] Creating virtual environment (.venv)...
python -m venv .venv

echo [2/3] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/3] Upgrading pip and installing requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ============================================================
echo  Virtual Environment Setup Complete!
echo  You can now run 'run_backend.bat' to start the server.
echo ============================================================
echo.
pause
