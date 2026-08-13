export interface ApiKeysConfig {
  geminiKey?: string;
  openaiKey?: string;
  groqKey?: string;
  anthropicKey?: string;
  deepseekKey?: string;
  ncbiKey?: string;
  backendUrl?: string;
  polygonRpc?: string;
}

const STORAGE_KEY = "forenza_api_keys_v1";

export function getStoredApiKeys(): ApiKeysConfig {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw);
  } catch (e) {
    console.warn("Failed to load API keys from storage:", e);
    return {};
  }
}

export function saveApiKeys(keys: ApiKeysConfig): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
    // Dispatch custom window event so all components react instantly
    window.dispatchEvent(new Event("forenza-apikeys-updated"));
  } catch (e) {
    console.warn("Failed to save API keys to storage:", e);
  }
}

export function hasLiveApiKeys(): boolean {
  const keys = getStoredApiKeys();
  return Boolean(
    keys.geminiKey?.trim() ||
    keys.openaiKey?.trim() ||
    keys.groqKey?.trim() ||
    keys.anthropicKey?.trim() ||
    keys.deepseekKey?.trim() ||
    keys.ncbiKey?.trim() ||
    keys.backendUrl?.trim()
  );
}

export function getActiveModeLabel(isTr: boolean): { label: string; isLive: boolean } {
  const isLive = hasLiveApiKeys();
  if (isLive) {
    return { label: isTr ? "CANLI ÜRETİM MODU" : "LIVE PRODUCTION MODE", isLive: true };
  }
  return { label: isTr ? "DEMO SİMÜLASYON MODU" : "DEMO SIMULATION MODE", isLive: false };
}
