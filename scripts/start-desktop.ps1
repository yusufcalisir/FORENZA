# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# One-Click Desktop Workstation Launcher (Windows PowerShell)
# ==============================================================================
#
# Architecture:
#   PowerShell launcher -> validates prerequisites
#                       -> ensures Next.js dev server is running (port 3000)
#                       -> launches Electron shell (which internally spawns
#                          the Python FastAPI sidecar via main.js)
#                       -> cleans up Next.js on exit
#
# The Python/FastAPI sidecar lifecycle is owned by Electron (desktop/main.js).
# This launcher only validates that a suitable Python interpreter is available.
# ==============================================================================

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------------------------
# Path Setup - all paths derived dynamically from script location
# ------------------------------------------------------------------------------
$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir      = Split-Path -Parent $ScriptDir
$DesktopDir   = Join-Path $RootDir "desktop"
$FrontendDir  = Join-Path $RootDir "frontend"

# ------------------------------------------------------------------------------
# Banner
# ------------------------------------------------------------------------------
Clear-Host
Write-Host ""
Write-Host "  ========================================================================" -ForegroundColor Magenta
Write-Host "   FORENZA  Forensic Evidence Operating System                            " -ForegroundColor Cyan
Write-Host "  ========================================================================" -ForegroundColor Magenta
Write-Host "  ISO/IEC 17025:2017 Aligned  *  Standalone Desktop Process Engine"
Write-Host "  ------------------------------------------------------------------------"
Write-Host ""

# ------------------------------------------------------------------------------
# Helper: Test whether the Next.js frontend is serving HTTP on port 3000
# ------------------------------------------------------------------------------
function Test-FrontendReady {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" `
            -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        return ($response.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

# ==============================================================================
# STEP 1 - Prerequisite Validation
# ==============================================================================
Write-Host "[1/4] Validating Runtime Prerequisites..." -ForegroundColor Cyan

# --- Node.js ---
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "  [FAIL] Node.js is required but not found in PATH." -ForegroundColor Red
    Write-Host "         Install from https://nodejs.org/ and ensure 'node' is on PATH." -ForegroundColor Yellow
    exit 1
}
$nodeVersion = & node --version 2>&1
Write-Host "  [OK]  Node.js $nodeVersion" -ForegroundColor Green

# --- Resolve npm and npx (Windows Win32 CreateProcess requires .cmd wrapper) ---
$npmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source
if (-not $npmCmd) {
    $npmCmd = (Get-Command npm -ErrorAction SilentlyContinue).Source
}
if (-not $npmCmd) {
    Write-Host "  [FAIL] npm is required but not found in PATH." -ForegroundColor Red
    Write-Host "         npm ships with Node.js - reinstall Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

$npxCmd = (Get-Command npx.cmd -ErrorAction SilentlyContinue).Source
if (-not $npxCmd) {
    $npxCmd = (Get-Command npx -ErrorAction SilentlyContinue).Source
}
if (-not $npxCmd) {
    $npxCmd = "npx.cmd"
}

# --- Python >= 3.12 ---
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  [FAIL] Python 3.12+ is required but not found in PATH." -ForegroundColor Red
    Write-Host "         The Electron application spawns a Python FastAPI sidecar internally." -ForegroundColor Yellow
    Write-Host "         Install from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
$pyRaw = & python --version 2>&1
$pyVersionString = "$pyRaw".Trim()    # e.g. "Python 3.12.4"
if ($pyVersionString -match "Python\s+(\d+)\.(\d+)") {
    $pyMajor = [int]$Matches[1]
    $pyMinor = [int]$Matches[2]
    if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 12)) {
        Write-Host "  [FAIL] Python 3.12+ is required, but found $pyVersionString" -ForegroundColor Red
        Write-Host "         Upgrade from https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  [OK]  $pyVersionString" -ForegroundColor Green
}
else {
    Write-Host "  [WARN] Could not parse Python version from: $pyVersionString" -ForegroundColor Yellow
    Write-Host "         Proceeding, but the FastAPI sidecar may fail if Python is older than 3.12." -ForegroundColor Yellow
}

Write-Host ""

# ==============================================================================
# STEP 2 - Dependency Verification
# ==============================================================================
Write-Host "[2/4] Verifying Project Dependencies..." -ForegroundColor Cyan

# --- Desktop (Electron wrapper) ---
if (-not (Test-Path (Join-Path $DesktopDir "node_modules"))) {
    Write-Host "  Installing desktop Electron dependencies (one-time)..." -ForegroundColor Yellow
    $npmDesktop = Start-Process -FilePath $npmCmd `
        -ArgumentList "install","--prefer-offline","--no-audit" `
        -WorkingDirectory $DesktopDir -PassThru -NoNewWindow -Wait
    if ($npmDesktop.ExitCode -ne 0) {
        Write-Host "  [FAIL] npm install failed in desktop/ with exit code $($npmDesktop.ExitCode)" -ForegroundColor Red
        Write-Host "         Check network connectivity and package-lock.json integrity." -ForegroundColor Yellow
        exit 1
    }
}
Write-Host "  [OK]  Desktop dependencies ready." -ForegroundColor Green

# --- Frontend (Next.js application) ---
if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Host "  Installing frontend Next.js dependencies (one-time)..." -ForegroundColor Yellow
    $npmFrontend = Start-Process -FilePath $npmCmd `
        -ArgumentList "install","--prefer-offline","--no-audit" `
        -WorkingDirectory $FrontendDir -PassThru -NoNewWindow -Wait
    if ($npmFrontend.ExitCode -ne 0) {
        Write-Host "  [FAIL] npm install failed in frontend/ with exit code $($npmFrontend.ExitCode)" -ForegroundColor Red
        Write-Host "         Check network connectivity and package-lock.json integrity." -ForegroundColor Yellow
        exit 1
    }
}
Write-Host "  [OK]  Frontend dependencies ready." -ForegroundColor Green

Write-Host ""

# ==============================================================================
# STEP 3 - Frontend Server (Next.js on port 3000)
# ==============================================================================
Write-Host "[3/4] Preparing Next.js Frontend Server..." -ForegroundColor Cyan

$frontendProcess    = $null   # Process object if we started Next.js
$weStartedFrontend  = $false  # Track ownership for cleanup

if (Test-FrontendReady) {
    Write-Host "  [OK]  Frontend already running on http://localhost:3000 (reusing)." -ForegroundColor Green
}
else {
    Write-Host "  Starting Next.js development server in background..." -ForegroundColor Yellow

    $stdoutLog = Join-Path $env:TEMP "forenza-next-stdout.log"
    $stderrLog = Join-Path $env:TEMP "forenza-next-stderr.log"

    $frontendProcess = Start-Process -FilePath $npmCmd `
        -ArgumentList "run","dev" `
        -WorkingDirectory $FrontendDir `
        -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError  $stderrLog

    $weStartedFrontend = $true

    # Wait for Next.js to become ready (bounded timeout)
    $timeoutSec = 90
    $elapsed    = 0
    $pollSec    = 2
    $ready      = $false

    Write-Host "  Waiting for Next.js to compile and start (up to ${timeoutSec}s)..." -ForegroundColor Yellow
    while ($elapsed -lt $timeoutSec) {
        # Check if the process crashed during startup
        if ($frontendProcess.HasExited) {
            $exitCode = $frontendProcess.ExitCode
            Write-Host ""
            Write-Host "  [FAIL] Next.js process exited unexpectedly with code $exitCode" -ForegroundColor Red
            if (Test-Path $stderrLog) {
                $errTail = Get-Content $stderrLog -Tail 10 -ErrorAction SilentlyContinue
                if ($errTail) {
                    Write-Host "  --- stderr (last 10 lines) ---" -ForegroundColor Yellow
                    $errTail | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
                }
            }
            exit 1
        }

        if (Test-FrontendReady) {
            $ready = $true
            break
        }

        Start-Sleep -Seconds $pollSec
        $elapsed += $pollSec
        Write-Host -NoNewline "." -ForegroundColor DarkGray
    }

    Write-Host ""
    if (-not $ready) {
        Write-Host "  [FAIL] Next.js did not become ready within ${timeoutSec} seconds." -ForegroundColor Red
        Write-Host "         Check $stderrLog for errors." -ForegroundColor Yellow
        # Clean up the process we started before exiting
        if (-not $frontendProcess.HasExited) {
            & taskkill /PID $frontendProcess.Id /T /F 2>$null | Out-Null
        }
        exit 1
    }
    Write-Host "  [OK]  Next.js is ready on http://localhost:3000" -ForegroundColor Green
}

Write-Host ""

# ==============================================================================
# STEP 4 - Launch Electron Desktop Shell
# ==============================================================================
Write-Host "[4/4] Launching FORENZA Electron Desktop..." -ForegroundColor Cyan
Write-Host "  Electron will start the Python FastAPI sidecar internally." -ForegroundColor Gray
Write-Host ""

$electronExitCode = 0

try {
    # npx resolves the local electron binary from desktop/node_modules
    Push-Location $DesktopDir
    & $npxCmd electron .
    $electronExitCode = $LASTEXITCODE
}
finally {
    Pop-Location

    # --- Cleanup: kill the Next.js process tree we started ---
    if ($weStartedFrontend -and $frontendProcess -and -not $frontendProcess.HasExited) {
        Write-Host ""
        Write-Host "  Stopping Next.js server (PID $($frontendProcess.Id))..." -ForegroundColor Gray
        # taskkill /T kills the entire process tree (npm -> node -> next)
        # This mirrors the pattern used in desktop/main.js L144 for the Python sidecar
        & taskkill /PID $frontendProcess.Id /T /F 2>$null | Out-Null
        try { $frontendProcess.WaitForExit(5000) } catch { }
    }
}

# --- Report exit status ---
Write-Host ""
if ($electronExitCode -ne 0) {
    Write-Host "  FORENZA Desktop exited with code $electronExitCode." -ForegroundColor Yellow
}
else {
    Write-Host "  FORENZA Desktop session ended." -ForegroundColor Gray
}
