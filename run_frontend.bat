@echo off
title IndusVision - Frontend Service
echo ============================================================
echo Starting IndusVision React / Vite Frontend on port 5173...
echo ============================================================
cd /d "%~dp0frontend"
npm run dev
pause
