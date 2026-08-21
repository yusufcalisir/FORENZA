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

Write-Host "========================================================================" -ForegroundColor Magenta
Write-Host "              FORENZA NATIVE FORENSIC DESKTOP WORKSTATION               " -ForegroundColor Cyan
Write-Host "     ISO/IEC 17025:2017 Aligned - Standalone Desktop Process Engine     " -ForegroundColor Gray
Write-Host "========================================================================`n" -ForegroundColor Magenta

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
$nodeVer = node --version
Write-Host "  * Node.js $nodeVer and Python detected.`n" -ForegroundColor Green

# 2. Check Desktop Node Dependencies
Write-Host "[2/3] Verifying Desktop Dependencies..." -ForegroundColor Cyan
if (-not (Test-Path (Join-Path $DesktopDir "node_modules"))) {
    Write-Host "  Installing desktop Electron wrapper dependencies..." -ForegroundColor Yellow
    Set-Location $DesktopDir
    & npm install --prefer-offline --no-audit
}
Write-Host "  * Desktop dependencies verified.`n" -ForegroundColor Green

# 3. Launch Frontend and Desktop App
Write-Host "[3/3] Launching FORENZA Forensic Desktop Environment..." -ForegroundColor Cyan

# Start Frontend Dev Server in background job if port 3000 is not already active
$frontendNeeded = $true
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $iar = $tcp.BeginConnect("127.0.0.1", 3000, $null, $null)
    $success = $iar.AsyncWaitHandle.WaitOne(800)
    if ($success) {
        $tcp.EndConnect($iar)
        $frontendNeeded = $false
    }
    $tcp.Close()
} catch {
    $frontendNeeded = $true
}

$frontendJob = $null
if ($frontendNeeded) {
    Write-Host "  Starting local Next.js rendering engine in background..." -ForegroundColor Yellow
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

if ($frontendJob) {
    Stop-Job $frontendJob -ErrorAction SilentlyContinue | Out-Null
    Remove-Job $frontendJob -ErrorAction SilentlyContinue | Out-Null
}

Write-Host "`nFORENZA Desktop session ended cleanly." -ForegroundColor Gray
