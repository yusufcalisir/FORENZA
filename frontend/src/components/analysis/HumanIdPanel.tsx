"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Binary, Dna, ShieldAlert, FileText, CheckCircle2, ChevronRight, Activity, Cpu } from "lucide-react";

export default function HumanIdPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"multimodal" | "degradation">("multimodal");

  // Mock Multi-Modal Joint LR Candidates
  const candidates = [
    { id: "REF-INDIVIDUAL-701", str_lr: "12,400.00", ystr_lr: "120.00", mtdna_lr: "85.00", snp_lr: "15.00", joint_lr: "1,897,200,000.00", log10: "9.28", prob: "99.9999%", verdict: "CONFIRMED_IDENTIFICATION" },
    { id: "REF-INDIVIDUAL-304", str_lr: "1,200.00", ystr_lr: "1.00", mtdna_lr: "85.00", snp_lr: "1.00", joint_lr: "102,000.00", log10: "5.01", prob: "99.9990%", verdict: "STRONG_CANDIDATE" },
    { id: "REF-INDIVIDUAL-088", str_lr: "15.00", ystr_lr: "1.00", mtdna_lr: "1.00", snp_lr: "1.00", joint_lr: "15.00", log10: "1.18", prob: "93.7500%", verdict: "MODERATE_CANDIDATE" },
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
              Human Identification (HID) & Skeletal Remains Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Multi-Modal Evidence Synthesis (STR • Y-STR • mtDNA • SNP) • Skeletal Amplicon Degradation Audit
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("multimodal")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "multimodal" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Multi-Modal Joint LR
          </button>
          <button
            onClick={() => setActiveSubTab("degradation")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "degradation" ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Bone Degradation Audit
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: Multi-Modal Joint LR ── */}
      {activeSubTab === "multimodal" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Sample Case ID</span>
              <p className="text-base font-bold text-cyan-400 font-mono">UNKNOWN-SKELETAL-BONE-101</p>
              <p className="text-[9px] text-zinc-400">Femur bone fragment remain</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Synthesized Modalities</span>
              <p className="text-base font-bold text-tactical-text font-mono">STR + Y-STR + mtDNA + SNP</p>
              <p className="text-[9px] text-zinc-400">Joint independence product rule applied</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Joint Product LR</span>
              <p className="text-base font-bold text-emerald-400 font-mono">1,897,200,000.00</p>
              <p className="text-[9px] text-zinc-400">log10(LR_joint) = 9.28</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Ranked Candidate Identification Matches
              </span>
              <span className="text-[9px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
                Product Rule Active
              </span>
            </div>

            <div className="space-y-4">
              {candidates.map((c, i) => (
                <div key={c.id} className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-tactical-border/20 pb-2">
                    <div className="flex items-center gap-3">
                      <span className="flex h-6 w-6 items-center justify-center rounded bg-cyan-500/20 text-cyan-400 font-bold text-xs font-mono">
                        #{i + 1}
                      </span>
                      <span className="text-xs font-bold text-tactical-text font-mono">{c.id}</span>
                    </div>
                    <span className="text-xs font-bold text-emerald-400 font-mono">
                      LR_joint = {c.joint_lr} (log10 = {c.log10})
                    </span>
                  </div>

                  {/* Multi-modal breakdown grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px]">
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">Autosomal STR LR</span>
                      <span className="font-bold text-indigo-300 font-mono">{c.str_lr}</span>
                    </div>
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">Y-STR LR</span>
                      <span className="font-bold text-indigo-300 font-mono">{c.ystr_lr}</span>
                    </div>
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">mtDNA LR</span>
                      <span className="font-bold text-indigo-300 font-mono">{c.mtdna_lr}</span>
                    </div>
                    <div className="p-2 rounded bg-black/30 border border-tactical-border/30">
                      <span className="text-zinc-500 block">Phenotype SNP LR</span>
                      <span className="font-bold text-indigo-300 font-mono">{c.snp_lr}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Skeletal Degradation Audit ── */}
      {activeSubTab === "degradation" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Skeletal Loci Degradation & Low-Copy-Number (LCN) PCR Audit
              </span>
              <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                LCN Threshold Detected
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Degradation Index (RFU Small / RFU Large)</span>
                <p className="text-lg font-bold text-amber-400 font-mono">1.65 (Moderate Amplicon Decay)</p>
                <p className="text-[10px] text-zinc-400">Long amplicon loci (&gt;300bp) exhibit partial allele dropout risk.</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Recommended PCR Amplification Protocol</span>
                <p className="text-sm font-bold text-cyan-300">MiniSTR Short Amplicon Panel (&lt;200bp)</p>
                <p className="text-[10px] text-zinc-400">Increase PCR cycles by +4 cycles for LCN skeletal bone sample.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
