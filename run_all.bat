@echo off
title IndusVision - Launcher
echo =====================================================================
echo           IndusVision - Industrial Quality Inspector
echo           Final-Year B.Tech Capstone Project Demonstration
echo =====================================================================
echo.
echo [1/2] Launching Backend Server (FastAPI on http://127.0.0.1:8000)...
start "IndusVision - Backend (Port 8000)" cmd /k ""%~dp0run_backend.bat""

echo [2/2] Launching Frontend Server (Vite React on http://127.0.0.1:5173)...
start "IndusVision - Frontend (Port 5173)" cmd /k ""%~dp0run_frontend.bat""

echo.
echo =====================================================================
echo Both servers are starting up in separate terminal windows:
echo   - Backend API:    http://127.0.0.1:8000
echo   - Swagger Docs:   http://127.0.0.1:8000/docs
echo   - Frontend UI:    http://127.0.0.1:5173
echo =====================================================================
echo.
pause
