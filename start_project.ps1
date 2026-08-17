$ErrorActionPreference = "Continue"

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  🧬 FORENZA: Forensic Evidence Operating System" -ForegroundColor Green
Write-Host "  🚀 Initializing Full-Stack Biocomputational Environment..." -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan

$rootDir = $PSScriptRoot
Set-Location "$rootDir"

# 1. Start Infrastructure
Write-Host "`n📦 [1/3] Checking Infrastructure (Milvus, Postgres, Prometheus)..." -ForegroundColor Cyan
$dockerAvailable = $false
try {
    $null = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerAvailable = $true
    }
} catch {
    $dockerAvailable = $false
}

if ($dockerAvailable) {
    Write-Host "   🐳 Docker detected. Starting containerized microservices..." -ForegroundColor Yellow
    docker-compose -f "infra\docker-compose.yml" up -d
    Write-Host "   ✅ Infrastructure containers active." -ForegroundColor Green
} else {
    Write-Host "   ℹ️ Docker not running. FORENZA Safety Mode active (In-memory storage & blockchain fallback)." -ForegroundColor Gray
}

# 2. Start Backend
Write-Host "`n🐍 [2/3] Initializing Forensic Compute Backend (FastAPI)..." -ForegroundColor Cyan
$pythonExe = $null

if (Test-Path "$rootDir\backend\venv\Scripts\python.exe") {
    $pythonExe = "$rootDir\backend\venv\Scripts\python.exe"
} elseif (Test-Path "$rootDir\backend\.venv\Scripts\python.exe") {
    $pythonExe = "$rootDir\backend\.venv\Scripts\python.exe"
} elseif (Test-Path "$rootDir\.venv\Scripts\python.exe") {
    $pythonExe = "$rootDir\.venv\Scripts\python.exe"
} else {
    $pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $pythonExe = "python"
    }
}

if (-not $pythonExe) {
    Write-Host "   ❌ Python executable not found. Please install Python 3.10+." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "   🔍 Using Python: $pythonExe" -ForegroundColor Gray
$backendPath = Join-Path "$rootDir" "backend"

Start-Process -FilePath "powershell.exe" -WorkingDirectory "$backendPath" -ArgumentList "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle = 'FORENZA Backend [Port 8000]'; & '$pythonExe' -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Write-Host "   ✅ Backend running on http://127.0.0.1:8000" -ForegroundColor Green

# 3. Start Frontend
Write-Host "`n⚛️ [3/3] Initializing Tactical Frontend (Next.js 16)..." -ForegroundColor Cyan
$frontendPath = Join-Path "$rootDir" "frontend"
if (-not (Test-Path "$frontendPath\node_modules")) {
    Write-Host "   📦 Installing frontend dependencies (npm install)..." -ForegroundColor Yellow
    Start-Process -FilePath "cmd.exe" -WorkingDirectory "$frontendPath" -ArgumentList "/c", "npm install" -Wait
}

Start-Process -FilePath "powershell.exe" -WorkingDirectory "$frontendPath" -ArgumentList "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle = 'FORENZA Frontend [Port 3000]'; npm run dev"
Write-Host "   ✅ Frontend running on http://localhost:3000" -ForegroundColor Green

Write-Host "`n===============================================================================" -ForegroundColor Cyan
Write-Host "  ✨ FORENZA Environment Successfully Initialized!" -ForegroundColor Green
Write-Host "  🌐 Web Application (Frontend):  http://localhost:3000" -ForegroundColor White
Write-Host "  🧬 Forensic API Docs (Swagger): http://localhost:8000/docs" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan
