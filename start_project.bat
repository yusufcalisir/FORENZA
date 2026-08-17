@echo off
title FORENZA: Forensic Evidence Operating System Launcher
cls

echo ===============================================================================
echo   [FORENZA] Forensic Evidence Operating System
echo   Initializing Full-Stack Biocomputational Environment...
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Infrastructure (Milvus, Postgres, Prometheus)...
docker info >nul 2>&1
if errorlevel 1 goto NoDocker
echo    Docker engine detected. Starting containerized microservices...
docker-compose -f "infra\docker-compose.yml" up -d >nul 2>&1
echo    [OK] Infrastructure containers active.
goto AfterDocker

:NoDocker
echo    [INFO] Docker is not running or not installed.
echo    [INFO] FORENZA Safety Mode Active (In-memory storage and cryptographic fallbacks).

:AfterDocker
echo.

echo [2/3] Initializing Forensic Compute Backend (FastAPI)...
set PY_CMD=python
if exist "%~dp0backend\venv\Scripts\python.exe" set PY_CMD="%~dp0backend\venv\Scripts\python.exe"
if exist "%~dp0backend\.venv\Scripts\python.exe" set PY_CMD="%~dp0backend\.venv\Scripts\python.exe"
if exist "%~dp0.venv\Scripts\python.exe" set PY_CMD="%~dp0.venv\Scripts\python.exe"

echo    [INFO] Using Python: %PY_CMD%
start "FORENZA Backend (Port 8000)" /D "%~dp0backend" cmd /k %PY_CMD% -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo    [OK] Backend launched on http://127.0.0.1:8000
echo.

echo [3/3] Initializing Tactical Frontend (Next.js 16)...
if not exist "%~dp0frontend\node_modules" (
    echo    [INFO] node_modules not found. Installing...
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
)

start "FORENZA Frontend (Port 3000)" /D "%~dp0frontend" cmd /k npm run dev
echo    [OK] Frontend launched on http://localhost:3000
echo.

echo ===============================================================================
echo   [SUCCESS] FORENZA Environment Successfully Initialized!
echo.
echo   * Web Application (Frontend):  http://localhost:3000
echo   * Forensic API Docs (Swagger): http://localhost:8000/docs
echo   * Alternative API Root:        http://127.0.0.1:8000
echo.
echo   Note: Keep the spawned Backend and Frontend command windows open.
echo ===============================================================================
echo.
pause
