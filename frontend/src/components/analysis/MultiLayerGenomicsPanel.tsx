"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Dna, Layers, ShieldCheck, Activity, RefreshCw, ChevronRight, CheckCircle2, AlertTriangle } from "lucide-react";

interface LayerDetail {
  layer_name: string;
  likelihood_ratio: number;
  log10_lr: number;
  exclusion_probability: number;
  status: string;
}

interface SynthesisResult {
  joint_likelihood_ratio: number;
  log10_joint_likelihood_ratio: number;
  joint_exclusion_probability: number;
  enfsi_verbal_predicate: string;
  active_layer_count: number;
  genomic_layers: LayerDetail[];
  architecture_provenance: string;
}

export default function MultiLayerGenomicsPanel() {
  const [lrStr, setLrStr] = useState<number>(1.0e12);
  const [lrSnp, setLrSnp] = useState<number>(1.0e3);
  const [lrMtdna, setLrMtdna] = useState<number>(1.0e2);
  const [lrYStr, setLrYStr] = useState<number>(1.0e4);
  const [lrWgs, setLrWgs] = useState<number>(1.0e5);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SynthesisResult | null>({
    joint_likelihood_ratio: 1.0e26,
    log10_joint_likelihood_ratio: 26.0,
    joint_exclusion_probability: 0.999999999,
    enfsi_verbal_predicate: "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION",
    active_layer_count: 5,
    genomic_layers: [
      { layer_name: "AUTOSOMAL_STR", likelihood_ratio: 1.0e12, log10_lr: 12.0, exclusion_probability: 0.999999, status: "ACTIVE_EVIDENCE" },
      { layer_name: "FORENSIC_SNP", likelihood_ratio: 1.0e3, log10_lr: 3.0, exclusion_probability: 0.995, status: "ACTIVE_EVIDENCE" },
      { layer_name: "MATERNAL_MTDNA", likelihood_ratio: 1.0e2, log10_lr: 2.0, exclusion_probability: 0.990, status: "ACTIVE_EVIDENCE" },
      { layer_name: "PATERNAL_Y_STR", likelihood_ratio: 1.0e4, log10_lr: 4.0, exclusion_probability: 0.998, status: "ACTIVE_EVIDENCE" },
      { layer_name: "WHOLE_GENOME_WGS", likelihood_ratio: 1.0e5, log10_lr: 5.0, exclusion_probability: 0.9999, status: "ACTIVE_EVIDENCE" },
    ],
    architecture_provenance: "FORENZA 5-Tier Multi-Omic Genomic Synthesizer"
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runSynthesis = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/genomics/synthesize-layers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lr_str: lrStr,
          lr_snp: lrSnp,
          lr_mtdna: lrMtdna,
          lr_y_str: lrYStr,
          lr_wgs: lrWgs
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error("Genomic layer synthesis request failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-cyan-500/30 bg-cyan-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-300">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Multi-Layered Forensic Genomics Architecture
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                5-TIER MULTI-OMIC
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              STR → SNP → mtDNA → Y-Chromosome → Whole Genome (WGS) Synthesizer
            </p>
          </div>
        </div>

        <button
          onClick={runSynthesis}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Synthesize Multi-Omic Layers
        </button>
      </div>

      {/* ── 5-Tier Architecture Visualizer ── */}
      <div className="p-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 space-y-3">
        <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
          5-Tier Genetic Evidence Flow & Linkage Independence Matrix
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 text-center">
          {[
            { tier: "TIER 1", name: "Autosomal STR", code: "CODIS 24", icon: Dna, color: "text-cyan-400 border-cyan-500/30 bg-cyan-500/10" },
            { tier: "TIER 2", name: "Forensic SNP", code: "HIrisPlex-S", icon: Activity, color: "text-purple-400 border-purple-500/30 bg-purple-500/10" },
            { tier: "TIER 3", name: "Lineage mtDNA", code: "rCRS HV1-3", icon: Layers, color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10" },
            { tier: "TIER 4", name: "Paternal Y-STR", code: "Y-FILER 23", icon: Dna, color: "text-amber-400 border-amber-500/30 bg-amber-500/10" },
            { tier: "TIER 5", name: "Deep WGS", code: "INDEL/CNV", icon: ShieldCheck, color: "text-indigo-400 border-indigo-500/30 bg-indigo-500/10" },
          ].map((t) => (
            <div key={t.tier} className={`p-3 rounded-xl border ${t.color} flex flex-col items-center justify-center gap-1`}>
              <t.icon className="w-4 h-4 mb-0.5" />
              <span className="text-[8px] text-zinc-400 uppercase font-bold">{t.tier}</span>
              <span className="text-xs font-bold font-mono">{t.name}</span>
              <span className="text-[9px] font-mono text-zinc-500">{t.code}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Main Layout: Controls & Output ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Layer Likelihood Ratio Controls */}
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
              Genomic Layer LR Weights (log10 Scale)
            </span>
          </div>

          <div className="space-y-3.5">
            {[
              { label: "Autosomal STR (LR_STR)", val: lrStr, setter: setLrStr, defaultLog: 12 },
              { label: "Forensic SNP (LR_SNP)", val: lrSnp, setter: setLrSnp, defaultLog: 3 },
              { label: "Maternal mtDNA (LR_mtDNA)", val: lrMtdna, setter: setLrMtdna, defaultLog: 2 },
              { label: "Paternal Y-STR (LR_Y)", val: lrYStr, setter: setLrYStr, defaultLog: 4 },
              { label: "Whole Genome WGS (LR_WGS)", val: lrWgs, setter: setLrWgs, defaultLog: 5 },
            ].map((layer) => (
              <div key={layer.label} className="space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-bold text-zinc-300">{layer.label}</span>
                  <span className="font-mono text-cyan-400 font-bold">10^{Math.log10(maxOne(layer.val)).toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="15"
                  step="0.5"
                  value={Math.log10(maxOne(layer.val))}
                  onChange={(e) => layer.setter(Math.pow(10, parseFloat(e.target.value)))}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Right 2-Cols: Synthesized Output & ENFSI Verdict */}
        <div className="lg:col-span-2 space-y-6">
          {result && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              {/* Synthesized Joint Verdict Card */}
              <div className="rounded-2xl border border-cyan-500/40 bg-gradient-to-br from-cyan-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl relative overflow-hidden">
                <div className="flex items-center justify-between border-b border-cyan-500/20 pb-4">
                  <div>
                    <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-widest block">
                      SYNTHESIZED MULTI-OMIC LIKELIHOOD RATIO
                    </span>
                    <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-teal-300 to-emerald-300 font-mono">
                      10^{result.log10_joint_likelihood_ratio}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-zinc-400 block uppercase font-bold">ENFSI Verbal Predicate</span>
                    <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold text-xs uppercase font-mono tracking-wider inline-block mt-1">
                      {result.enfsi_verbal_predicate.replace(/_/g, " ")}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-2">
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Active Tiers Evaluated</span>
                    <span className="font-bold text-cyan-300 font-mono">{result.active_layer_count} / 5 Tiers</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Joint Exclusion (PE_joint)</span>
                    <span className="font-bold text-emerald-400 font-mono">{(result.joint_exclusion_probability * 100).toFixed(6)}%</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 col-span-2 sm:col-span-1">
                    <span className="text-[10px] text-zinc-500 block">Linkage Assumption</span>
                    <span className="font-bold text-purple-300 font-mono">LINKAGE EQUILIBRIUM</span>
                  </div>
                </div>
              </div>

              {/* Layer-by-Layer Contribution Table */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-3 shadow-xl">
                <h3 className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                  <Activity className="w-4 h-4 text-cyan-400" />
                  Layer-by-Layer Multi-Omic Contribution Breakdown
                </h3>

                <div className="divide-y divide-tactical-border/30">
                  {result.genomic_layers.map((l) => (
                    <div key={l.layer_name} className="py-2.5 flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-zinc-200">{l.layer_name.replace(/_/g, " ")}</span>
                        <span className="px-1.5 py-0.5 rounded text-[8px] font-bold bg-zinc-800 text-zinc-400 border border-zinc-700">
                          {l.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-cyan-400 font-bold">10^{l.log10_lr}</span>
                        <span className="text-zinc-500 text-[10px]">PE: {(l.exclusion_probability * 100).toFixed(2)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </div>

      </div>
    </div>
  );
}

function maxOne(v: number): number {
  return v < 1 ? 1 : v;
}
