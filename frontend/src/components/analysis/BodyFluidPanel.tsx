"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Droplet, Activity, ShieldCheck, ChevronRight, TestTube, BarChart2 } from "lucide-react";

export default function BodyFluidPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"classification" | "coextraction">("classification");

  // Mock mRNA Expression Probability Output
  const fluidProbabilities = [
    { fluid: "Saliva (Oral Fluid)", code: "SALIVA", prob: 0.94, markers: "HTN3, STATH", color: "bg-amber-500", text: "text-amber-300" },
    { fluid: "Venous Blood", code: "VENOUS_BLOOD", prob: 0.04, markers: "HBA1, HBB", color: "bg-red-500", text: "text-red-300" },
    { fluid: "Semen", code: "SEMEN", prob: 0.01, markers: "PRM1, PRM2, KLK3", color: "bg-cyan-500", text: "text-cyan-300" },
    { fluid: "Vaginal Secretion", code: "VAGINAL_SECRETION", prob: 0.01, markers: "CYP2B7P1, MYOZ1", color: "bg-pink-500", text: "text-pink-300" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <Droplet className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              mRNA Body Fluid Identification Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Cell-Type Specific mRNA Marker Expression • Multinomial Softmax Fluid Probability • RNA/DNA Co-Extraction Audit
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("classification")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "classification" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            mRNA Expression & Probabilities
          </button>
          <button
            onClick={() => setActiveSubTab("coextraction")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "coextraction" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            RNA/DNA Co-Extraction Audit
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: mRNA Expression & Probabilities ── */}
      {activeSubTab === "classification" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Stain Sample ID</span>
              <p className="text-base font-bold text-amber-400 font-mono">FLUID-STAIN-401</p>
              <p className="text-[9px] text-zinc-400">Biological trace swab from glass surface</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Top Predicted Fluid</span>
              <p className="text-base font-bold text-tactical-text font-mono">Saliva (P = 94.0%)</p>
              <p className="text-[9px] text-zinc-400">High HTN3 & STATH transcript levels</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">EDNAP Panel Status</span>
              <p className="text-base font-bold text-emerald-400 font-mono">Validated Expression</p>
              <p className="text-[9px] text-zinc-400">Cell-type specific biomarker confirmed</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Multinomial Body Fluid Probability Breakdown
              </span>
              <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                EDNAP mRNA Standard
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
                RNA/DNA Co-Extraction Yield & Integrity Audit
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                STR Compatible = TRUE
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Total RNA Yield</span>
                <p className="text-base font-bold text-amber-400 font-mono">3.50 ng/µL</p>
                <p className="text-[10px] text-zinc-400">Sufficient for multiplex RT-PCR</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">RNA Integrity Number (RIN)</span>
                <p className="text-base font-bold text-emerald-400 font-mono">RIN = 8.50 / 10.0</p>
                <p className="text-[10px] text-zinc-400">High 28S/18S rRNA peak ratio</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Recommended Co-Processing</span>
                <p className="text-xs font-bold text-indigo-300 font-mono">OPTIMAL_CO_EXTRACTION</p>
                <p className="text-[10px] text-zinc-400">Full 24-locus STR amplification</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
