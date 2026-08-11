@echo off
chcp 65001 >nul
echo 🚀 FORENZA: Starting Development Environment...

rem Ensure we are in the project root
cd /d "%~dp0"

rem 1. Start Infrastructure
echo 📦 [1/3] Starting Infrastructure...

rem Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo 🐳 Docker is not running. Attempting to start Docker Desktop...
    
    rem Try standard installation paths
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) else (
        echo ❌ Could not find Docker Desktop.exe. Please start it manually.
        pause
        exit /b 1
    )
    
    echo ⏳ Waiting for Docker to initialize...
    :WaitForDocker
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⏳ Still waiting for Docker engine...
        goto WaitForDocker
    )
    echo ✅ Docker is up and running!
)

docker-compose -f "infra\docker-compose.yml" up -d
if %errorlevel% neq 0 (
    echo ❌ Docker failed. Ensure Docker Desktop is running.
    exit /b %errorlevel%
)
echo ✅ Infrastructure running.

rem 2. Start Backend
echo 🐍 [2/3] Starting Backend...

rem Check/Install Dependencies
echo 🔍 Checking Python dependencies...
start /b /wait "" "backend\venv\Scripts\python.exe" -c "import pydantic_settings" 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installing missing dependencies...
    start /b /wait "" "backend\venv\Scripts\pip.exe" install -r backend\requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed.
) else (
    echo ✅ Dependencies already installed.
)

rem Use the venv python executable explicitly to ensure we use the installed dependencies
start "FORENZA-Backend" /D "%~dp0backend" cmd /k "venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✅ Backend started.

rem 3. Start Frontend
echo ⚛️ [3/3] Starting Frontend...
start "FORENZA-Frontend" /D "%~dp0frontend" cmd /k "npm run dev"
echo ✅ Frontend started.

echo ✨ FORENZA is now running!
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000/docs
pause
