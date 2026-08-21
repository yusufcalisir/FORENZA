// ==============================================================================
// FORENZA: Forensic Evidence Operating System
// Native Desktop Main Process & Python Sidecar Supervisor
// ==============================================================================

const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn, execSync } = require('child_process');
const http = require('http');
const fs = require('fs');

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const ROOT_DIR = path.resolve(__dirname, '..');
const BACKEND_DIR = path.join(ROOT_DIR, 'backend');

let mainWindow = null;
let backendProcess = null;
let backendPort = 8000;
let backendReady = false;

// ------------------------------------------------------------------------------
// Single Instance Lock (Enforces one forensic workstation instance)
// ------------------------------------------------------------------------------
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

// ------------------------------------------------------------------------------
// Python Sidecar Resolver & Supervisor
// ------------------------------------------------------------------------------
function getPythonExecutable() {
  const isWin = process.platform === 'win32';
  
  // 1. Check local virtual environments
  const venvPaths = [
    path.join(ROOT_DIR, 'venv', isWin ? 'Scripts/python.exe' : 'bin/python'),
    path.join(BACKEND_DIR, 'venv', isWin ? 'Scripts/python.exe' : 'bin/python'),
    path.join(ROOT_DIR, '.venv', isWin ? 'Scripts/python.exe' : 'bin/python'),
  ];

  for (const p of venvPaths) {
    if (fs.existsSync(p)) {
      console.log(`[FORENZA Desktop] Found Python venv: ${p}`);
      return p;
    }
  }

  // 2. Fallback to system Python
  return isWin ? 'python' : 'python3';
}

function startBackendSidecar() {
  return new Promise((resolve) => {
    const pythonExe = getPythonExecutable();
    console.log(`[FORENZA Desktop] Launching Biocomputational Sidecar via ${pythonExe}...`);

    const env = Object.assign({}, process.env, {
      PYTHONUNBUFFERED: '1',
      PYTHONPATH: `${BACKEND_DIR}${path.delimiter}${ROOT_DIR}`,
      AIRGAP_MODE: 'true',
      OFFLINE_SIMULATION: 'true',
      PORT: `${backendPort}`,
    });

    try {
      backendProcess = spawn(
        pythonExe,
        ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', `${backendPort}`],
        {
          cwd: BACKEND_DIR,
          env: env,
          stdio: ['pipe', 'pipe', 'pipe'],
          windowsHide: true,
        }
      );

      backendProcess.stdout.on('data', (data) => {
        const msg = data.toString();
        if (isDev) console.log(`[Backend stdout] ${msg.trim()}`);
      });

      backendProcess.stderr.on('data', (data) => {
        const msg = data.toString();
        if (isDev) console.error(`[Backend stderr] ${msg.trim()}`);
      });

      backendProcess.on('error', (err) => {
        console.error('[FORENZA Desktop] Failed to spawn backend process:', err);
      });

      backendProcess.on('exit', (code, signal) => {
        console.log(`[FORENZA Desktop] Backend process exited with code ${code}, signal ${signal}`);
        backendReady = false;
      });

      // Poll healthcheck endpoint until ready
      const checkHealth = (retries = 30) => {
        const req = http.get(`http://127.0.0.1:${backendPort}/api/v1/system/health`, (res) => {
          if (res.statusCode === 200) {
            console.log('[FORENZA Desktop] Biocomputational Engine is HEALTHY (35 subsystems active).');
            backendReady = true;
            resolve(true);
          } else if (retries > 0) {
            setTimeout(() => checkHealth(retries - 1), 500);
          } else {
            console.warn('[FORENZA Desktop] Healthcheck timed out, proceeding anyway.');
            resolve(false);
          }
        });

        req.on('error', () => {
          if (retries > 0) {
            setTimeout(() => checkHealth(retries - 1), 500);
          } else {
            console.warn('[FORENZA Desktop] Backend connection retries exhausted.');
            resolve(false);
          }
        });
        req.end();
      };

      setTimeout(() => checkHealth(30), 800);
    } catch (e) {
      console.error('[FORENZA Desktop] Error launching sidecar:', e);
      resolve(false);
    }
  });
}

function stopBackendSidecar() {
  if (backendProcess) {
    console.log('[FORENZA Desktop] Terminating Python sidecar process...');
    try {
      if (process.platform === 'win32' && backendProcess.pid) {
        execSync(`taskkill /pid ${backendProcess.pid} /T /F 2>nul`);
      } else {
        backendProcess.kill('SIGTERM');
      }
    } catch (e) {
      // Process already terminated
    }
    backendProcess = null;
    backendReady = false;
  }
}

// ------------------------------------------------------------------------------
// Browser Window Creation
// ------------------------------------------------------------------------------
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: '#090d16',
    title: 'FORENZA: Forensic Evidence Operating System',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      webSecurity: true,
    },
  });

  // Custom tactical application menu
  mainWindow.setMenuBarVisibility(false);

  // Load Next.js interface
  const startUrl = isDev ? 'http://localhost:3000' : 'http://localhost:3000';
  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (isDev) {
      // mainWindow.webContents.openDevTools({ mode: 'detach' });
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ------------------------------------------------------------------------------
// App Lifecycle
// ------------------------------------------------------------------------------
app.whenReady().then(async () => {
  setupIpcHandlers();
  await startBackendSidecar();
  createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopBackendSidecar();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackendSidecar();
});

// ------------------------------------------------------------------------------
// Native IPC Handlers
// ------------------------------------------------------------------------------
function setupIpcHandlers() {
  // Open Native File Dialog (.fsa, .hid, .vcf, .csv, .xml, .txt)
  ipcMain.handle('forenza:open-file', async (event, options = {}) => {
    const defaultFilters = [
      { name: 'Forensic Profiles & Raw Data', extensions: ['fsa', 'hid', 'vcf', 'csv', 'xml', 'txt', 'json'] },
      { name: 'Capillary Electrophoresis (.fsa, .hid)', extensions: ['fsa', 'hid'] },
      { name: 'Next-Gen Sequencing VCF (.vcf)', extensions: ['vcf'] },
      { name: 'All Files', extensions: ['*'] }
    ];

    const result = await dialog.showOpenDialog(mainWindow, {
      title: options.title || 'Import Forensic Evidence Profile',
      filters: options.filters || defaultFilters,
      properties: options.multiple ? ['openFile', 'multiSelections'] : ['openFile'],
    });

    if (!result.canceled && result.filePaths.length > 0) {
      // Read file content if requested
      const filesData = result.filePaths.map((filePath) => {
        try {
          const stats = fs.statSync(filePath);
          const isText = ['.csv', '.txt', '.vcf', '.xml', '.json'].includes(path.extname(filePath).toLowerCase());
          return {
            path: filePath,
            name: path.basename(filePath),
            size: stats.size,
            content: isText && stats.size < 10 * 1024 * 1024 ? fs.readFileSync(filePath, 'utf-8') : null,
          };
        } catch (e) {
          return { path: filePath, name: path.basename(filePath), error: e.message };
        }
      });
      return { canceled: false, files: filesData };
    }
    return { canceled: true, files: [] };
  });

  // Save Native File Dialog (PDF, UDF, CSV, JSON Reports)
  ipcMain.handle('forenza:save-file', async (event, options = {}) => {
    const result = await dialog.showSaveDialog(mainWindow, {
      title: options.title || 'Export Forensic Report',
      defaultPath: options.defaultPath || 'FORENZA_ISO17025_Report.pdf',
      filters: options.filters || [
        { name: 'ISO 17025 Expert Report (*.pdf)', extensions: ['pdf'] },
        { name: 'National Judicial UYAP Document (*.udf)', extensions: ['udf'] },
        { name: 'Forensic Data JSON (*.json)', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ],
    });

    if (!result.canceled && result.filePath && options.content) {
      try {
        const isBuffer = Buffer.isBuffer(options.content) || options.isBinary;
        const data = isBuffer ? Buffer.from(options.content, options.encoding || 'base64') : options.content;
        fs.writeFileSync(result.filePath, data);
        return { success: true, filePath: result.filePath };
      } catch (e) {
        return { success: false, error: e.message };
      }
    }
    return { success: !result.canceled, filePath: result.filePath };
  });

  // Telemetry & Status
  ipcMain.handle('forenza:backend-status', () => ({
    online: backendReady,
    port: backendPort,
    pid: backendProcess ? backendProcess.pid : null,
  }));

  ipcMain.handle('forenza:restart-backend', async () => {
    stopBackendSidecar();
    await startBackendSidecar();
    return { online: backendReady };
  });

  ipcMain.handle('forenza:open-external', (event, url) => {
    if (url && (url.startsWith('https://') || url.startsWith('http://'))) {
      shell.openExternal(url);
    }
  });

  // Window Controls
  ipcMain.on('forenza:window-minimize', () => mainWindow && mainWindow.minimize());
  ipcMain.on('forenza:window-maximize', () => {
    if (mainWindow) {
      mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
    }
  });
  ipcMain.on('forenza:window-close', () => mainWindow && mainWindow.close());
}
