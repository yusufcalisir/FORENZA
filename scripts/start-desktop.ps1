# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# One-Click Desktop Workstation Launcher (Windows PowerShell)
# ==============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$DesktopDir = Join-Path $RootDir "desktop"
$FrontendDir = Join-Path $RootDir "frontend"

Clear-Host
Write-Host @"
  ███████╗ ██████╗ ██████╗ ███████╗███╗   ██╗███████╗ █████╗ 
  ██╔════╝██╔═══██╗██╔══██╗██╔════╝████╗  ██║╚══███╔╝██╔══██╗
  █████╗  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║  ███╔╝ ███████║
  ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██║╚██╗██║ ███╔╝  ██╔══██║
  ██║     ╚██████╔╝██║  ██║███████╗██║ ╚████║███████╗██║  ██║
  ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
"@ -ForegroundColor Magenta

Write-Host "  FORENZA Native Forensic Desktop Workstation" -ForegroundColor Cyan
Write-Host "  ISO/IEC 17025:2017 Aligned • Standalone Desktop Process Engine"
Write-Host "  ──────────────────────────────────────────────────────────────────────────`n"

# 1. Prerequisite Validation
Write-Host "[1/3] Checking Node.js and Python Runtime..." -ForegroundColor Cyan
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js is required but not found in PATH." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python 3.12+ is required but not found in PATH." -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Node $(node --version) and Python detected.`n" -ForegroundColor Green

# 2. Check Desktop Node Dependencies
Write-Host "[2/3] Verifying Desktop Dependencies..." -ForegroundColor Cyan
if (-not (Test-Path (Join-Path $DesktopDir "node_modules"))) {
    Write-Host "  Installing desktop Electron wrapper dependencies (one-time)..." -ForegroundColor Yellow
    Set-Location $DesktopDir
    & npm install --prefer-offline --no-audit
}
Write-Host "  ✓ Desktop dependencies ready.`n" -ForegroundColor Green

# 3. Launch Frontend and Desktop App
Write-Host "[3/3] Launching FORENZA Forensic Desktop Environment..." -ForegroundColor Cyan

# Start Frontend Dev Server in background job if port 3000 is not listening
$frontendNeeded = $true
try {
    $conn = Test-NetConnection -ComputerName 127.0.0.1 -Port 3000 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($conn) { $frontendNeeded = $false }
} catch {}

if ($frontendNeeded) {
    Write-Host "  Starting local Next.js rendering engine..." -ForegroundColor Yellow
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        & npm run dev
    } -ArgumentList $FrontendDir
}

# Launch Electron Workstation
Write-Host "  Starting native Electron window with Python FastAPI sidecar..." -ForegroundColor Green
Set-Location $DesktopDir
& npx electron .

Write-Host "`nFORENZA Desktop session ended cleanly." -ForegroundColor Gray
