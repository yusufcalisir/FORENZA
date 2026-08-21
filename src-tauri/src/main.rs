// ==============================================================================
// FORENZA: Forensic Evidence Operating System
// Tauri 2.0 Native Rust Main Entry Point
// ==============================================================================

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::{Manager, State};

struct BackendSidecar(Mutex<Option<Child>>);

#[tauri::command]
fn get_system_status() -> serde_json::Value {
    serde_json::json!({
        "status": "OPERATIONAL",
        "subsystems": 35,
        "mode": "AIR_GAPPED_STANDALONE",
        "platform": std::env::consts::OS
    })
}

fn main() {
    tauri::Builder::default()
        .manage(BackendSidecar(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![get_system_status])
        .setup(|app| {
            // Optional: Launch backend child process in Tauri setup
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                // window.open_devtools();
            }
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                // Ensure backend child process is killed when window is destroyed
                let state: State<BackendSidecar> = window.state();
                if let Ok(mut lock) = state.0.lock() {
                    if let Some(mut child) = lock.take() {
                        let _ = child.kill();
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running FORENZA desktop application");
}
