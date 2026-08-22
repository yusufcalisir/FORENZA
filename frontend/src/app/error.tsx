"use client";

import { useEffect } from "react";
import { AlertOctagon, RotateCcw, ShieldAlert, Home } from "lucide-react";
import Link from "next/link";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function RootErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  useEffect(() => {
    // Log unexpected client exceptions
    console.error("[FORENZA Runtime Exception Boundary]", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#070D18] flex items-center justify-center p-4">
      <div className="w-full max-w-xl p-6 sm:p-8 rounded-2xl bg-tactical-surface/90 border border-rose-500/40 shadow-[0_0_40px_rgba(244,63,94,0.15)] flex flex-col items-center text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
          <AlertOctagon className="w-8 h-8 animate-pulse" />
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-300 font-mono text-[10px] font-bold uppercase tracking-widest">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{isTr ? "İstisna Sınırı Yakalandı" : "Exception Boundary Triggered"}</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            {isTr ? "Sistem Hatası Meydana Geldi" : "A System Exception Occurred"}
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 max-w-md mx-auto leading-relaxed">
            {isTr
              ? "Biyo-hesaplamalı modül veya işleme hattında beklenmeyen bir hata oluştu. Veri bütünlüğü korundu."
              : "An unexpected runtime error occurred in the biocomputational pipeline. Data integrity has been preserved."}
          </p>
        </div>

        {error.message && (
          <div className="w-full p-3 rounded-xl bg-black/60 border border-tactical-border/80 text-left font-mono text-[11px] text-zinc-400 overflow-x-auto">
            <span className="text-rose-400 font-bold block mb-1">Diagnostic Details:</span>
            <code>{error.message}</code>
            {error.digest && (
              <span className="block mt-1 text-[9px] text-zinc-600">Digest ID: {error.digest}</span>
            )}
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-3 w-full justify-center">
          <button
            type="button"
            onClick={() => reset()}
            className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-mono font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg shadow-emerald-500/20"
          >
            <RotateCcw className="w-4 h-4" />
            <span>{isTr ? "İşlemi Yeniden Dene" : "Retry Pipeline"}</span>
          </button>

          <Link
            href="/analysis"
            className="px-5 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-mono font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all border border-zinc-700"
          >
            <Home className="w-4 h-4 text-cyan-400" />
            <span>{isTr ? "Çalışma Alanına Dön" : "Return to Workspace"}</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
