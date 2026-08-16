"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Clock, Dna, Activity, Sliders, Layers, RefreshCw, Flame, Sun, Droplets, ShieldCheck, CheckCircle2 } from "lucide-react";
import AgeEstimationPanel from "./AgeEstimationPanel";

interface TissueDeconvResult {
  top_predicted_tissue: string;
  top_tissue_probability: number;
  tissue_probabilities: Record<string, number>;
  lr_tissue: number;
  log10_lr_tissue: number;
  tdmr_loci_evaluated: number;
  deconvolution_method: string;
}

interface LifestyleResult {
  ahrr_methylation_beta: number;
  f2rl3_methylation_beta?: number;
  alppl2_methylation_beta?: number;
  smoking_score?: number;
  smoking_status: string;
  smoking_probability: number;
  estimated_pack_years: number;
  abcg1_methylation_beta?: number;
  cpt1a_methylation_beta?: number;
  srebf1_methylation_beta?: number;
  estimated_bmi?: number;
  bmi_category?: string;
  alcohol_index_score: number;
  alcohol_exposure_level: string;
  circadian_phase: string;
  estimated_tod_window: string;
  biomarker_panel: string;
}

export default function ComprehensiveEpigenomicsPanel() {
  const [activeResearchTab, setActiveResearchTab] = useState<"clock" | "tissue" | "lifestyle">("clock");

  // Tissue Deconvolution State (12 Diagnostic tDMR CpG Markers)
  const [tdmrBetas, setTdmrBetas] = useState<Record<string, number>>({
    cg09652652: 0.12,
    cg19406367: 0.15,
    cg17610929: 0.91,
    cg23521140: 0.85,
    cg26763284: 0.89,
    cg23576855: 0.84,
    cg00399818: 0.82,
    cg04382942: 0.88,
    cg11624633: 0.86,
    cg00854446: 0.82,
    cg18063373: 0.80,
    cg07823520: 0.90,
  });

  const tdmrLabels: Record<string, string> = {
    cg09652652: "Endothelial (cg09652652)",
    cg19406367: "Hematopoietic (cg19406367)",
    cg17610929: "Germ Cell (cg17610929)",
    cg23521140: "DACT1 (cg23521140)",
    cg26763284: "PRMT12 (cg26763284)",
    cg23576855: "Oral Epithelial (cg23576855)",
    cg00399818: "Salivary Gland (cg00399818)",
    cg04382942: "Cervicovaginal (cg04382942)",
    cg11624633: "MYO1G (cg11624633)",
    cg00854446: "Endometrial (cg00854446)",
    cg18063373: "Endometrial Stroma (cg18063373)",
    cg07823520: "Epidermis (cg07823520)",
  };

  const [deconvLoading, setDeconvLoading] = useState(false);
  const [deconvResult, setDeconvResult] = useState<TissueDeconvResult | null>({
    top_predicted_tissue: "BLOOD",
    top_tissue_probability: 0.9998,
    tissue_probabilities: {
      BLOOD: 0.9998,
      MENSTRUAL: 0.0002,
      SALIVA: 0.0000,
      VAGINAL: 0.0000,
      SKIN: 0.0000,
      SEMEN: 0.0000,
    },
    lr_tissue: 4999.0,
    log10_lr_tissue: 3.70,
    tdmr_loci_evaluated: 12,
    deconvolution_method: "Bayesian Quadratic Discriminant Analysis (QDA 12-tDMR Gaussian Mixture)"
  });

  // Lifestyle & Epigenetic Biomarkers State
  const [ahrrBeta, setAhrrBeta] = useState<number>(0.32);
  const [f2rl3Beta, setF2rl3Beta] = useState<number>(0.28);
  const [alppl2Beta, setAlppl2Beta] = useState<number>(0.30);
  const [abcg1Beta, setAbcg1Beta] = useState<number>(0.35);
  const [cpt1aBeta, setCpt1aBeta] = useState<number>(0.45);
  const [srebf1Beta, setSrebf1Beta] = useState<number>(0.30);
  const [slc6a3Beta, setSlc6a3Beta] = useState<number>(0.50);
  const [per2Beta, setPer2Beta] = useState<number>(0.40);
  const [bmal1Beta, setBmal1Beta] = useState<number>(0.60);

  const [lifestyleLoading, setLifestyleLoading] = useState(false);
  const [lifestyleResult, setLifestyleResult] = useState<LifestyleResult | null>({
    ahrr_methylation_beta: 0.32,
    f2rl3_methylation_beta: 0.28,
    alppl2_methylation_beta: 0.30,
    smoking_score: 6.12,
    smoking_status: "CURRENT_HEAVY_SMOKER",
    smoking_probability: 0.95,
    estimated_pack_years: 44.2,
    abcg1_methylation_beta: 0.35,
    cpt1a_methylation_beta: 0.45,
    srebf1_methylation_beta: 0.30,
    estimated_bmi: 24.4,
    bmi_category: "NORMAL_WEIGHT",
    alcohol_index_score: 0.0,
    alcohol_exposure_level: "LOW_OR_ABSTAINER",
    circadian_phase: "MATUTINAL_PEAK_MORNING",
    estimated_tod_window: "04:00 - 10:00 UTC",
    biomarker_panel: "AHRR + F2RL3 + ALPPL2 + ABCG1 + CPT1A + SREBF1 + SLC6A3 + PER2/BMAL1"
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runDeconvolution = async () => {
    setDeconvLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/deconvolve-tissue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tdmr_methylation: tdmrBetas })
      });
      if (res.ok) {
        const data = await res.json();
        setDeconvResult(data);
      }
    } catch (e) {
      console.error("Tissue deconvolution failed:", e);
    } finally {
      setDeconvLoading(false);
    }
  };

  const runLifestyleAnalysis = async () => {
    setLifestyleLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/lifestyle-profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ahrr_cg05575921_beta: ahrrBeta,
          f2rl3_beta: f2rl3Beta,
          alppl2_beta: alppl2Beta,
          abcg1_beta: abcg1Beta,
          cpt1a_beta: cpt1aBeta,
          srebf1_beta: srebf1Beta,
          slc6a3_beta: slc6a3Beta,
          per2_beta: per2Beta,
          bmal1_beta: bmal1Beta,
        })
      });
      if (res.ok) {
        const data = await res.json();
        setLifestyleResult(data);
      }
    } catch (e) {
      console.error("Lifestyle epigenetics analysis failed:", e);
    } finally {
      setLifestyleLoading(false);
    }
  };


  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-purple-500/30 bg-purple-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-300">
            <Dna className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Forensic Epigenomics & Biological State Intelligence
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                MULTI-OMICS EPIGENETICS
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              DNA Methylation • Epigenetic Clock • Tissue Deconvolution • AHRR Lifestyle Profiling
            </p>
          </div>
        </div>

        {/* Inner Navigation Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/60 border border-tactical-border/60">
          <button
            onClick={() => setActiveResearchTab("clock")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeResearchTab === "clock"
                ? "bg-purple-500 text-black shadow-md"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Epigenetic Clock
          </button>
          <button
            onClick={() => setActiveResearchTab("tissue")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeResearchTab === "tissue"
                ? "bg-purple-500 text-black shadow-md"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Tissue Deconvolution
          </button>
          <button
            onClick={() => setActiveResearchTab("lifestyle")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeResearchTab === "lifestyle"
                ? "bg-purple-500 text-black shadow-md"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Lifestyle & Environment
          </button>
        </div>
      </div>

      {/* ── Tab Content ── */}
      {activeResearchTab === "clock" && <AgeEstimationPanel />}

      {activeResearchTab === "tissue" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  tDMR Methylation Beta Inputs
                </span>
              </div>
              <button
                onClick={runDeconvolution}
                disabled={deconvLoading}
                className="px-3 py-1 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 font-bold text-[10px] uppercase transition-all flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${deconvLoading ? "animate-spin" : ""}`} />
                Deconvolve
              </button>
            </div>

            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {Object.entries(tdmrBetas).map(([locus, val]) => (
                <div key={locus} className="space-y-1">
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-bold text-zinc-300 truncate max-w-[170px]">{tdmrLabels[locus] || locus}</span>
                    <span className="font-mono text-purple-400 font-bold">β = {val.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.01"
                    value={val}
                    onChange={(e) => setTdmrBetas((prev) => ({ ...prev, [locus]: parseFloat(e.target.value) }))}
                    className="w-full accent-purple-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                  />
                </div>
              ))}
            </div>
          </div>


          {/* Results Display */}
          <div className="lg:col-span-2 space-y-6">
            {deconvResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                {/* Primary Verdict Card */}
                <div className="rounded-2xl border border-purple-500/40 bg-gradient-to-br from-purple-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-purple-500/20 pb-4">
                    <div>
                      <span className="text-[10px] font-bold text-purple-300 uppercase tracking-widest block">
                        PREDICTED TISSUE ORIGIN
                      </span>
                      <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-teal-300 to-emerald-300 font-mono">
                        {deconvResult.top_predicted_tissue}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">Tissue LR (LR_tissue)</span>
                      <span className="text-xl font-bold text-emerald-400 font-mono">
                        {deconvResult.lr_tissue} (10^{deconvResult.log10_lr_tissue})
                      </span>
                    </div>
                  </div>

                  {/* Probability Distribution Bar */}
                  <div className="space-y-3 pt-2">
                    <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">
                      Dirichlet Mixture Tissue Distribution
                    </span>
                    <div className="space-y-2">
                      {Object.entries(deconvResult.tissue_probabilities).map(([tissue, prob]) => (
                        <div key={tissue} className="space-y-1">
                          <div className="flex items-center justify-between text-xs font-mono">
                            <span className="font-bold text-zinc-300">{tissue}</span>
                            <span className="text-purple-300 font-bold">{(prob * 100).toFixed(1)}%</span>
                          </div>
                          <div className="h-2 w-full rounded-full bg-black/60 overflow-hidden border border-tactical-border/40">
                            <div
                              className="h-full bg-gradient-to-r from-purple-500 to-teal-400 rounded-full transition-all duration-500"
                              style={{ width: `${prob * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {activeResearchTab === "lifestyle" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Lifestyle & BMI Biomarkers
                </span>
              </div>
              <button
                onClick={runLifestyleAnalysis}
                disabled={lifestyleLoading}
                className="px-3 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-bold text-[10px] uppercase transition-all flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${lifestyleLoading ? "animate-spin" : ""}`} />
                Analyze
              </button>
            </div>

            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {/* Smoking Section */}
              <div className="text-[10px] font-bold text-amber-400 uppercase border-b border-tactical-border/30 pb-1">
                Smoking Markers (AHRR / F2RL3 / ALPPL2)
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">AHRR (cg05575921)</span>
                  <span className="font-mono text-amber-400 font-bold">β = {ahrrBeta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={ahrrBeta}
                  onChange={(e) => setAhrrBeta(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">F2RL3 (cg03636183)</span>
                  <span className="font-mono text-amber-400 font-bold">β = {f2rl3Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={f2rl3Beta}
                  onChange={(e) => setF2rl3Beta(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">ALPPL2 (cg01940273)</span>
                  <span className="font-mono text-amber-400 font-bold">β = {alppl2Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={alppl2Beta}
                  onChange={(e) => setAlppl2Beta(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>

              {/* BMI Section */}
              <div className="text-[10px] font-bold text-teal-400 uppercase border-b border-tactical-border/30 pb-1 pt-2">
                Epigenetic BMI (ABCG1 / CPT1A / SREBF1)
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">ABCG1 (cg06500161)</span>
                  <span className="font-mono text-teal-400 font-bold">β = {abcg1Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={abcg1Beta}
                  onChange={(e) => setAbcg1Beta(parseFloat(e.target.value))}
                  className="w-full accent-teal-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">CPT1A (cg00574958)</span>
                  <span className="font-mono text-teal-400 font-bold">β = {cpt1aBeta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={cpt1aBeta}
                  onChange={(e) => setCpt1aBeta(parseFloat(e.target.value))}
                  className="w-full accent-teal-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">SREBF1 (cg11024682)</span>
                  <span className="font-mono text-teal-400 font-bold">β = {srebf1Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={srebf1Beta}
                  onChange={(e) => setSrebf1Beta(parseFloat(e.target.value))}
                  className="w-full accent-teal-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div className="lg:col-span-2 space-y-6">
            {lifestyleResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <div className="rounded-2xl border border-amber-500/40 bg-gradient-to-br from-amber-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-amber-500/20 pb-4">
                    <div>
                      <span className="text-[10px] font-bold text-amber-300 uppercase tracking-widest block">
                        EPIGENETIC SMOKING BIOMARKER STATUS
                      </span>
                      <span className="text-2xl font-black text-amber-300 font-mono">
                        {lifestyleResult.smoking_status.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">Probability</span>
                      <span className="text-lg font-bold text-emerald-400 font-mono">
                        {(lifestyleResult.smoking_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Smoking Score</span>
                      <span className="font-bold text-amber-300 font-mono">{lifestyleResult.smoking_score ?? "N/A"}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Est. Pack Years</span>
                      <span className="font-bold text-amber-300 font-mono">{lifestyleResult.estimated_pack_years} Yrs</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Epigenetic BMI</span>
                      <span className="font-bold text-teal-300 font-mono">{lifestyleResult.estimated_bmi ?? 24.4} kg/m²</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">BMI Category</span>
                      <span className="font-bold text-teal-300 font-mono">{lifestyleResult.bmi_category ?? "NORMAL"}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-2">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Alcohol Exposure Level</span>
                      <span className="font-bold text-cyan-300 font-mono">{lifestyleResult.alcohol_exposure_level}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Circadian TOD Window</span>
                      <span className="font-bold text-purple-300 font-mono">{lifestyleResult.estimated_tod_window}</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </div>
  );

}
