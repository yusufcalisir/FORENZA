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

  // Mock Interpol DVI AM/PM Reconciliation Matrix
  const dviMatrix = [
    { am: "AM-REF-FAMILY-01", pm: "PM-REMAIN-SITE-A01", rel: "PARENT_CHILD", lr: "2,840,000.00", status: "CONFIRMED_IDENTIFICATION" },
    { am: "AM-REF-FAMILY-02", pm: "PM-REMAIN-SITE-A04", rel: "PARENT_CHILD", lr: "185,400.00", status: "CONFIRMED_IDENTIFICATION" },
    { am: "AM-REF-FAMILY-03", pm: "PM-REMAIN-SITE-B02", rel: "PARENT_CHILD", lr: "1,250.00", status: "PROBABLE_IDENTIFICATION" },
    { am: "AM-REF-FAMILY-04", pm: "PM-REMAIN-SITE-C01", rel: "PARENT_CHILD", lr: "0.00", status: "EXCLUDED" },
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
              Missing Persons & Disaster Victim Identification (DVI) Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Pedigree Candidate Ranking • Interpol AM/PM Mass Casualty Cross-Reconciliation Matrix
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Query Profile ID</span>
              <p className="text-base font-bold text-amber-400 font-mono">MP-QUERY-TURKEY-2026</p>
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

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Ranked Missing Person Kinship Candidate Matches
              </span>
              <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                Prior P(Hp) = 0.50
              </span>
            </div>

            <div className="space-y-3">
              {missingCandidates.map((c, i) => (
                <div key={c.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-black/20 border border-tactical-border/40 gap-3">
                  <div className="flex items-center gap-3">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400 font-bold text-xs font-mono">
                      #{i + 1}
                    </span>
                    <div>
                      <p className="text-xs font-bold text-tactical-text font-mono">{c.id}</p>
                      <p className="text-[9px] text-zinc-400">Hypothesis: <span className="text-indigo-400 font-bold">{c.rel}</span></p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-xs font-mono">
                    <div className="text-right">
                      <p className="text-[9px] text-zinc-500">Likelihood Ratio</p>
                      <p className="font-bold text-emerald-400">{c.lr}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[9px] text-zinc-500">Posterior Prob.</p>
                      <p className="font-bold text-amber-300">{c.prob}</p>
                    </div>
                    <span className={`px-2.5 py-1 rounded text-[9px] font-bold uppercase ${
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

      {/* ── Sub-tab 2: Interpol DVI Reconciliation Matrix ── */}
      {activeSubTab === "dvi" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Interpol DVI Mass Casualty Reconciliation Matrix (Ante-Mortem vs Post-Mortem)
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                Event: DVI-EVENT-TURKEY-2026
              </span>
            </div>

            <div className="space-y-3">
              {dviMatrix.map((row) => (
                <div key={`${row.am}-${row.pm}`} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-black/20 border border-tactical-border/40 gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold font-mono">
                      <span className="text-indigo-400">{row.am}</span>
                      <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
                      <span className="text-amber-400">{row.pm}</span>
                    </div>
                    <p className="text-[9px] text-zinc-500">Hypothesis: {row.rel} • Combined LR = {row.lr}</p>
                  </div>

                  <div>
                    <span className={`px-3 py-1 rounded text-[9px] font-bold uppercase font-mono ${
                      row.status === "CONFIRMED_IDENTIFICATION"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : row.status === "PROBABLE_IDENTIFICATION"
                        ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                        : "bg-red-500/20 text-red-400 border border-red-500/30"
                    }`}>
                      {row.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
