"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { KeyRound, X, ShieldCheck, Eye, EyeOff, Save, Trash2, CheckCircle2, Sparkles, Cpu, Server, Dna } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getStoredApiKeys, saveApiKeys, ApiKeysConfig } from "@/services/apiClient";

export default function ApiKeySettingsModal({
  isOpen,
  onClose
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [keys, setKeys] = useState<ApiKeysConfig>({});
  const [showKeys, setShowKeys] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setKeys(getStoredApiKeys());
      setSaveSuccess(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    saveApiKeys(keys);
    setSaveSuccess(true);
    setTimeout(() => {
      setSaveSuccess(false);
      onClose();
    }, 1200);
  };

  const handleClear = () => {
    saveApiKeys({});
    setKeys({});
    setSaveSuccess(true);
    setTimeout(() => {
      setSaveSuccess(false);
    }, 1000);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md font-mono text-tactical-text select-none">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative w-full max-w-2xl bg-[#090F1E] border border-tactical-border/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        >
          {/* Top Header */}
          <div className="p-5 border-b border-tactical-border/80 bg-tactical-surface/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.25)]">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-extrabold uppercase tracking-wider text-white flex items-center gap-2">
                  {isTr ? "API Anahtarı & Canlı Üretim Ayarları" : "API Credentials & Live Production Settings"}
                </h2>
                <p className="text-[11px] text-zinc-400 mt-0.5">
                  {isTr ? "BYO-Key (Bring Your Own Key) Kendi Anahtarını Getir Motoru" : "BYO-Key Production Architecture"}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-tactical-border/50 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Form Body */}
          <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-5">
            {/* Zero Leakage Security Guarantee Note */}
            <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
              <div className="text-xs text-purple-200 leading-relaxed">
                <span className="font-bold text-white block mb-1">
                  {isTr ? "🔒 Kriptografik Gizlilik & Veri Güvenliği Garantisi" : "🔒 Zero Data Leakage Security Guarantee"}
                </span>
                {isTr
                  ? "Girdiğiniz tüm API anahtarları yalnızca tarayıcınızın yerel depolamasında (localStorage) saklanır ve doğrudan ilgili AI/biyo-hesaplama sunucularına iletilir. Üçüncü taraf veritabanlarına veya harici sunuculara asla kaydedilmez."
                  : "All entered API keys reside exclusively within your browser's local storage and are transmitted directly to destination AI/biocomputational services. No keys are ever stored on third-party servers or external logs."}
              </div>
            </div>

            {/* Controls Header */}
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                {isTr ? "AI & Biyo-Hesaplama Anahtarları" : "AI & Biocomputational Keys"}
              </span>
              <button
                type="button"
                onClick={() => setShowKeys(!showKeys)}
                className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 cursor-pointer"
              >
                {showKeys ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                <span>{showKeys ? (isTr ? "Gizle" : "Hide Keys") : (isTr ? "Göster" : "Show Keys")}</span>
              </button>
            </div>

            {/* Inputs Grid */}
            <div className="space-y-4">
              {/* Google Gemini Key */}
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>Google Gemini API Key</span>
                  <span className="text-[10px] text-purple-400 font-normal">GEMINI_API_KEY</span>
                </label>
                <input
                  type={showKeys ? "text" : "password"}
                  value={keys.geminiKey || ""}
                  onChange={e => setKeys({ ...keys, geminiKey: e.target.value })}
                  placeholder="AIzaSy..."
                  className="w-full bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500/60 transition-all font-mono"
                />
              </div>

              {/* OpenAI Key */}
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>OpenAI API Key</span>
                  <span className="text-[10px] text-purple-400 font-normal">OPENAI_API_KEY</span>
                </label>
                <input
                  type={showKeys ? "text" : "password"}
                  value={keys.openaiKey || ""}
                  onChange={e => setKeys({ ...keys, openaiKey: e.target.value })}
                  placeholder="sk-proj-..."
                  className="w-full bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500/60 transition-all font-mono"
                />
              </div>

              {/* Groq Key */}
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>Groq API Key</span>
                  <span className="text-[10px] text-purple-400 font-normal">GROQ_API_KEY</span>
                </label>
                <input
                  type={showKeys ? "text" : "password"}
                  value={keys.groqKey || ""}
                  onChange={e => setKeys({ ...keys, groqKey: e.target.value })}
                  placeholder="gsk_..."
                  className="w-full bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500/60 transition-all font-mono"
                />
              </div>

              {/* Anthropic Claude Key */}
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>Anthropic Claude API Key</span>
                  <span className="text-[10px] text-purple-400 font-normal">ANTHROPIC_API_KEY</span>
                </label>
                <input
                  type={showKeys ? "text" : "password"}
                  value={keys.anthropicKey || ""}
                  onChange={e => setKeys({ ...keys, anthropicKey: e.target.value })}
                  placeholder="sk-ant-api03-..."
                  className="w-full bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500/60 transition-all font-mono"
                />
              </div>

              {/* DeepSeek Key */}
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>DeepSeek API Key</span>
                  <span className="text-[10px] text-purple-400 font-normal">DEEPSEEK_API_KEY</span>
                </label>
                <input
                  type={showKeys ? "text" : "password"}
                  value={keys.deepseekKey || ""}
                  onChange={e => setKeys({ ...keys, deepseekKey: e.target.value })}
                  placeholder="sk-deepseek-..."
                  className="w-full bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500/60 transition-all font-mono"
                />
              </div>

              {/* NCBI E-utilities Key */}
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>NCBI Entrez / E-utilities API Key</span>
                  <span className="text-[10px] text-cyan-400 font-normal">NCBI_API_KEY</span>
                </label>
                <input
                  type={showKeys ? "text" : "password"}
                  value={keys.ncbiKey || ""}
                  onChange={e => setKeys({ ...keys, ncbiKey: e.target.value })}
                  placeholder="ncbi_api_key_..."
                  className="w-full bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500/60 transition-all font-mono"
                />
              </div>

              {/* Python FastAPI Backend URL */}
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>Python FastAPI Backend Endpoint</span>
                  <span className="text-[10px] text-emerald-400 font-normal">FASTAPI_URL</span>
                </label>
                <input
                  type="text"
                  value={keys.backendUrl || ""}
                  onChange={e => setKeys({ ...keys, backendUrl: e.target.value })}
                  placeholder="http://localhost:8000"
                  className="w-full bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-emerald-500/60 transition-all font-mono"
                />
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="pt-4 border-t border-tactical-border/80 flex items-center justify-between">
              <button
                type="button"
                onClick={handleClear}
                className="px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-bold hover:bg-red-500/20 transition-all flex items-center gap-2 cursor-pointer"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{isTr ? "Anahtarları Temizle (Demo Modu)" : "Clear Keys (Demo Mode)"}</span>
              </button>

              <div className="flex items-center gap-3">
                {saveSuccess && (
                  <span className="text-xs text-emerald-400 font-bold flex items-center gap-1.5 animate-pulse">
                    <CheckCircle2 className="w-4 h-4" />
                    {isTr ? "Kaydedildi!" : "Saved Successfully!"}
                  </span>
                )}
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-200 text-xs font-bold hover:bg-purple-500/30 transition-all flex items-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(168,85,247,0.2)]"
                >
                  <Save className="w-4 h-4 text-purple-400" />
                  <span>{isTr ? "Kaydet & Etkinleştir" : "Save & Activate Mode"}</span>
                </button>
              </div>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
