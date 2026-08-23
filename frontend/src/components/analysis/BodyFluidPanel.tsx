"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Droplet, Activity, ShieldCheck, ChevronRight, TestTube, BarChart2 } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function BodyFluidPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeSubTab, setActiveSubTab] = useState<"classification" | "coextraction">("classification");

  // Mock mRNA Expression Probability Output
  const fluidProbabilities = [
    {
      fluid: isTr ? "Tükürük (Oral Sıvı)" : "Saliva (Oral Fluid)",
      code: "SALIVA",
      prob: 0.94,
      markers: "HTN3, STATH",
      color: "bg-amber-500",
      text: "text-amber-300"
    },
    {
      fluid: isTr ? "Venöz Kan" : "Venous Blood",
      code: "VENOUS_BLOOD",
      prob: 0.04,
      markers: "HBA1, HBB",
      color: "bg-red-500",
      text: "text-red-300"
    },
    {
      fluid: isTr ? "Meni (Seminal Sıvı)" : "Semen",
      code: "SEMEN",
      prob: 0.01,
      markers: "PRM1, PRM2, KLK3",
      color: "bg-cyan-500",
      text: "text-cyan-300"
    },
    {
      fluid: isTr ? "Vajinal Salgı" : "Vaginal Secretion",
      code: "VAGINAL_SECRETION",
      prob: 0.01,
      markers: "CYP2B7P1, MYOZ1",
      color: "bg-pink-500",
      text: "text-pink-300"
    },
  ];

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Modern Unified Benchmark & Standards Mission Bar ────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        {/* Top: Engine Identity & Technical Verification Badges */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-400 shrink-0">
              <Droplet className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "mRNA Vücut Sıvısı Tanımlama" : "mRNA Body Fluid Identification"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300">
                  EDNAP • mRNA
                </span>
              </div>
            </div>
          </div>

          <div className="flex bg-black/60 p-1 rounded-xl border border-tactical-border/60 shrink-0">
            <button
              type="button"
              onClick={() => setActiveSubTab("classification")}
              className={`px-3 py-1 rounded-lg text-[10px] font-bold uppercase transition-all cursor-pointer ${
                activeSubTab === "classification" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm" : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {isTr ? "mRNA Ekspresyonu" : "mRNA Expression"}
            </button>
            <button
              type="button"
              onClick={() => setActiveSubTab("coextraction")}
              className={`px-3 py-1 rounded-lg text-[10px] font-bold uppercase transition-all cursor-pointer ${
                activeSubTab === "coextraction" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm" : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {isTr ? "Birlikte Ekstraksiyon" : "Co-Extraction"}
            </button>
          </div>
        </div>
      </div>

      {/* ── Sub-tab 1: mRNA Expression & Probabilities ── */}
      {activeSubTab === "classification" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Leke Numune Kimliği" : "Stain Sample ID"}
              </span>
              <p className="text-base font-bold text-amber-400 font-mono">FLUID-STAIN-401</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Cam yüzeyden biyolojik iz sürüntüsü" : "Biological trace swab from glass surface"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "En Yüksek Olasılıklı Sıvı" : "Top Predicted Fluid"}
              </span>
              <p className="text-base font-bold text-tactical-text font-mono">
                {isTr ? "Tükürük (P = %94.0)" : "Saliva (P = 94.0%)"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Yüksek HTN3 & STATH transkript seviyeleri" : "High HTN3 & STATH transcript levels"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "EDNAP Panel Durumu" : "EDNAP Panel Status"}
              </span>
              <p className="text-base font-bold text-emerald-400 font-mono">
                {isTr ? "Doğrulanmış Ekspresyon" : "Validated Expression"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Hücre tipine özgü biyobelirteç doğrulandı" : "Cell-type specific biomarker confirmed"}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "Çok Terimli Vücut Sıvısı Olasılık Dağılımı" : "Multinomial Body Fluid Probability Breakdown"}
              </span>
              <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                {isTr ? "EDNAP mRNA Standardı" : "EDNAP mRNA Standard"}
              </span>
            </div>

            <div className="space-y-3">
              {fluidProbabilities.map((item, i) => (
                <div key={i} className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center gap-2 font-bold">
                      <span className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                      <span className="text-tactical-text">{item.fluid}</span>
                      <span className="text-[10px] text-zinc-500 font-normal">({item.markers})</span>
                    </div>
                    <span className={`font-bold ${item.text}`}>{(item.prob * 100).toFixed(1)}%</span>
                  </div>

                  {/* Progress bar */}
                  <div className="h-2 rounded-full bg-black/40 overflow-hidden border border-tactical-border/30">
                    <div style={{ width: `${item.prob * 100}%` }} className={`h-full ${item.color} transition-all`} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: RNA/DNA Co-Extraction Audit ── */}
      {activeSubTab === "coextraction" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "RNA/DNA Birlikte Ekstraksiyon Verimi & Bütünlük Denetimi" : "RNA/DNA Co-Extraction Yield & Integrity Audit"}
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                {isTr ? "STR Uyumlu = DOĞRU" : "STR Compatible = TRUE"}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">{isTr ? "Toplam RNA Verimi" : "Total RNA Yield"}</span>
                <p className="text-base font-bold text-amber-400 font-mono">3.50 ng/µL</p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Multipleks RT-PCR için yeterli" : "Sufficient for multiplex RT-PCR"}
                </p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">{isTr ? "RNA Bütünlük Sayısı (RIN)" : "RNA Integrity Number (RIN)"}</span>
                <p className="text-base font-bold text-emerald-400 font-mono">RIN = 8.50 / 10.0</p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Yüksek 28S/18S rRNA pik oranı" : "High 28S/18S rRNA peak ratio"}
                </p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">{isTr ? "Önerilen Birlikte İşleme" : "Recommended Co-Processing"}</span>
                <p className="text-xs font-bold text-indigo-300 font-mono">OPTIMAL_CO_EXTRACTION</p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Tam 24 lokus STR amplifikasyonu" : "Full 24-locus STR amplification"}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
