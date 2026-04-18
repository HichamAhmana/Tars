@echo off
title TARS - Voice PC Assistant
color 0B

echo.
echo  ============================================
echo    T A R S  -  Voice PC Assistant
echo  ============================================
echo.

:: ── Start Django API ─────────────────────────────────────────────────────
echo  [1/2] Starting Django API on http://localhost:8000 ...
start "TARS Django API" cmd /k "cd /d %~dp0 && call venv\Scripts\activate && python manage.py runserver 8000"
timeout /t 2 /nobreak >nul

:: ── Start Next.js Dashboard ───────────────────────────────────────────────
echo  [2/2] Starting Next.js Dashboard on http://localhost:3000 ...
start "TARS Dashboard" cmd /k "cd /d %~dp0dashboard && npm run dev"
timeout /t 3 /nobreak >nul

:: ── Open browser ─────────────────────────────────────────────────────────
echo  Opening dashboard in browser...
start http://localhost:3000

echo.
echo  TARS is starting up!
echo  - Dashboard : http://localhost:3000
echo  - API       : http://localhost:8000/api
echo.
echo  To run the voice engine, open a NEW terminal and run:
echo    cd engine ^&^& python main.py
echo.
pause
