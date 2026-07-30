@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo   FaultMate - Instalacion y ejecucion local
echo ============================================
echo.

set VENV_DIR=..\.venv

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro Python instalado.
    echo Descargalo desde https://www.python.org/downloads/ ^(marca "Add to PATH"^)
    pause
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [1/5] Creando entorno virtual...
    python -m venv "%VENV_DIR%"
) else (
    echo [1/5] Entorno virtual ya existe, se omite.
)

echo [2/5] Instalando dependencias ^(puede tardar unos minutos^)...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip >nul
"%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

if not exist ".env" (
    echo [3/5] Creando archivo .env desde plantilla...
    copy .env.example .env >nul
) else (
    echo [3/5] Archivo .env ya existe, se omite.
)

echo [4/5] Aplicando migraciones de base de datos...
"%VENV_DIR%\Scripts\python.exe" manage.py migrate
if errorlevel 1 (
    echo [ERROR] Fallo la migracion de la base de datos.
    pause
    exit /b 1
)

echo [5/5] Creando usuario administrador si no existe...
"%VENV_DIR%\Scripts\python.exe" manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@faultmate.local','admin123')"

echo.
echo ============================================
echo   Todo listo. Iniciando servidor...
echo.
echo   URL:      http://127.0.0.1:8000/
echo   Admin:    http://127.0.0.1:8000/admin/
echo   Usuario:  admin
echo   Password: admin123
echo.
echo   Presiona CTRL+C para detener el servidor.
echo ============================================
echo.

start "" http://127.0.0.1:8000/
"%VENV_DIR%\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

pause
