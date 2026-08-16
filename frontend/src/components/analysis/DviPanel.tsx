"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, UserCheck, ShieldAlert, FileSpreadsheet, CheckCircle2, ChevronRight, Layers, AlertCircle } from "lucide-react";

export default function DviPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"missing" | "dvi">("missing");

  // Mock Missing Persons Candidate Hits
  const missingCandidates = [
    { id: "MP-CANDIDATE-802", rel: "PARENT_CHILD", lr: "1,450,200.00", log10: "6.16", prob: "99.9999%", tier: "CONFIRMED_MATCH" },
    { id: "MP-CANDIDATE-411", rel: "FULL_SIBLING", lr: "42,800.00", log10: "4.63", prob: "99.9976%", tier: "STRONG_CANDIDATE" },
    { id: "MP-CANDIDATE-109", rel: "HALF_SIBLING", lr: "340.50", log10: "2.53", prob: "99.7070%", tier: "MODERATE_CANDIDATE" },
  ];

  // Mock Interpol DVI AM/PM Multi-Omic Reconciliation Matrix (Research §4.1, VECTOR_P2_03)
  const dviMatrix = [
    {
      am: "AM-REF-FAMILY-01",
      pm: "PM-REMAIN-SITE-A01 (VECTOR_P2_03)",
      rel: "PARENT_CHILD",
      autoLr: "5,200.00",
      ystrLr: "5,000.00 (p=0.0002)",
      mtdnaLr: "10,000.00 (p=0.0001)",
      jointLr: "2.60 × 10¹¹",
      log10: "11.41",
      status: "DEFINITIVE_IDENTIFICATION",
      action: "Sufficient forensic proof for standalone legal identification.",
    },
    {
      am: "AM-REF-FAMILY-02",
      pm: "PM-REMAIN-SITE-A04",
      rel: "PARENT_CHILD",
      autoLr: "185,400.00",
      ystrLr: "1.00 (N/A)",
      mtdnaLr: "1.00 (N/A)",
      jointLr: "1.85 × 10⁵",
      log10: "5.27",
      status: "PROBABLE_MATCH",
      action: "Requires secondary corroboration (forensic odontology, implants).",
    },
    {
      am: "AM-REF-FAMILY-03",
      pm: "PM-REMAIN-SITE-B02",
      rel: "PARENT_CHILD",
      autoLr: "1,250.00",
      ystrLr: "1.00 (N/A)",
      mtdnaLr: "1.00 (N/A)",
      jointLr: "1,250.00",
      log10: "3.10",
      status: "INCONCLUSIVE",
      action: "Insufficient data; requires additional STR or NGS SNP testing.",
    },
    {
      am: "AM-REF-FAMILY-04",
      pm: "PM-REMAIN-SITE-C01",
      rel: "PARENT_CHILD",
      autoLr: "0.0005",
      ystrLr: "0.00",
      mtdnaLr: "0.00",
      jointLr: "5.00 × 10⁻⁴",
      log10: "-3.30",
      status: "EXCLUSION",
      action: "Definite exclusion from missing person reference pedigree.",
    },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Interpol DVI & Missing Persons Multi-Omic Reconciliation Engine
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Multi-Omic Joint LR (Auto STR • Y-STR • mtDNA • SNP) • Interpol DVI 4-Tier Statutory Decision Standard
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("missing")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "missing" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Missing Person Ranking
          </button>
          <button
            onClick={() => setActiveSubTab("dvi")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "dvi" ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Interpol DVI Matrix
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: Missing Persons Candidate Ranking ── */}
      {activeSubTab === "missing" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Query Profile ID</span>
              <p className="text-base font-bold text-amber-400 font-mono truncate">MP-QUERY-TURKEY-2026</p>
              <p className="text-[9px] text-zinc-400">Target missing person reference</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Database Candidates Searched</span>
              <p className="text-base font-bold text-tactical-text font-mono">12,480 Profiles</p>
              <p className="text-[9px] text-zinc-400">Cross-pedigree kinship scan complete</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Top Candidate LR</span>
              <p className="text-base font-bold text-emerald-400 font-mono">LR = 1,450,200.00</p>
              <p className="text-[9px] text-zinc-400">P(Hp | E) = 99.9999% (Parent-Child)</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 space-y-4 shadow-lg overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider leading-snug">
                Ranked Missing Person Kinship Candidate Matches
              </span>
              <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded shrink-0 self-start sm:self-auto">
                Prior P(Hp) = 0.50
              </span>
            </div>

            <div className="space-y-3">
              {missingCandidates.map((c, i) => (
                <div key={c.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 sm:p-4 rounded-xl bg-black/30 border border-tactical-border/40 gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400 font-bold text-xs font-mono">
                      #{i + 1}
                    </span>
                    <div className="min-w-0">
                      <p className="text-xs font-bold text-tactical-text font-mono truncate">{c.id}</p>
                      <p className="text-[9px] text-zinc-400 truncate">Hypothesis: <span className="text-indigo-400 font-bold">{c.rel}</span></p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center justify-between sm:justify-end gap-3 sm:gap-6 text-xs font-mono pt-2 sm:pt-0 border-t sm:border-t-0 border-tactical-border/20">
                    <div>
                      <p className="text-[9px] text-zinc-500">Likelihood Ratio</p>
                      <p className="font-bold text-emerald-400">{c.lr}</p>
                    </div>
                    <div>
                      <p className="text-[9px] text-zinc-500">Posterior Prob.</p>
                      <p className="font-bold text-amber-300">{c.prob}</p>
                    </div>
                    <span className={`px-2.5 py-1 rounded text-[9px] font-bold uppercase whitespace-nowrap ${
                      c.tier === "CONFIRMED_MATCH" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                    }`}>
                      {c.tier}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Interpol DVI Multi-Omic Reconciliation Matrix ── */}
      {activeSubTab === "dvi" && (
        <div className="space-y-6">
          {/* Interpol Decision Tier Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { tier: "Definitive Match", range: "LR ≥ 10⁶ (log₁₀ ≥ 6.0)", color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/5", desc: "Standalone legal identification" },
              { tier: "Probable Match", range: "10⁴ ≤ LR < 10⁶ (4.0–6.0)", color: "text-indigo-300 border-indigo-500/30 bg-indigo-500/5", desc: "Secondary corroboration required" },
              { tier: "Inconclusive", range: "10⁻² < LR < 10⁴ (-2.0–4.0)", color: "text-amber-400 border-amber-500/30 bg-amber-500/5", desc: "Additional STR / SNP panels required" },
              { tier: "Exclusion", range: "LR ≤ 10⁻² (log₁₀ ≤ -2.0)", color: "text-rose-400 border-rose-500/30 bg-rose-500/5", desc: "Definite pedigree exclusion" },
            ].map((t) => (
              <div key={t.tier} className={`rounded-xl border p-3 space-y-1 ${t.color}`}>
                <span className="text-[10px] font-bold uppercase">{t.tier}</span>
                <p className="text-xs font-bold font-mono">{t.range}</p>
                <p className="text-[9px] text-zinc-400">{t.desc}</p>
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 space-y-4 shadow-lg overflow-hidden">
            {/* Header Block */}
            <div className="flex flex-col gap-2.5 sm:gap-3 border-b border-tactical-border/40 pb-3.5">
              <span className="text-xs sm:text-sm font-bold text-tactical-text uppercase tracking-wider leading-snug">
                Multi-Omic Disaster Victim Cross-Reconciliation Matrix (LR_Joint)
              </span>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-[9px] sm:text-[10px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-lg whitespace-nowrap">
                  Interpol DVI Sec. 4
                </span>
                <span className="text-[9px] sm:text-[10px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg whitespace-nowrap">
                  Event: DVI-EVENT-TURKEY-2026
                </span>
              </div>
            </div>

            {/* Reconciliation Match Cards */}
            <div className="space-y-3">
              {dviMatrix.map((row) => (
                <div key={`${row.am}-${row.pm}`} className="flex flex-col p-3.5 sm:p-4 rounded-xl bg-black/30 border border-tactical-border/40 space-y-3 hover:border-amber-500/30 transition-all">
                  {/* Pair Header & Status Badge */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                    <div className="flex flex-wrap items-center gap-2 text-xs font-bold font-mono">
                      <span className="text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-1 rounded-lg">
                        {row.am}
                      </span>
                      <ChevronRight className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                      <span className="text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-lg">
                        {row.pm}
                      </span>
                    </div>
                    <span className={`px-2.5 py-1 rounded-lg text-[9px] font-bold uppercase font-mono w-fit shrink-0 whitespace-nowrap ${
                      row.status === "DEFINITIVE_IDENTIFICATION"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : row.status === "PROBABLE_MATCH"
                        ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                        : row.status === "INCONCLUSIVE"
                        ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        : "bg-rose-500/20 text-red-400 border border-rose-500/30"
                    }`}>
                      {row.status.replace(/_/g, " ")}
                    </span>
                  </div>

                  {/* Multi-omic breakdown metrics grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-[10px] font-mono">
                    <div className="bg-black/40 p-2.5 rounded-lg border border-tactical-border/30 space-y-0.5">
                      <span className="text-zinc-400 text-[9px] font-semibold block">Autosomal STR LR</span>
                      <p className="text-zinc-100 font-bold text-xs">{row.autoLr}</p>
                    </div>
                    <div className="bg-black/40 p-2.5 rounded-lg border border-tactical-border/30 space-y-0.5">
                      <span className="text-zinc-400 text-[9px] font-semibold block">Y-STR LR (1/p̂)</span>
                      <p className="text-cyan-300 font-bold text-xs">{row.ystrLr}</p>
                    </div>
                    <div className="bg-black/40 p-2.5 rounded-lg border border-tactical-border/30 space-y-0.5">
                      <span className="text-zinc-400 text-[9px] font-semibold block">mtDNA LR (1/p̂)</span>
                      <p className="text-purple-300 font-bold text-xs">{row.mtdnaLr}</p>
                    </div>
                    <div className="bg-emerald-500/10 p-2.5 rounded-lg border border-emerald-500/30 space-y-0.5">
                      <span className="text-emerald-400 text-[9px] font-semibold block">Combined LR_Joint</span>
                      <p className="text-emerald-300 font-bold text-xs">
                        {row.jointLr} <span className="text-[9px] font-normal text-emerald-400/80">(log={row.log10})</span>
                      </p>
                    </div>
                  </div>

                  <p className="text-[9px] text-zinc-400 italic pt-1 border-t border-tactical-border/20">
                    Judicial Action: {row.action}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

