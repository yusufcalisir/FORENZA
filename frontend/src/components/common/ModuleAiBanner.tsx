"use client";

import React, { useState, useEffect } from "react";
import { Zap, Upload, FileCode, CheckCircle, RefreshCw, KeyRound, Cpu, Sparkles, ShieldCheck } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getStoredApiKeys, hasLiveApiKeys, getActiveModeLabel } from "@/services/apiClient";
import ApiKeySettingsModal from "./ApiKeySettingsModal";

interface ModuleAiBannerProps {
  moduleName?: string;
  moduleType?: string;
  onAnalysisComplete?: (results: any) => void;
}

export default function ModuleAiBanner({
  moduleName = "Multi-Omic Forensic Engine",
  moduleType = "full_multiomic",
  onAnalysisComplete
}: ModuleAiBannerProps) {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [isLive, setIsLive] = useState(false);
  const [modeLabel, setModeLabel] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [lastAnalysis, setLastAnalysis] = useState<any | null>(null);

  useEffect(() => {
    const checkMode = () => {
      const live = hasLiveApiKeys();
      setIsLive(live);
      setModeLabel(getActiveModeLabel(isTr).label);
    };
    checkMode();
    window.addEventListener("forenza-apikeys-updated", checkMode);
    return () => window.removeEventListener("forenza-apikeys-updated", checkMode);
  }, [isTr]);

  const handleRunAiAnalysis = async (customFileContent?: string) => {
    setIsRunning(true);
    try {
      const res = await fetch("/api/analyze-module", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          moduleType,
          inputData: {
            fileName: fileName || "sample_codis24.fasta",
            customData: customFileContent || null,
            timestamp: new Date().toISOString()
          },
          userApiKeys: getStoredApiKeys(),
          lang: isTr ? "tr" : "en"
        })
      });

      if (res.ok) {
        const data = await res.json();
        setLastAnalysis(data);
        if (onAnalysisComplete) {
          onAnalysisComplete(data);
        }
      }
    } catch (err) {
      console.warn("Live module AI sweep failed:", err);
    } finally {
      setIsRunning(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      handleRunAiAnalysis(content);
    };
    reader.readAsText(file);
  };

  return (
    <>
      <div className="w-full mb-6 p-4 rounded-2xl bg-gradient-to-r from-[#0D1527] via-[#090F1E] to-[#0D1527] border border-tactical-border/80 shadow-xl font-mono text-tactical-text select-none">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          {/* Left Title & Status */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/40 flex items-center justify-center text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.2)] shrink-0">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xs sm:text-sm font-extrabold uppercase tracking-wider text-white">
                  {moduleName}
                </h3>
                <span
                  onClick={() => setIsApiModalOpen(true)}
                  className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider cursor-pointer transition-all border ${
                    isLive
                      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                      : "bg-purple-500/15 text-purple-300 border-purple-500/40 hover:bg-purple-500/25"
                  }`}
                >
                  {isLive ? (isTr ? "CANLI AI ÜRETİM MODU" : "LIVE AI PRODUCTION") : (isTr ? "DEMO SİMÜLASYON" : "DEMO SIMULATION")}
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                {isLive
                  ? (isTr ? "Bağlı AI API & Biyo-Hesaplama sunucusu üzerinden canlı analiz çalıştırılır." : "Executing live AI inference via connected API & biocomputational server.")
                  : (isTr ? "API anahtarlarınızı bağlayarak tüm modüllerde canlı AI analizini aktifleştirebilirsiniz." : "Connect API credentials to activate live AI analysis across all modules.")}
              </p>
            </div>
          </div>

          {/* Right Action Controls */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 shrink-0 w-full md:w-auto justify-end">
            {/* Custom Sample Upload Button */}
            <label className="px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/80 text-zinc-300 hover:text-white hover:border-cyan-500/50 text-xs font-bold transition-all flex items-center gap-2 cursor-pointer">
              <Upload className="w-3.5 h-3.5 text-cyan-400" />
              <span className="truncate">{fileName || (isTr ? "Özel Numune Yükle (FASTA/VCF/CSV)" : "Upload Custom Sample (FASTA/VCF/CSV)")}</span>
              <input
                type="file"
                accept=".fasta,.fa,.vcf,.csv,.json,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {/* Run Live AI Sweep Button */}
            <button
              type="button"
              onClick={() => handleRunAiAnalysis()}
              disabled={isRunning}
              className="px-4 py-2 rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-200 hover:bg-purple-500/30 text-xs font-extrabold transition-all flex items-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(168,85,247,0.2)] disabled:opacity-50"
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 text-purple-400 animate-spin" />
                  <span>{isTr ? "AI Taraması Çalışıyor..." : "Running AI Sweep..."}</span>
                </>
              ) : (
                <>
                  <Zap className="w-3.5 h-3.5 text-purple-400" />
                  <span>{isTr ? "⚡ Canlı AI Analizi Çalıştır" : "⚡ Run Live AI Sweep"}</span>
                </>
              )}
            </button>

            {/* Key Manager Launcher */}
            <button
              type="button"
              onClick={() => setIsApiModalOpen(true)}
              className="p-2 rounded-xl bg-tactical-surface/60 border border-tactical-border/80 text-zinc-400 hover:text-white hover:border-purple-500/40 transition-all cursor-pointer"
              title={isTr ? "API Anahtarlarını Yönet" : "Manage API Credentials"}
            >
              <KeyRound className="w-4 h-4 text-purple-400" />
            </button>
          </div>
        </div>

        {/* Live Analysis Output Summary Banner if Available */}
        {lastAnalysis && (
          <div className="mt-3 pt-3 border-t border-tactical-border/60 flex items-start justify-between gap-3 text-xs">
            <div className="flex items-start gap-2 text-emerald-300">
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-white block">
                  {lastAnalysis.provider} • {lastAnalysis.badge}
                </span>
                <p className="text-[11px] text-zinc-300 font-sans mt-0.5 leading-relaxed">
                  {lastAnalysis.analysis?.summary || JSON.stringify(lastAnalysis.analysis)}
                </p>
              </div>
            </div>
            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold text-[9px] uppercase border border-emerald-500/30 shrink-0">
              ANALYZED OK
            </span>
          </div>
        )}
      </div>

      <ApiKeySettingsModal isOpen={isApiModalOpen} onClose={() => setIsApiModalOpen(false)} />
    </>
  );
}
