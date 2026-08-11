"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Pill, Activity, ShieldCheck, ChevronRight, TestTube, AlertTriangle } from "lucide-react";

export default function ToxicologyPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"screening" | "pharmacokinetics">("screening");

  // Mock Quantitative Toxicology Screen
  const analyteHits = [
    { name: "Morphine", matrix: "Whole Blood", concentration: "0.85 ± 0.09 mg/L", status: "FATAL_LETHAL", color: "bg-red-500/20 border-red-500/40 text-red-300", badge: "FATAL" },
    { name: "Fentanyl", matrix: "Whole Blood", concentration: "0.025 ± 0.003 mg/L", status: "FATAL_LETHAL", color: "bg-red-500/20 border-red-500/40 text-red-300", badge: "FATAL" },
    { name: "Cocaine", matrix: "Urine", concentration: "0.08 ± 0.01 mg/L", status: "THERAPEUTIC", color: "bg-emerald-500/20 border-emerald-500/40 text-emerald-300", badge: "THERAPEUTIC" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.15)]">
            <Pill className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Forensic Toxicology & Pharmacokinetics Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Quantitative Drug Screening • ISO 17025 Expanded Measurement Uncertainty (U_95%) • Widmark BAC Elimination & PMR
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("screening")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "screening" ? "bg-red-500/20 text-red-300 border border-red-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Quantitative Screening & ISO 17025
          </button>
          <button
            onClick={() => setActiveSubTab("pharmacokinetics")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "pharmacokinetics" ? "bg-red-500/20 text-red-300 border border-red-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Widmark BAC & PMR Audit
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: Quantitative Screening & ISO 17025 ── */}
      {activeSubTab === "screening" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Toxicology Sample ID</span>
              <p className="text-base font-bold text-red-400 font-mono">TOX-SAMPLE-901</p>
              <p className="text-[9px] text-zinc-400">Postmortem femoral blood specimen</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Measurement Uncertainty Standard</span>
              <p className="text-base font-bold text-tactical-text font-mono">ISO/IEC 17025 (k=2, 95% CI)</p>
              <p className="text-[9px] text-zinc-400">Validated SOFT/AAFS laboratory bounds</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Lethal Alert Status</span>
              <p className="text-base font-bold text-red-400 font-mono">ACUTE FATAL TOXICITY</p>
              <p className="text-[9px] text-zinc-400">Multiple lethal drug concentrations</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Quantitative Analyte Screening Results with Expanded Uncertainty (C_meas ± U_95%)
              </span>
              <span className="text-[9px] text-red-400 font-bold bg-red-500/10 border border-red-500/20 px-2 py-0.5 rounded">
                LC-MS/MS & GC-MS Screening
              </span>
            </div>

            <div className="space-y-3">
              {analyteHits.map((h, i) => (
                <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-black/20 border border-tactical-border/40 gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold font-mono">
                      <span className="text-tactical-text">{h.name}</span>
                      <span className="text-zinc-600">•</span>
                      <span className="text-indigo-400">{h.matrix}</span>
                    </div>
                    <p className="text-[10px] text-zinc-400">ISO 17025 Calibrated Measurement</p>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono">
                    <div className="text-right">
                      <p className="text-[9px] text-zinc-500">Concentration ± U_95%</p>
                      <p className="font-bold text-red-400">{h.concentration}</p>
                    </div>
                    <span className={`px-3 py-1 rounded text-[9px] font-bold uppercase ${h.color}`}>
                      {h.badge}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Widmark BAC & PMR Audit ── */}
      {activeSubTab === "pharmacokinetics" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Ethanol Widmark Elimination Model & Postmortem Redistribution Audit
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                PMR Ratio = 1.22
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Initial BAC (t=0)</span>
                <p className="text-base font-bold text-amber-400 font-mono">0.180 g/dL</p>
                <p className="text-[10px] text-zinc-400">Femoral blood specimen</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Current BAC (t = 4.0h)</span>
                <p className="text-base font-bold text-emerald-400 font-mono">0.120 g/dL</p>
                <p className="text-[10px] text-zinc-400">Elimination rate β = 0.015 g/dL/h</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Time to Complete Sobriety</span>
                <p className="text-base font-bold text-indigo-300 font-mono">12.00 Hours</p>
                <p className="text-[10px] text-zinc-400">Linear Widmark elimination</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
