"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Clock, Dna, Activity, Sliders, AlertCircle, CheckCircle2, ShieldCheck, RefreshCw } from "lucide-react";

interface CpgContribution {
  locus: string;
  methylation_beta: number;
  weight: number;
  contribution_years: number;
}

interface AgePredictionResult {
  estimated_age_years: number;
  prediction_interval_lower: number;
  prediction_interval_upper: number;
  standard_error_years: number;
  expanded_uncertainty_95: number;
  tissue_type: string;
  tissue_offset_applied: number;
  age_acceleration_delta: number | null;
  aging_status: string;
  cpg_locus_contributions: CpgContribution[];
  model_provenance: string;
}

export default function AgeEstimationPanel() {
  const [tissueType, setTissueType] = useState<string>("BLOOD");
  const [knownAge, setKnownAge] = useState<string>("");
  const [cpgBetas, setCpgBetas] = useState<Record<string, number>>({
    ELOVL2: 0.45,
    FHL2: 0.35,
    TRIM59: 0.25,
    KLF14: 0.60,
    MIR29B2CHG: 0.30
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgePredictionResult | null>({
    estimated_age_years: 31.2,
    prediction_interval_lower: 24.8,
    prediction_interval_upper: 37.6,
    standard_error_years: 3.2,
    expanded_uncertainty_95: 6.4,
    tissue_type: "BLOOD",
    tissue_offset_applied: 0.0,
    age_acceleration_delta: 1.2,
    aging_status: "NORMAL_AGING",
    cpg_locus_contributions: [
      { locus: "ELOVL2", methylation_beta: 0.45, weight: 52.4, contribution_years: 23.58 },
      { locus: "FHL2", methylation_beta: 0.35, weight: 38.6, contribution_years: 13.51 },
      { locus: "TRIM59", methylation_beta: 0.25, weight: 29.8, contribution_years: 7.45 },
      { locus: "KLF14", methylation_beta: 0.60, weight: -18.5, contribution_years: -11.10 },
      { locus: "MIR29B2CHG", methylation_beta: 0.30, weight: 24.1, contribution_years: 7.23 }
    ],
    model_provenance: "Horvath-Hannum ElasticNet 5-CpG Forensic Standard"
  });

  const handleSliderChange = (locus: string, val: number) => {
    setCpgBetas((prev) => ({ ...prev, [locus]: val }));
  };

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runPrediction = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/predict-age`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cpg_methylation: cpgBetas,
          tissue_type: tissueType,
          chronological_age_known: knownAge ? parseFloat(knownAge) : null
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error("Age estimation request failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header Banner ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl border border-purple-500/30 bg-purple-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-300">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Epigenetic Clock & Age Estimation Engine
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                CpG METHYLATION
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Horvath ElasticNet Multivariate Model • 95% Prediction Interval • ISO 17025 Calibrated
            </p>
          </div>
        </div>

        <button
          onClick={runPrediction}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-purple-500 hover:bg-purple-400 text-black font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Predict Epigenetic Age
        </button>
      </div>

      {/* ── Main Layout: Controls & Dashboard ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: CpG Beta Inputs */}
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                CpG Methylation Ratios (Beta)
              </span>
            </div>
          </div>

          {/* Tissue Type Selection */}
          <div className="space-y-1.5">
            <label className="text-[10px] text-zinc-400 block font-bold uppercase">Biological Tissue Type</label>
            <select
              value={tissueType}
              onChange={(e) => setTissueType(e.target.value)}
              className="w-full bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-purple-300 font-bold focus:outline-none focus:border-purple-500"
            >
              <option value="BLOOD">Peripheral Blood (Baseline Offset: 0.0 yrs)</option>
              <option value="BUCCAL">Buccal Swab (+1.2 yrs)</option>
              <option value="SALIVA">Saliva (-0.8 yrs)</option>
              <option value="BONE">Skeletal Bone (+2.1 yrs)</option>
              <option value="TEETH">Dental Pulp (+2.5 yrs)</option>
            </select>
          </div>

          {/* Known Age Input for Acceleration Delta */}
          <div className="space-y-1.5 pt-2 border-t border-tactical-border/30">
            <label className="text-[10px] text-zinc-400 block font-bold uppercase">Known Chronological Age (Optional)</label>
            <input
              type="number"
              placeholder="e.g. 30.0"
              value={knownAge}
              onChange={(e) => setKnownAge(e.target.value)}
              className="w-full bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-purple-300 font-bold focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* 5-CpG Sliders */}
          <div className="space-y-3.5 pt-3 border-t border-tactical-border/30">
            {Object.entries(cpgBetas).map(([locus, betaVal]) => (
              <div key={locus} className="space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-bold text-zinc-300">{locus}</span>
                  <span className="font-mono text-purple-400 font-bold">Beta = {betaVal.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={betaVal}
                  onChange={(e) => handleSliderChange(locus, parseFloat(e.target.value))}
                  className="w-full accent-purple-500 cursor-pointer"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Right 2-Cols: Prediction Output & Analysis */}
        <div className="lg:col-span-2 space-y-6">
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Estimated Age Card */}
              <div className="rounded-2xl border border-purple-500/40 bg-gradient-to-br from-purple-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl relative overflow-hidden">
                <div className="flex items-center justify-between border-b border-purple-500/20 pb-4">
                  <div>
                    <span className="text-[10px] font-bold text-purple-300 uppercase tracking-widest block">
                      CHRONOLOGICAL AGE ESTIMATE
                    </span>
                    <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-teal-300 to-emerald-300 font-mono">
                      {result.estimated_age_years} Years
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-zinc-400 block uppercase font-bold">95% Prediction Interval</span>
                    <span className="text-sm font-bold text-emerald-400 font-mono">
                      [{result.prediction_interval_lower} - {result.prediction_interval_upper} Years]
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-2">
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Std Error (SE)</span>
                    <span className="font-bold text-purple-300 font-mono">±{result.standard_error_years} Years</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Expanded U95% (k=2)</span>
                    <span className="font-bold text-cyan-300 font-mono">±{result.expanded_uncertainty_95} Years</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 col-span-2 sm:col-span-1">
                    <span className="text-[10px] text-zinc-500 block">Aging Acceleration</span>
                    <span className="font-bold text-emerald-400 font-mono">
                      {result.age_acceleration_delta !== null
                        ? `${result.age_acceleration_delta > 0 ? "+" : ""}${result.age_acceleration_delta} yrs`
                        : "N/A"}
                    </span>
                  </div>
                </div>
              </div>

              {/* CpG Locus Contribution Table */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-3 shadow-xl">
                <h3 className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                  <Activity className="w-4 h-4 text-cyan-400" />
                  CpG Locus Model Contributions
                </h3>

                <div className="divide-y divide-tactical-border/30">
                  {result.cpg_locus_contributions.map((c) => (
                    <div key={c.locus} className="py-2.5 flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-zinc-200">{c.locus}</span>
                        <span className="text-[10px] text-zinc-500">(w = {c.weight})</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-zinc-400">Beta = {c.methylation_beta}</span>
                        <span className={`font-bold ${c.contribution_years >= 0 ? "text-emerald-400" : "text-amber-400"}`}>
                          {c.contribution_years >= 0 ? "+" : ""}{c.contribution_years} yrs
                        </span>
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
