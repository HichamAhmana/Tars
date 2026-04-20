@echo off
rem Start TARS v2: Django backend + dashboard + engine (Windows).
rem Requires the virtualenv at .\.venv and dashboard\node_modules.

pushd "%~dp0"

if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
if exist .env for /f "usebackq tokens=* delims=" %%A in (".env") do set "%%A"

python manage.py migrate --noinput

set "BACKEND_PORT=%TARS_BACKEND_PORT%"
if "%BACKEND_PORT%"==""    set "BACKEND_PORT=8000"
set "DASHBOARD_PORT=%TARS_DASHBOARD_PORT%"
if "%DASHBOARD_PORT%"=="" set "DASHBOARD_PORT=3000"

echo Starting Django ASGI (daphne) on :%BACKEND_PORT%
start "tars-backend" daphne -b 0.0.0.0 -p %BACKEND_PORT% backend.asgi:application

echo Starting Next.js dashboard on :%DASHBOARD_PORT%
start "tars-dashboard" cmd /c "cd dashboard && npm run dev -- -p %DASHBOARD_PORT%"

echo Starting TARS engine
python manage.py run_engine

popd
