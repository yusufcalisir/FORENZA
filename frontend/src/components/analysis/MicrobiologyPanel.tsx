"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Dna, ShieldCheck, Activity, ChevronRight, UserCheck, Layers, PieChart } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function MicrobiologyPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeSubTab, setActiveSubTab] = useState<"classification" | "origin">("classification");

  // 16S rRNA Taxa Distribution
  const taxaData = [
    { genus: "Cutibacterium", phylum: "Actinomycetota", percentage: 65, color: "bg-indigo-500" },
    { genus: "Staphylococcus", phylum: "Bacillota", percentage: 20, color: "bg-emerald-500" },
    { genus: "Corynebacterium", phylum: "Actinomycetota", percentage: 10, color: "bg-purple-500" },
    { genus: isTr ? "Diğer Sınıflandırılmamış" : "Other Unclassified", phylum: isTr ? "Çevresel" : "Environmental", percentage: 5, color: "bg-zinc-600" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              {isTr ? "Adli Mikrobiyoloji & 16S rRNA Merkezi" : "Forensic Microbiology & 16S rRNA Hub"}
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              {isTr
                ? "16S rRNA V3-V4 Profillendirmesi • Shannon Çeşitlilik İndeksi H' • Vücut Bölgesi & Çevresel Köken Denetimi"
                : "16S rRNA V3-V4 Profiling • Shannon Diversity Index H' • Human Body Site & Environmental Origin Auditing"}
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("classification")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "classification" ? "bg-purple-500/20 text-purple-300 border border-purple-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "16S rRNA Taksonomik Dağılım" : "16S rRNA Taxonomic Distribution"}
          </button>
          <button
            onClick={() => setActiveSubTab("origin")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "origin" ? "bg-purple-500/20 text-purple-300 border border-purple-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "Vücut Bölgesi & Toprak Kökeni" : "Body Site & Soil Origin"}
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: 16S rRNA Taxonomic Distribution ── */}
      {activeSubTab === "classification" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Mikrobiyal Numune No" : "Microbial Sample ID"}
              </span>
              <p className="text-base font-bold text-purple-400 font-mono">MIC-SAMPLE-301</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Biyolojik iz temas sürüntüsü" : "Biological trace touch swab"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Baskın Takson" : "Dominant Taxon"}
              </span>
              <p className="text-base font-bold text-tactical-text font-mono">Cutibacterium (%65)</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Actinomycetota şubesi" : "Actinomycetota phylum"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Shannon Çeşitlilik İndeksi" : "Shannon Diversity Index"}
              </span>
              <p className="text-base font-bold text-emerald-400 font-mono">H' = 0.9421</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Düşük çeşitlilikli deri mikrobiyom imzası" : "Low-diversity skin community signature"}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "16S rRNA Hiperdeğişken Göreceli Bolluk Dağılımı" : "16S rRNA Hypervariable Relative Abundance Distribution"}
              </span>
              <span className="text-[9px] text-purple-400 font-bold bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                {isTr ? "SILVA 138.1 Taksonomi VT" : "SILVA 138.1 Taxonomy DB"}
              </span>
            </div>

            {/* Abundance Progress Bar */}
            <div className="h-4 rounded-xl bg-black/40 overflow-hidden flex border border-tactical-border/40">
              {taxaData.map((t, i) => (
                <div key={i} style={{ width: `${t.percentage}%` }} className={`${t.color} h-full transition-all`} title={`${t.genus}: ${t.percentage}%`} />
              ))}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              {taxaData.map((t, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-black/20 border border-tactical-border/40 text-xs">
                  <div className="flex items-center gap-2 font-mono">
                    <span className={`w-3 h-3 rounded-full ${t.color}`} />
                    <span className="font-bold text-tactical-text">{t.genus}</span>
                    <span className="text-[10px] text-zinc-500">({t.phylum})</span>
                  </div>
                  <span className="font-bold text-purple-300 font-mono">%{t.percentage}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Body Site & Soil Origin ── */}
      {activeSubTab === "origin" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "Mikrobiyal Vücut Bölgesi & Çevresel Köken Tahmini" : "Microbial Body Site & Environmental Origin Prediction"}
              </span>
              <span className="text-[9px] text-purple-400 font-bold bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                LR_microbiome = 185.00
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Tahmin Edilen Vücut Bölgesi" : "Predicted Body Site"}
                </span>
                <p className="text-base font-bold text-purple-400 font-mono">
                  {isTr ? "YAĞLI_DERİ (SEBACEOUS_SKIN)" : "SEBACEOUS_SKIN"}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Güven Skoru: %94.0" : "Confidence Score: 94.0%"}
                </p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Anahtar Belirteç Taksonlar" : "Key Indicator Taxa"}
                </span>
                <p className="text-sm font-bold text-indigo-300 font-mono">Cutibacterium acnes</p>
                <p className="text-[10px] text-zinc-400">Staphylococcus epidermidis</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Bray-Curtis Toprak Uzaklığı" : "Bray-Curtis Soil Distance"}
                </span>
                <p className="text-sm font-bold text-emerald-400 font-mono">D_Bray-Curtis = 0.9850</p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Çevresel toprak ile yüksek benzemezlik" : "High dissimilarity to environmental soil"}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
