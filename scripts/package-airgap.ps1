# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# Offline Air-Gap Distribution Packager (Windows PowerShell)
# ==============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$DistDir = Join-Path $RootDir "dist"
$PkgVersion = "2.0.0"
$PkgName = "forenza-airgap-v$PkgVersion"
$PkgWorkDir = Join-Path $DistDir $PkgName

Clear-Host
Write-Host "=== FORENZA Air-Gap Distribution Packager (Windows) ===" -ForegroundColor Cyan
Write-Host "Building full standalone offline bundle for USB / air-gapped installation...`n"

if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
}
if (Test-Path $PkgWorkDir) {
    Remove-Item -Path $PkgWorkDir -Recurse -Force | Out-Null
}

New-Item -ItemType Directory -Path (Join-Path $PkgWorkDir "infra\airgap") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PkgWorkDir "scripts") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PkgWorkDir "docs") -Force | Out-Null

# 1. Pull Base Images
Write-Host "[1/4] Pulling Base Images..." -ForegroundColor Cyan
docker pull nginx:1.25-alpine
docker pull postgres:16-alpine
docker pull redis:7-alpine

# 2. Build Production Images
Write-Host "[2/4] Building FORENZA Microservices & Workstation Images..." -ForegroundColor Cyan
docker build -t forenza-backend:latest -f "$RootDir\backend\Dockerfile" "$RootDir"
docker build -t forenza-frontend:latest -f "$RootDir\frontend\Dockerfile" "$RootDir\frontend"

# 3. Export to Tarball
Write-Host "[3/4] Exporting Container Images to Tarball..." -ForegroundColor Cyan
$tarPath = Join-Path $PkgWorkDir "forenza-airgap-images.tar"

docker save -o $tarPath `
    forenza-backend:latest `
    forenza-frontend:latest `
    nginx:1.25-alpine `
    postgres:16-alpine `
    redis:7-alpine

Write-Host "  * Exported container images to $tarPath" -ForegroundColor Green

# 4. Assemble Offline Package
Write-Host "[4/4] Assembling Distribution Archive..." -ForegroundColor Cyan
Copy-Item -Path "$RootDir\infra\airgap\*" -Destination (Join-Path $PkgWorkDir "infra\airgap") -Recurse -Force
Copy-Item -Path "$RootDir\scripts\start-airgap.ps1" -Destination (Join-Path $PkgWorkDir "scripts") -Force
Copy-Item -Path "$RootDir\scripts\start-airgap.sh" -Destination (Join-Path $PkgWorkDir "scripts") -Force
Copy-Item -Path "$RootDir\scripts\start-airgap.bat" -Destination $PkgWorkDir -Force
Copy-Item -Path "$RootDir\docs\airgap-deployment-guide.md" -Destination (Join-Path $PkgWorkDir "docs") -Force

# Create ZIP archive
$zipPath = Join-Path $DistDir "$PkgName.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Compress-Archive -Path "$PkgWorkDir\*" -DestinationPath $zipPath -CompressionLevel Optimal

# Compute SHA-256 Checksum
$sha256 = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "  [OK] Air-Gapped Windows ZIP Package Created Successfully!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  Distribution Archive: $zipPath" -ForegroundColor White
Write-Host "  SHA-256 Checksum:     $sha256" -ForegroundColor Cyan
Write-Host "`n  Air-Gap Deployment Instructions:" -ForegroundColor White
Write-Host "  1. Copy $PkgName.zip to an approved forensic USB drive."
Write-Host "  2. Extract on the air-gapped workstation."
Write-Host "  3. Double-click start-airgap.bat to launch.`n"
