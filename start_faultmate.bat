@echo off
setlocal enabledelayedexpansion

REM One-command local startup for FaultMate on Windows.
cd /d "%~dp0\FaultMateWeb"

set "PY_EXE=%~dp0.venv\Scripts\python.exe"

if not exist "%PY_EXE%" (
  echo [FaultMate] Creating virtual environment in .venv...
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -m venv "%~dp0.venv"
  ) else (
    python -m venv "%~dp0.venv"
  )
)

if not exist "%PY_EXE%" (
  echo [FaultMate] ERROR: Could not create .venv. Verify Python is installed.
  exit /b 1
)

echo [FaultMate] Installing dependencies...
"%PY_EXE%" -m pip install --upgrade pip
"%PY_EXE%" -m pip install -r requirements.txt

if not exist ".env" (
  echo [FaultMate] Creating .env template...
  (
    echo GEMINI_API_KEY=
    echo DEBUG=True
    echo ALLOWED_HOSTS=127.0.0.1,localhost
  ) > ".env"
)

echo [FaultMate] Applying migrations...
"%PY_EXE%" manage.py migrate

echo [FaultMate] Starting server at http://127.0.0.1:8000/
echo [FaultMate] Press Ctrl+C to stop.
"%PY_EXE%" manage.py runserver 127.0.0.1:8000
