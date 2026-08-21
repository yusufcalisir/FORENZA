# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# Desktop Distribution Installer Builder (Windows PowerShell)
# ==============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$DesktopDir = Join-Path $RootDir "desktop"
$FrontendDir = Join-Path $RootDir "frontend"
$DistDir = Join-Path $RootDir "dist\desktop"

Clear-Host
Write-Host "=== FORENZA Standalone Desktop Installer Builder (Windows) ===" -ForegroundColor Cyan
Write-Host "Compiling standalone Windows NSIS Installer (.exe) and Portable Executable...`n"

# 1. Build Frontend Static Assets
Write-Host "[1/3] Compiling Next.js Workstation Production Bundle..." -ForegroundColor Cyan
Set-Location $FrontendDir
& npm run build

# 2. Prepare Desktop Dependencies
Write-Host "[2/3] Preparing Desktop Packaging Environment..." -ForegroundColor Cyan
Set-Location $DesktopDir
& npm install --prefer-offline --no-audit

# 3. Build Windows Executable via Electron Builder
Write-Host "[3/3] Compiling Native Windows Executable (.exe)..." -ForegroundColor Cyan
& npx electron-builder --win --x64

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "  [OK] FORENZA Windows Desktop Installer Built Successfully!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Output Directory: $DistDir" -ForegroundColor White
if (Test-Path $DistDir) {
    Get-ChildItem -Path $DistDir -Filter "*.exe" | ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 1)
        Write-Host "  * $($_.Name) ($sizeMB MB)" -ForegroundColor Cyan
    }
}
Write-Host "`nReady for air-gapped laboratory distribution without web server installation.`n"
