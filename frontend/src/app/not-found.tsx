"use client";

import Link from "next/link";
import { Compass, Home, Layers, Search } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function NotFound() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  return (
    <div className="min-h-screen bg-[#070D18] flex items-center justify-center p-4">
      <div className="w-full max-w-lg p-6 sm:p-8 rounded-2xl bg-tactical-surface/90 border border-tactical-border/80 flex flex-col items-center text-center space-y-6 shadow-2xl relative overflow-hidden">
        {/* Glowing radar background aura */}
        <div className="absolute -top-20 -left-20 w-48 h-48 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-20 -right-20 w-48 h-48 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none" />

        <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <Compass className="w-8 h-8 animate-[spin_8s_linear_infinite]" />
        </div>

        <div className="space-y-2">
          <span className="font-mono text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-emerald-400 to-teal-300">
            404
          </span>
          <h1 className="text-lg sm:text-xl font-bold text-white tracking-tight">
            {isTr ? "Adli Koordinat Bulunamadı" : "Forensic Coordinate Not Found"}
          </h1>
          <p className="text-xs text-zinc-400 leading-relaxed max-w-sm mx-auto">
            {isTr
              ? "İstenen modül, profil veya veri tablosu mevcut federe defter ağında bulunamadı."
              : "The requested module, biometric profile, or evidence route does not exist in this federated workspace."}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full pt-2">
          <Link
            href="/analysis"
            className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-mono font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md shadow-emerald-500/20"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{isTr ? "Süit Matrisi" : "Analysis Matrix"}</span>
          </Link>

          <Link
            href="/"
            className="px-4 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-mono font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all border border-zinc-700"
          >
            <Home className="w-3.5 h-3.5 text-cyan-400" />
            <span>{isTr ? "Ana Sayfa" : "Landing Hub"}</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
