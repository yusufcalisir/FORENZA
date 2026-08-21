@echo off
REM ==============================================================================
REM FORENZA: Forensic Evidence Operating System
REM One-Click Desktop Workstation Launcher (Windows Batch Wrapper)
REM ==============================================================================

chcp 65001 >nul
TITLE FORENZA Native Desktop Forensic Workstation

echo Launching FORENZA Desktop Workstation...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-desktop.ps1"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Desktop launcher encountered an issue. Press any key to exit.
    pause >nul
)
