"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, RefreshCw, Activity, Layers } from "lucide-react";

interface InspectionDimension {
  dimension: string;
  status: string;
  metric: string;
  threshold: string;
}

interface LocusQcDetail {
  locus: string;
  alleles: string[];
  peak_heights_rfu: number[];
  heterozygote_balance_hb: number;
  min_rfu: number;
  locus_status: string;
}

interface QcResult {
  sample_id: string;
  overall_qc_verdict: string;
  action_recommendation: string;
  quality_inspection_matrix: InspectionDimension[];
  locus_qc_details: LocusQcDetail[];
  total_loci_inspected: number;
  imbalanced_loci_count: number;
  stochastic_warning_count: number;
  iso_17025_provenance: string;
}

export default function QualityAssurancePanel() {
  const [ncRfu, setNcRfu] = useState<number>(0.0);
  const [pcMatch, setPcMatch] = useState<boolean>(true);
  const [loading, setLoading] = useState(false);

  const [result, setResult] = useState<QcResult | null>({
    sample_id: "SAMPLE-DNA-01",
    overall_qc_verdict: "QC_PASSED",
    action_recommendation: "PROCEED_TO_STATISTICAL_INTERPRETATION",
    quality_inspection_matrix: [
      { dimension: "NEGATIVE_CONTROL_INTEGRITY", status: "PASS", metric: "Max NC RFU: 0.0", threshold: "< 50.0 RFU" },
      { dimension: "POSITIVE_CONTROL_CONCORDANCE", status: "PASS", metric: "100% Match (9947A)", threshold: "100% Concordance" },
      { dimension: "HETEROZYGOTE_ALLELE_BALANCE", status: "PASS", metric: "0 Imbalanced Loci (Hb >= 0.60)", threshold: "Hb >= 0.60" },
      { dimension: "STOCHASTIC_THRESHOLDING", status: "PASS", metric: "0 Loci below ST (150.0 RFU)", threshold: ">= 150.0 RFU" },
      { dimension: "LOCUS_COMPLETION_RATE", status: "PASS", metric: "Completion: 100.0% (4 Loci)", threshold: ">= 90%" },
    ],
    locus_qc_details: [
      { locus: "D3S1358", alleles: ["15", "16"], peak_heights_rfu: [1200, 1150], heterozygote_balance_hb: 0.958, min_rfu: 1150, locus_status: "PASS" },
      { locus: "VWA", alleles: ["16", "17"], peak_heights_rfu: [950, 980], heterozygote_balance_hb: 0.969, min_rfu: 950, locus_status: "PASS" },
      { locus: "FGA", alleles: ["21", "24"], peak_heights_rfu: [1400, 1380], heterozygote_balance_hb: 0.986, min_rfu: 1380, locus_status: "PASS" },
      { locus: "D8S1179", alleles: ["13", "14"], peak_heights_rfu: [880, 850], heterozygote_balance_hb: 0.966, min_rfu: 850, locus_status: "PASS" },
    ],
    total_loci_inspected: 4,
    imbalanced_loci_count: 0,
    stochastic_warning_count: 0,
    iso_17025_provenance: "FORENZA QA/QC Gatekeeper Engine v1.0"
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const evaluateQc = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/qc/evaluate-profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sample_id: "SAMPLE-DNA-01",
          negative_control_max_rfu: ncRfu,
          positive_control_concordant: pcMatch
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error("QA/QC evaluation request failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-teal-500/30 bg-teal-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-teal-500/20 border border-teal-500/40 text-teal-300">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Forensic Quality Assurance & Quality Control (QA/QC) Gatekeeper
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
                ISO 17025 GATEKEEPER
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              7-Point Quality Inspection Matrix, Heterozygote Balance (Hb) & Control Verification
            </p>
          </div>
        </div>

        <button
          onClick={evaluateQc}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-black font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Run QA/QC Inspection
        </button>
      </div>

      {/* ── Control Input & Simulation Settings ── */}
      <div className="p-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 space-y-3">
        <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
          Control Sample Integrity Controls
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-zinc-300 font-bold">Negative Control Peak RFU</span>
              <span className="text-teal-400 font-bold">{ncRfu} RFU</span>
            </div>
            <input
              type="range"
              min="0"
              max="200"
              step="10"
              value={ncRfu}
              onChange={(e) => setNcRfu(parseFloat(e.target.value))}
              className="w-full accent-teal-500 cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl border border-tactical-border/40 bg-black/40 text-xs">
            <span className="font-bold text-zinc-300">Positive Control Concordance (9947A)</span>
            <button
              onClick={() => setPcMatch(!pcMatch)}
              className={`px-3 py-1 rounded-lg font-bold text-xs transition-all ${
                pcMatch ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "bg-red-500/20 text-red-300 border border-red-500/40"
              }`}
            >
              {pcMatch ? "MATCH (100%)" : "DISCORDANCE (FAIL)"}
            </button>
          </div>
        </div>
      </div>

      {/* ── Inspection Matrix & Locus Details ── */}
      {result && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Status Verdict Banner */}
          <div className={`p-5 rounded-2xl border ${
            result.overall_qc_verdict === "QC_PASSED"
              ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
              : result.overall_qc_verdict === "REVIEW_REQUIRED"
              ? "border-amber-500/40 bg-amber-500/10 text-amber-300"
              : "border-red-500/40 bg-red-500/10 text-red-300"
          } flex items-center justify-between`}>
            <div className="flex items-center gap-3">
              {result.overall_qc_verdict === "QC_PASSED" ? (
                <CheckCircle2 className="w-8 h-8 text-emerald-400" />
              ) : result.overall_qc_verdict === "REVIEW_REQUIRED" ? (
                <AlertTriangle className="w-8 h-8 text-amber-400" />
              ) : (
                <XCircle className="w-8 h-8 text-red-400" />
              )}
              <div>
                <span className="text-xs uppercase font-bold tracking-widest block opacity-70">ISO 17025 VERDICT</span>
                <span className="text-xl font-black tracking-wider">{result.overall_qc_verdict.replace(/_/g, " ")}</span>
              </div>
            </div>
            <span className="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-lg bg-black/40 border border-current">
              {result.action_recommendation.replace(/_/g, " ")}
            </span>
          </div>

          {/* 7-Point Inspection Matrix */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-3 shadow-xl">
            <h3 className="text-xs font-bold uppercase tracking-wider text-tactical-text border-b border-tactical-border/40 pb-3">
              Quality Inspection Matrix (7 Dimensions)
            </h3>
            <div className="divide-y divide-tactical-border/30">
              {result.quality_inspection_matrix.map((item, i) => (
                <div key={i} className="py-2.5 flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-zinc-200">{item.dimension.replace(/_/g, " ")}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-zinc-400 text-[11px]">{item.metric}</span>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                      item.status === "PASS"
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : "bg-red-500/20 text-red-300 border border-red-500/30"
                    }`}>
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
