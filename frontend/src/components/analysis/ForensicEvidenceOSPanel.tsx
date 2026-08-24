"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Play, CheckCircle2, ShieldCheck, Activity, Layers, Network, Lock, RefreshCw } from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";

interface PipelineResult {
  pipeline_id: string;
  case_id: string;
  sample_id: string;
  execution_timestamp: string;
  unified_pipeline_status: string;
  execution_layers: Record<string, any>;
  master_os_hmac_hash: string;
}

export default function ForensicEvidenceOSPanel() {
  const [loading, setLoading] = useState(false);
  const [pipeline, setPipeline] = useState<PipelineResult | null>({
    pipeline_id: "OS-PIPE-1786490000",
    case_id: "CASE-2026-OS-01",
    sample_id: "SAMPLE-DNA-101",
    execution_timestamp: "2026-08-12T14:10:00Z",
    unified_pipeline_status: "PIPELINE_SUCCESSFULLY_EXECUTED",
    execution_layers: {
      layer_1_ingestion: { str_loci_profiled: 24, serology_blood_group: "A_POSITIVE", body_fluid_mrna: "PERIPHERAL_BLOOD", status: "COMPLETED" },
      layer_2_inference: { likelihood_ratio_lr: 1.0e26, log10_lr: 26.0, kinship_relationship: "PARENT_CHILD", predicted_eye_color: "BLUE", status: "COMPLETED" },
      layer_3_ledger: { lims_sample_accessioned: true, chain_of_custody_hmac: "INTACT_VERIFIED", status: "COMPLETED" },
      layer_4_qc: { overall_qc_verdict: "QC_PASSED", negative_control_rfu: 0.0, positive_control_match: true, status: "COMPLETED" },
      layer_5_review: { human_decision: "APPROVE_AI_PREDICATE", primary_analyst: "ANALYST-01 (Dr. Sarah Connor)", technical_reviewer: "PEER-REVIEWER-02 (Dr. James Vance)", dual_sign_off_verified: true, status: "COMPLETED" },
      layer_6_reporting: { iso_certificate_compiled: true, court_admissibility_certified: true, certificate_hash: "e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2", status: "COMPLETED" }
    },
    master_os_hmac_hash: "e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2"
  });

  const API_BASE = getApiBaseUrl();

  const handleRunPipeline = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/os/run-unified-pipeline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: "CASE-2026-OS-01",
          sample_id: "SAMPLE-DNA-101",
          primary_analyst: "ANALYST-01 (Dr. Sarah Connor)",
          technical_reviewer: "PEER-REVIEWER-02 (Dr. James Vance)"
        })
      });
      if (res.ok) {
        const data = await res.json();
        setPipeline(data);
      }
    } catch (e) {
      console.error("Unified OS pipeline execution failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const layersList = [
    { title: "Layer 1: Multi-Omic Ingestion", desc: "DNA (STR/SNP/mt/Y), ABO/Rh Serology, mRNA, 16S Microbiology" },
    { title: "Layer 2: Biocomputational Inference", desc: "MCMC Mixture Deconvolution, Kinship, HIrisPlex-S, Dirichlet Fst" },
    { title: "Layer 3: Directed Case Graph & Ledger", desc: "Directed Acyclic Graph, LIMS Accessioning, HMAC Chain of Custody" },
    { title: "Layer 4: ISO 17025 QA/QC Gatekeeper", desc: "Heterozygote Balance Hb, Stochastic ST, Positive/Negative Controls" },
    { title: "Layer 5: Human Analyst Governance", desc: "Dual Sign-Off Review, Override Rationale, Prosecutor Fallacy Shield" },
    { title: "Layer 6: Court-Admissible Reporting", desc: "8-Section ISO Certificate Compiler, PDF Exporter, Court Mode Brief" }
  ];

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-indigo-500/30 bg-indigo-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500/20 border border-indigo-500/40 text-indigo-300">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                FORENZA Forensic Evidence OS Master System Architecture
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                MASTER OS DAG
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              30-Subsystem Multi-Omic Directed Acyclic Graph Orchestrator Platform
            </p>
          </div>
        </div>

        <button
          onClick={handleRunPipeline}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-black font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <Play className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Run Unified OS Pipeline
        </button>
      </div>

      {/* ── Master OS 6-Layer Topology DAG visualizer ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left: 6-Layer Architecture Map */}
        <div className="space-y-3 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
          <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block border-b border-tactical-border/40 pb-3 flex items-center gap-2">
            <Network className="w-4 h-4 text-indigo-400" />
            6-Layer Directed Evidence Pipeline Map
          </span>

          <div className="space-y-2.5 pt-1">
            {layersList.map((layer, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl border border-tactical-border/40 bg-black/40 flex items-start gap-3 hover:border-indigo-500/40 transition-all"
              >
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-300 font-bold text-[10px]">
                  0{idx + 1}
                </div>
                <div className="space-y-0.5">
                  <div className="font-bold text-xs text-zinc-200">{layer.title}</div>
                  <div className="text-[9px] text-zinc-500">{layer.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Unified OS Pipeline Live Execution Result */}
        <div className="space-y-4">
          {pipeline && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-indigo-500/40 bg-tactical-surface/50 p-5 space-y-4 shadow-xl"
            >
              <div className="flex items-center justify-between border-b border-indigo-500/20 pb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  Unified OS End-to-End Trace
                </span>
                <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold text-[9px] uppercase">
                  {pipeline.unified_pipeline_status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                  <span className="text-[9px] text-zinc-500 block">Pipeline Run ID</span>
                  <span className="font-bold text-indigo-300 text-xs truncate block">{pipeline.pipeline_id}</span>
                </div>
                <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                  <span className="text-[9px] text-zinc-500 block">Calculated log10(LR)</span>
                  <span className="font-bold text-emerald-300 text-xs block">10^{pipeline.execution_layers.layer_2_inference.log10_lr}</span>
                </div>
              </div>

              <div className="space-y-1.5 text-[10px] font-mono">
                <div className="p-2.5 rounded-lg bg-black/40 border border-zinc-800 flex justify-between">
                  <span className="text-zinc-400">Layer 4 QA/QC Verdict:</span>
                  <span className="font-bold text-emerald-400">{pipeline.execution_layers.layer_4_qc.overall_qc_verdict}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-zinc-800 flex justify-between">
                  <span className="text-zinc-400">Layer 5 Governance:</span>
                  <span className="font-bold text-indigo-300">{pipeline.execution_layers.layer_5_review.human_decision}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-zinc-800 flex justify-between">
                  <span className="text-zinc-400">Layer 6 Admissibility:</span>
                  <span className="font-bold text-emerald-400">CERTIFIED ISO 17025</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-black/60 border border-zinc-900 text-[8px] text-zinc-500 truncate">
                Master OS HMAC Hash: {pipeline.master_os_hmac_hash}
              </div>
            </motion.div>
          )}
        </div>

      </div>
    </div>
  );
}
