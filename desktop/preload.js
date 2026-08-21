// ==============================================================================
// FORENZA: Forensic Evidence Operating System
// Desktop Secure IPC Preload Script (Context Isolation Layer)
// ==============================================================================

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('forenzaDesktop', {
  isDesktop: true,
  platform: process.platform,
  version: '2.0.0',

  // Native File Dialogs (for .fsa, .hid, .vcf, .csv, .xml, .pdf)
  openFileDialog: (options = {}) => ipcRenderer.invoke('forenza:open-file', options),
  saveFileDialog: (options = {}) => ipcRenderer.invoke('forenza:save-file', options),

  // System & Sidecar Telemetry
  getBackendStatus: () => ipcRenderer.invoke('forenza:backend-status'),
  restartBackend: () => ipcRenderer.invoke('forenza:restart-backend'),

  // Window Controls
  minimizeWindow: () => ipcRenderer.send('forenza:window-minimize'),
  maximizeWindow: () => ipcRenderer.send('forenza:window-maximize'),
  closeWindow: () => ipcRenderer.send('forenza:window-close'),

  // Open External Links Safely
  openExternal: (url) => ipcRenderer.invoke('forenza:open-external', url),
});
