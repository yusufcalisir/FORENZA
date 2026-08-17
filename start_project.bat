@echo off
chcp 65001 >nul
title FORENZA: Forensic Evidence Operating System Launcher
cls

echo ===============================================================================
echo   🧬 FORENZA: Forensic Evidence Operating System
echo   🚀 Initializing Full-Stack Biocomputational Environment...
echo ===============================================================================
echo.

rem Ensure we are in the project root directory
cd /d "%~dp0"

rem ─────────────────────────────────────────────────────────────────────────────
rem [STEP 1/3] INFRASTRUCTURE (Docker Compose / Safety Mode)
rem ─────────────────────────────────────────────────────────────────────────────
echo 📦 [1/3] Checking Infrastructure (Milvus, Postgres, Prometheus)...

docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo    🐳 Docker engine detected. Starting containerized microservices...
    docker-compose -f "infra\docker-compose.yml" up -d >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ Containerized infrastructure running (Milvus :19530, Postgres :5432, Grafana :3001).
    ) else (
        echo    ⚠️ Docker compose warning. Proceeding in Safety Mode.
    )
) else (
    echo    ℹ️ Docker is not running or not installed.
    echo    🛡️ FORENZA Safety Mode Active (In-memory storage & cryptographic fallbacks enabled).
)
echo.

rem ─────────────────────────────────────────────────────────────────────────────
rem [STEP 2/3] BACKEND SERVICE (FastAPI & Forensic Compute Engine)
rem ─────────────────────────────────────────────────────────────────────────────
echo 🐍 [2/3] Initializing Forensic Compute Backend (FastAPI)...

set "PYTHON_EXE="

if exist "backend\venv\Scripts\python.exe" (
    set "PYTHON_EXE=backend\venv\Scripts\python.exe"
) else if exist "backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=backend\.venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    )
)

if "%PYTHON_EXE%"=="" (
    echo    ❌ Python not found on system PATH. Please install Python 3.10+ and re-run.
    pause
    exit /b 1
)

echo    🔍 Using Python executable: %PYTHON_EXE%

rem Verify essential packages
"%PYTHON_EXE%" -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if %errorlevel% neq 0 (
    echo    📦 Installing required Python dependencies from requirements.txt...
    "%PYTHON_EXE%" -m pip install -r backend\requirements.txt
    if %errorlevel% neq 0 (
        echo    ❌ Failed to install Python dependencies.
        pause
        exit /b 1
    )
    echo    ✅ Dependencies installed successfully.
) else (
    echo    ✅ Python dependencies verified.
)

rem Launch backend server in separate titled window
start "FORENZA-Backend [Port 8000]" /D "%~dp0backend" cmd /k "%PYTHON_EXE% -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo    ✅ Backend launched on http://127.0.0.1:8000
echo.

rem ─────────────────────────────────────────────────────────────────────────────
rem [STEP 3/3] FRONTEND SERVICE (Next.js 16 App Router)
rem ─────────────────────────────────────────────────────────────────────────────
echo ⚛️ [3/3] Initializing Tactical Frontend (Next.js 16)...

if not exist "frontend\node_modules\" (
    echo    📦 node_modules not detected. Running npm install in frontend...
    start /b /wait "" cmd /c "cd /d "%~dp0frontend" && npm install"
    if %errorlevel% neq 0 (
        echo    ❌ Failed to run npm install in frontend.
        pause
        exit /b 1
    )
    echo    ✅ Frontend dependencies installed.
)

rem Launch frontend server in separate titled window
start "FORENZA-Frontend [Port 3000]" /D "%~dp0frontend" cmd /k "npm run dev"
echo    ✅ Frontend launched on http://localhost:3000
echo.

rem ─────────────────────────────────────────────────────────────────────────────
rem LAUNCH SUMMARY
rem ─────────────────────────────────────────────────────────────────────────────
echo ===============================================================================
echo   ✨ FORENZA Environment Successfully Initialized!
echo.
echo   🌐 Web Application (Frontend):  http://localhost:3000
echo   🧬 Forensic API Docs (Swagger): http://localhost:8000/docs
echo   📊 Alternative API Endpoint:   http://127.0.0.1:8000
echo.
echo   [Tip] Keep the spawned Backend and Frontend terminal windows open.
echo ===============================================================================
echo.
pause
