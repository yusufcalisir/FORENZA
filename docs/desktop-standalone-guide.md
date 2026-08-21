# FORENZA: Desktop Standalone Operations & Packaging Manual

<p align="center">
  <strong>Native Standalone Forensic Workstation Application</strong><br />
  ISO/IEC 17025:2017 Aligned • Dual Electron & Tauri 2.0 Architecture • Python Sidecar Engine
</p>

---

## Table of Contents

1. [Overview & Architectural Philosophy](#1-overview--architectural-philosophy)
2. [Process Lifecycle & Python Sidecar Management](#2-process-lifecycle--python-sidecar-management)
3. [Native OS Forensic Capabilities](#3-native-os-forensic-capabilities)
4. [Quickstart: Launching the Desktop Workstation](#4-quickstart-launching-the-desktop-workstation)
5. [Compiling Standalone Installers (.exe, .AppImage, .dmg)](#5-compiling-standalone-installers-exe-appimage-dmg)
6. [Tauri 2.0 Rust Engine Compilation](#6-tauri-20-rust-engine-compilation)
7. [Troubleshooting & Process Diagnostics](#7-troubleshooting--process-diagnostics)

---

## 1. Overview & Architectural Philosophy

For casework analysts working on air-gapped forensic laptops or workstations without Docker or web servers, **FORENZA Desktop Standalone** bundles the complete platform into a native desktop application.

### Key Capabilities:
* **Self-Contained Execution:** No Docker, Nginx, or external web server installation required.
* **Autonomous Biocomputational Sidecar:** The desktop app automatically spawns and manages the Python FastAPI backend engine as a background child process on `127.0.0.1:8000`.
* **Zero Orphaned Processes:** When the desktop window is closed, the main process cleanly terminates all Python child processes and releases the port.
* **Native File I/O:** Directly browse, drag-and-drop, and parse capillary electrophoresis binary files (`.fsa`, `.hid`), Next-Gen sequencing (`.vcf`), and CODIS XML (`.cmf`).
* **Hardware Acceleration:** Native GPU-accelerated WebGL rendering for 3D Bloodstain Pattern Analysis (BPA), 3D Craniofacial Procrustes Superposition, and 3D Juror Scene reconstructions.

---

## 2. Process Lifecycle & Python Sidecar Management

```
                                    +-----------------------------------------+
                                    |         FORENZA DESKTOP APPLICATION     |
                                    |              (Main Process)             |
                                    +--------------------+--------------------+
                                                         |
                                        +----------------+----------------+
                                        |                                 |
                                        v                                 v
                    +-------------------------------------+   +-------------------------------------+
                    |       STANDALONE DESKTOP UI         |   |    FASTAPI BIOCOMPUTATIONAL SIDECAR |
                    |      Chromium / Native Webview      |   |   uvicorn app.main:app (Port 8000)  |
                    |    (Hardware Accelerated WebGL)     |   |   (35 Subsystems & PopGen Data)     |
                    +-------------------------------------+   +-------------------------------------+
                                        |                                 ^
                                        +─────────── Localhost ───────────+
                                                  (Port 8000 REST/WS)
```

### Sidecar Supervision Rules:
1. **Virtual Environment Detection:** Checks for Python in `venv/`, `.venv/`, `backend/venv/`, or system PATH.
2. **Health Check Polling:** Automatically verifies `GET /api/v1/system/health` before displaying the primary window.
3. **Single Instance Lock:** Prevents multiple instances from conflicting on port 8000; secondary attempts focus the existing window.
4. **Graceful Teardown:** Listens on `before-quit` and `window-all-closed` to send `SIGTERM` (or `taskkill /T /F` on Windows) to terminate the backend process.

---

## 3. Native OS Forensic Capabilities

The desktop context bridge (`desktop/preload.js`) exposes secure native APIs to the Next.js frontend via `window.forenzaDesktop`:

* **`openFileDialog(options)`:** Opens native OS file browser filtered for `.fsa`, `.hid`, `.vcf`, `.csv`, `.xml`.
* **`saveFileDialog(options)`:** Saves court-admissible ISO 17025 PDF reports, UYAP `.udf` documents, and raw JSON evidence files.
* **`getBackendStatus()`:** Returns sidecar PID, port, and online health state.
* **`restartBackend()`:** Allows analysts to restart the biocomputational engine without closing the UI.

---

## 4. Quickstart: Launching the Desktop Workstation

### On Windows:
Double-click **`start-desktop.bat`** or run in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-desktop.ps1
```

### On Linux / macOS:
```bash
chmod +x ./scripts/start-desktop.sh
./scripts/start-desktop.sh
```

---

## 5. Compiling Standalone Installers (.exe, .AppImage, .dmg)

To build redistributable desktop packages that can be copied via USB drive:

### Building for Windows:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-desktop.ps1
```
* Generates:
  - `dist/desktop/FORENZA-Setup-2.0.0-x64.exe` (NSIS Installer with desktop shortcut and uninstaller)
  - `dist/desktop/FORENZA-2.0.0-x64.exe` (Standalone Portable Executable, zero installation needed)

### Building for Linux / macOS:
```bash
chmod +x ./scripts/build-desktop.sh
./scripts/build-desktop.sh
```
* Generates:
  - Linux: `dist/desktop/FORENZA-2.0.0-x64.AppImage` and `.deb`
  - macOS: `dist/desktop/FORENZA-2.0.0-x64.dmg`

---

## 6. Tauri 2.0 Rust Engine Compilation

For systems with the Rust toolchain installed seeking an ultra-lightweight ($<50\text{ MB}$) binary:

```bash
# Navigate to project root
cd str-analysis

# Build frontend production bundle
cd frontend && npm run build && cd ..

# Build native Tauri executable
cargo tauri build
```
The output binary will be located in `src-tauri/target/release/forenza-desktop`.

---

## 7. Troubleshooting & Process Diagnostics

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Port 8000 in Use** | A previous Python or Docker process is holding port 8000. | Run `netstat -ano \| findstr :8000` (Windows) or `lsof -i :8000` (Linux) and terminate the lingering process. |
| **Python Sidecar Fails to Start** | Python dependencies not installed. | Run `pip install -r backend/requirements.txt` in your active Python virtual environment. |
| **Blank Window on Launch** | Frontend dev server is still compiling Next.js pages. | Wait 5 seconds and press `Ctrl+R` (`Cmd+R`) to reload the workstation view. |
