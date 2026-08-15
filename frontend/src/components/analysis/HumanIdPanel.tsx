"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Binary, Dna, ShieldAlert, FileText, CheckCircle2, ChevronRight, Activity, Cpu, Zap, AlertTriangle } from "lucide-react";

export default function HumanIdPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"multimodal" | "mapdamage" | "degradation">("mapdamage");

  // MapDamage Kinetics Curve Mock Data (Research §5.1, delta_0 = 0.25, alpha = 0.10)
  const mapDamageCurve = [
    { pos: 1, delta: "0.2500", label: "Terminal 5' Overhang (Max Deamination)" },
    { pos: 2, delta: "0.2262", label: "Sub-terminal Single-Strand" },
    { pos: 3, delta: "0.2047", label: "Single-Strand Transition" },
    { pos: 5, delta: "0.1676", label: "Intermediate Overhang" },
    { pos: 10, delta: "0.1016", label: "Double-Strand Boundary" },
    { pos: 15, delta: "0.0616", label: "Interior Read Base" },
    { pos: 20, delta: "0.0374", label: "Deep Core Nucleotide" },
    { pos: 25, delta: "0.0227", label: "Baseline Error Asymptote" },
  ];

  // Mock Low-Coverage SNP Panel (Research §5.2)
  const snpPanelResults = [
    { locus: "rs12913832 (HERC2)", reads: "4 reads (C, C, T*, C)", called: "AA (C/C)", posterior: "74.9%", deamRisk: "Active (k=2 T base compensated)", lr: "3.85" },
    { locus: "rs1800407 (OCA2)", reads: "6 reads (A, A, A, A, A, A)", called: "AA (A/A)", posterior: "99.8%", deamRisk: "None (Purine Allele)", lr: "4.12" },
    { locus: "rs16891982 (SLC45A2)", reads: "3 reads (G, G, A*)", called: "AA (G/G)", posterior: "82.4%", deamRisk: "Compensated (3' deamination)", lr: "3.40" },
    { locus: "rs1393350 (TYR)", reads: "5 reads (C, T, C, T, T)", called: "AB (C/T)", posterior: "96.5%", deamRisk: "True Heterozygote (interior reads)", lr: "5.10" },
  ];

  // Mock Multi-Modal Joint LR Candidates
  const candidates = [
    { id: "REF-INDIVIDUAL-701", str_lr: "12,400.00", ystr_lr: "120.00", mtdna_lr: "85.00", snp_lr: "275.40", joint_lr: "3.48 × 10¹⁰", log10: "10.54", prob: "99.9999%", verdict: "CONFIRMED_IDENTIFICATION" },
    { id: "REF-INDIVIDUAL-304", str_lr: "1,200.00", ystr_lr: "1.00", mtdna_lr: "85.00", snp_lr: "1.00", joint_lr: "102,000.00", log10: "5.01", prob: "99.9990%", verdict: "PROBABLE_MATCH" },
    { id: "REF-INDIVIDUAL-088", str_lr: "15.00", ystr_lr: "1.00", mtdna_lr: "1.00", snp_lr: "1.00", joint_lr: "15.00", log10: "1.18", prob: "93.7500%", verdict: "INCONCLUSIVE" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
            <Binary className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Ancient DNA & Degraded Forensic SNP / Human ID (HID) Engine
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              MapDamage / Briggs Deamination Kinetics • Low-Coverage Genotype Likelihoods • Skeletal Degradation Audit
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("mapdamage")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "mapdamage" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            MapDamage & aDNA
          </button>
          <button
            onClick={() => setActiveSubTab("multimodal")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "multimodal" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Micro-SNP & Joint LR
          </button>
          <button
            onClick={() => setActiveSubTab("degradation")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "degradation" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Skeletal Degradation
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: MapDamage & Ancient DNA Kinetics ── */}
      {activeSubTab === "mapdamage" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Terminal Deamination (δ₀)</span>
              <p className="text-xl font-bold text-cyan-400 font-mono">δ₀ = 0.2500</p>
              <p className="text-[9px] text-zinc-400">25.0% C→T deamination at 5' overhang</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Decay Parameter (α)</span>
              <p className="text-xl font-bold text-indigo-300 font-mono">α = 0.10 bp⁻¹</p>
              <p className="text-[9px] text-zinc-400">Exponential damage spatial decay rate</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Mean Fragment Length</span>
              <p className="text-xl font-bold text-amber-400 font-mono">L̄ = 70.0 bp</p>
              <p className="text-[9px] text-zinc-400">λ = 0.025, L_min = 30.0 bp</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">STR Dropout Risk (&lt;100bp)</span>
              <p className="text-xl font-bold text-rose-400 font-mono">82.6% Dropout</p>
              <p className="text-[9px] text-zinc-400">Standard multiplex PCR will fail</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                MapDamage / Briggs Post-Mortem Deamination Kinetics Curve (δ_k = δ₀ · e^(-α(k-1)))
              </span>
              <span className="text-[9px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
                Position-Dependent Deamination
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              {mapDamageCurve.map((point) => (
                <div key={point.pos} className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1 font-mono">
                  <div className="flex justify-between items-center text-xs font-bold">
                    <span className="text-zinc-400">Position k = {point.pos}</span>
                    <span className="text-cyan-300">δ_k = {point.delta}</span>
                  </div>
                  <p className="text-[9px] text-zinc-500">{point.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Micro-SNP & Multi-Modal Joint LR ── */}
      {activeSubTab === "multimodal" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Low-Coverage Forensic SNP Genotype Likelihoods (Damage-Compensated)
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                40–70 bp Short Amplicons
              </span>
            </div>

            <div className="space-y-3">
              {snpPanelResults.map((snp) => (
                <div key={snp.locus} className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-xl bg-black/20 border border-tactical-border/40 gap-3 font-mono">
                  <div>
                    <span className="text-xs font-bold text-cyan-400">{snp.locus}</span>
                    <p className="text-[10px] text-zinc-400">Observed: {snp.reads}</p>
                    <p className="text-[9px] text-zinc-500 italic">{snp.deamRisk}</p>
                  </div>
                  <div className="flex items-center gap-6 text-xs">
                    <div className="text-right">
                      <span className="text-[9px] text-zinc-500 block">Called Genotype</span>
                      <span className="font-bold text-indigo-300">{snp.called}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[9px] text-zinc-500 block">Posterior P(G|D)</span>
                      <span className="font-bold text-amber-300">{snp.posterior}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[9px] text-zinc-500 block">Locus LR</span>
                      <span className="font-bold text-emerald-400">{snp.lr}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Multi-Modal Candidate Identification Synthesis (STR • Y-STR • mtDNA • SNP)
              </span>
              <span className="text-[9px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
                Joint Product Rule Active
              </span>
            </div>

            <div className="space-y-3">
              {candidates.map((c, i) => (
                <div key={c.id} className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-3 font-mono">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-tactical-border/20 pb-2">
                    <div className="flex items-center gap-3">
                      <span className="flex h-6 w-6 items-center justify-center rounded bg-cyan-500/20 text-cyan-400 font-bold text-xs">
                        #{i + 1}
                      </span>
                      <span className="text-xs font-bold text-tactical-text">{c.id}</span>
                    </div>
                    <span className="text-xs font-bold text-emerald-400">
                      LR_Joint = {c.joint_lr} (log₁₀ = {c.log10})
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px]">
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">Partial STR LR</span>
                      <span className="font-bold text-indigo-300">{c.str_lr}</span>
                    </div>
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">Y-STR LR (1/p̂)</span>
                      <span className="font-bold text-indigo-300">{c.ystr_lr}</span>
                    </div>
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">mtDNA LR (1/p̂)</span>
                      <span className="font-bold text-indigo-300">{c.mtdna_lr}</span>
                    </div>
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">Micro-SNP LR</span>
                      <span className="font-bold text-cyan-300">{c.snp_lr}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 3: Skeletal Degradation Audit ── */}
      {activeSubTab === "degradation" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Skeletal Loci Degradation & Low-Copy-Number (LCN) PCR Audit
              </span>
              <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                LCN Threshold Detected (&lt;100 pg)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block text-[10px] uppercase font-bold">Degradation Index (DI = RFU_small / RFU_large)</span>
                <p className="text-lg font-bold text-amber-400">DI = 3.429 (Severe Degradation)</p>
                <p className="text-[10px] text-zinc-400">Small Loci RFU: 1200 • Large Loci RFU: 350. Severe &gt;300 bp amplicon dropout.</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block text-[10px] uppercase font-bold">Recommended Technology</span>
                <p className="text-sm font-bold text-cyan-300">MICRO_SNP_PANEL_40_70BP</p>
                <p className="text-[10px] text-zinc-400">Short-amplicon targeted micro-SNP sequencing is mandated for this bone fragment.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

