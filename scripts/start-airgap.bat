@echo off
REM ==============================================================================
REM FORENZA: Forensic Evidence Operating System
# One-Click Air-Gapped Workstation Launcher (Windows Batch Wrapper)
REM ==============================================================================

TITLE FORENZA Air-Gapped Forensic Operating System

echo Launching FORENZA Air-Gapped Workstation via PowerShell...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-airgap.ps1"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] FORENZA launcher encountered an error. Press any key to exit.
    pause >nul
)
