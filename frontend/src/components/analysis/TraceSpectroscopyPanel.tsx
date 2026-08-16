"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Eye, ShieldCheck, RefreshCw, Layers, Activity, Zap, CheckCircle2, AlertTriangle, Filter } from "lucide-react";

interface MsiResponse {
  evidence_type: string;
  wavelength_nm: number;
  band_info: {
    wavelength_nm: number;
    band_name: string;
    phenomenon: string;
    target_evidence: string;
    mechanism: string;
    optimal_barrier_filter: string;
  };
  predicted_contrast_index: number;
  is_optimal_forensic_band: boolean;
}

interface MatchItem {
  material_name: string;
  hqi_score_percent: number;
  classification: string;
  evidence_strength: string;
  polymer_name: string;
  fiber_type: string;
  diagnostic_peaks_cm_1: number[];
}

interface SpectroscopyResponse {
  top_match: MatchItem | null;
  library_matches: MatchItem[];
  points_evaluated: number;
  prosecutors_fallacy_shield: string;
}

const MSI_PRESETS = [
  { id: "soret", name: "415 nm (Soret Band)", nm: 415, evidence: "Latent / Dilute Bloodstains", desc: "Maximum porphyrin ring absorption in hemoglobin." },
  { id: "uva", name: "365 nm (UV-A)", nm: 365, evidence: "Semen, Saliva, Vaginal Fluids", desc: "Fluorescence excitation of endogenous flavins & lipids." },
  { id: "blue", name: "450 nm (Blue Light)", nm: 450, evidence: "Latent Fingerprints & Trace Serology", desc: "530 nm long-pass filtered dye secondary fluorescence." },
  { id: "nir", name: "850 nm (Near-IR)", nm: 850, evidence: "Blood & GSR on Dark Textiles", desc: "Substrate transmission; fabric dyes become transparent." },
];

export default function TraceSpectroscopyPanel() {
  const [activeTab, setActiveTab] = useState<"msi" | "ftir">("ftir");
  const [selectedWavelength, setSelectedWavelength] = useState<number>(415);
  const [evidenceQuery, setEvidenceQuery] = useState<string>("Latent Bloodstain");
  const [selectedFiberPreset, setSelectedFiberPreset] = useState<string>("Polyester");
  const [loading, setLoading] = useState<boolean>(false);

  const [msiResult, setMsiResult] = useState<MsiResponse | null>({
    evidence_type: "Latent Bloodstain",
    wavelength_nm: 415,
    band_info: {
      wavelength_nm: 415,
      band_name: "Soret Band (415 nm)",
      phenomenon: "Peak Optical Absorption",
      target_evidence: "Latent / Dilute Bloodstains",
      mechanism: "Strong porphyrin ring absorption in hemoglobin",
      optimal_barrier_filter: "Monochromatic Neutral Density"
    },
    predicted_contrast_index: 0.98,
    is_optimal_forensic_band: true
  });

  const [spectroResult, setSpectroResult] = useState<SpectroscopyResponse | null>({
    top_match: {
      material_name: "Polyester",
      hqi_score_percent: 98.4,
      classification: "POSITIVE_SPECTRAL_MATCH",
      evidence_strength: "Definitive chemical identification (HQI >= 90.0%, P_false < 1e-4)",
      polymer_name: "Polyethylene Terephthalate (PET)",
      fiber_type: "Synthetic",
      diagnostic_peaks_cm_1: [1715.0, 1240.0, 1100.0, 725.0]
    },
    library_matches: [
      {
        material_name: "Polyester",
        hqi_score_percent: 98.4,
        classification: "POSITIVE_SPECTRAL_MATCH",
        evidence_strength: "Definitive chemical identification",
        polymer_name: "Polyethylene Terephthalate (PET)",
        fiber_type: "Synthetic",
        diagnostic_peaks_cm_1: [1715.0, 1240.0]
      },
      {
        material_name: "Nylon-6,6",
        hqi_score_percent: 42.1,
        classification: "NON_MATCH_EXCLUSION",
        evidence_strength: "Excluded (HQI < 75.0%)",
        polymer_name: "Polyamide 6,6",
        fiber_type: "Synthetic",
        diagnostic_peaks_cm_1: [1635.0, 1538.0]
      },
      {
        material_name: "Acrylic",
        hqi_score_percent: 31.5,
        classification: "NON_MATCH_EXCLUSION",
        evidence_strength: "Excluded (HQI < 75.0%)",
        polymer_name: "Polyacrylonitrile (PAN)",
        fiber_type: "Synthetic",
        diagnostic_peaks_cm_1: [2240.0]
      }
    ],
    points_evaluated: 100,
    prosecutors_fallacy_shield: "An HQI >= 90.0% provides definitive chemical polymer identification. Synthetic fibers are mass-manufactured (SWGMAT / ASTM E2228)."
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runMsiAnalysis = async (nm: number, ev: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/msi-optical-analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          evidence_type: ev,
          active_wavelength_nm: nm
        })
      });
      if (res.ok) {
        const data = await res.json();
        setMsiResult(data);
      }
    } catch (e) {
      console.error("MSI analysis failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const runSpectroscopyMatch = async (presetName: string) => {
    setLoading(true);
    try {
      // Synthesize 100-point spectrum based on preset
      const nPoints = 100;
      let targetPeaks = [1715.0, 1240.0];
      if (presetName === "Nylon-6,6") targetPeaks = [1635.0, 1538.0];
      if (presetName === "Acrylic") targetPeaks = [2240.0, 1450.0];
      if (presetName === "Cotton") targetPeaks = [3330.0, 1030.0];
      if (presetName === "Wool") targetPeaks = [1650.0, 1520.0];

      const sampleVec = Array.from({ length: nPoints }, (_, i) => {
        const wn = 400.0 + (i / (nPoints - 1)) * 3600.0;
        let intensity = 0.10;
        for (const peak of targetPeaks) {
          intensity += Math.exp(-Math.pow(wn - peak, 2) / (2.0 * 35.0 * 35.0));
        }
        return intensity;
      });

      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/ftir-raman-hqi-match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sample_spectrum: sampleVec })
      });

      if (res.ok) {
        const data = await res.json();
        setSpectroResult(data);
      }
    } catch (e) {
      console.error("Spectroscopy HQI matching failed:", e);
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
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold tracking-widest text-tactical-text uppercase">
                Trace Micro-Spectroscopy &amp; MSI Engine (Pillar 5 §4)
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 whitespace-nowrap">
                SWGMAT • ASTM E2228 • HQI ≥ 90%
              </span>
            </div>
            <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
              Multispectral Optical Imaging • ATR-FTIR &amp; Raman Hit Quality Index (HQI) Dot Product Matching
            </p>
          </div>
        </div>

        {/* Inner Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/60 border border-tactical-border/60 overflow-x-auto max-w-full shrink-0">
          <button
            onClick={() => setActiveTab("ftir")}
            className={`px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "ftir"
                ? "bg-cyan-500 text-black shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            ATR-FTIR &amp; Raman (HQI)
          </button>
          <button
            onClick={() => setActiveTab("msi")}
            className={`px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "msi"
                ? "bg-cyan-500 text-black shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Multispectral Optical (MSI)
          </button>
        </div>
      </div>

      {/* ── SubTab 1: ATR-FTIR & Raman HQI ── */}
      {activeTab === "ftir" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Unknown Sample & Polymer Selector */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                Questioned Fiber Sample
              </span>
              <button
                onClick={() => runSpectroscopyMatch(selectedFiberPreset)}
                disabled={loading}
                className="px-3 py-1 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-[10px] uppercase transition-all shadow-md flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                Match HQI
              </button>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] text-zinc-400 uppercase font-bold block">
                Load Standard Exemplar Spectrum:
              </label>
              <div className="grid grid-cols-1 gap-1.5 text-xs">
                {["Polyester", "Nylon-6,6", "Acrylic", "Cotton", "Wool"].map((fName) => (
                  <button
                    key={fName}
                    onClick={() => {
                      setSelectedFiberPreset(fName);
                      runSpectroscopyMatch(fName);
                    }}
                    className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                      selectedFiberPreset === fName
                        ? "border-cyan-500/80 bg-cyan-500/20 text-cyan-300 font-bold"
                        : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                    }`}
                  >
                    <div className="font-bold">{fName}</div>
                    <div className="text-[10px] text-zinc-500">
                      {fName === "Polyester" && "PET • 1715 cm⁻¹ (C=O), 1240 cm⁻¹ (C-O)"}
                      {fName === "Nylon-6,6" && "Polyamide • 1635 cm⁻¹ (Amide I), 1538 cm⁻¹ (Amide II)"}
                      {fName === "Acrylic" && "PAN • 2240 cm⁻¹ (Nitrile C≡N)"}
                      {fName === "Cotton" && "Cellulose • 3330 cm⁻¹ (O-H), 1030 cm⁻¹ (C-O)"}
                      {fName === "Wool" && "Keratin • 1650 cm⁻¹ (Amide I), 1520 cm⁻¹ (Amide II)"}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right: HQI Matching Results */}
          <div className="lg:col-span-2 space-y-4">
            {spectroResult && spectroResult.top_match && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-cyan-500/40 bg-gradient-to-br from-cyan-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-cyan-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-widest block">
                        HIT QUALITY INDEX (HQI) TOP MATCH
                      </span>
                      <span className="text-xl sm:text-2xl font-black text-cyan-300 font-mono">
                        {spectroResult.top_match.material_name} ({spectroResult.top_match.hqi_score_percent}%)
                      </span>
                    </div>
                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">Classification</span>
                      <span className={`text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded border font-mono whitespace-nowrap ${
                        spectroResult.top_match.classification === "POSITIVE_SPECTRAL_MATCH"
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                          : "bg-amber-500/20 text-amber-300 border-amber-500/40"
                      }`}>
                        {spectroResult.top_match.classification}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-0.5">
                      <span className="text-[10px] text-zinc-500 block">Polymer Name</span>
                      <span className="font-bold text-zinc-200">{spectroResult.top_match.polymer_name}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-0.5">
                      <span className="text-[10px] text-zinc-500 block">Fiber Class</span>
                      <span className="font-bold text-zinc-200">{spectroResult.top_match.fiber_type}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-0.5">
                      <span className="text-[10px] text-zinc-500 block">Diagnostic Wavenumbers</span>
                      <span className="font-bold text-cyan-400 font-mono text-[10px] block">
                        {spectroResult.top_match.diagnostic_peaks_cm_1?.join(", ")} cm⁻¹
                      </span>
                    </div>
                  </div>

                  {/* Library Matches Table */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                      Forensic Polymer Library Ranking:
                    </span>
                    {spectroResult.library_matches.map((lm) => (
                      <div
                        key={lm.material_name}
                        className="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 sm:p-3 rounded-lg bg-black/40 border border-tactical-border/40 text-xs font-mono gap-2 hover:border-cyan-500/30 transition-colors"
                      >
                        <div className="flex flex-wrap items-baseline gap-1.5 min-w-0">
                          <span className="font-bold text-zinc-200 text-xs">{lm.material_name}</span>
                          <span className="text-[10px] text-zinc-400">({lm.polymer_name})</span>
                        </div>
                        <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0 pt-1 sm:pt-0 border-t sm:border-t-0 border-tactical-border/20">
                          <span className={`text-xs font-bold font-mono ${
                            lm.hqi_score_percent >= 90.0 ? "text-emerald-400" : lm.hqi_score_percent >= 75.0 ? "text-amber-400" : "text-zinc-400"
                          }`}>
                            HQI = {lm.hqi_score_percent.toFixed(1)}%
                          </span>
                          <span className={`text-[9px] font-bold px-2 py-0.5 rounded border whitespace-nowrap ${
                            lm.classification === "POSITIVE_SPECTRAL_MATCH"
                              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                              : "bg-zinc-800/80 text-zinc-400 border-zinc-700/60"
                          }`}>
                            {lm.classification === "POSITIVE_SPECTRAL_MATCH" ? "MATCH" : "EXCLUDED"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-cyan-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                      SWGMAT / ASTM E2228 Legal Evaluative Shield
                    </div>
                    {spectroResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ── SubTab 2: Multispectral Optical Imaging (MSI) ── */}
      {activeTab === "msi" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: MSI Wavelength Band Presets */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                Targeted Optical Wavelength Bands
              </span>
            </div>

            <div className="space-y-2">
              {MSI_PRESETS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => {
                    setSelectedWavelength(p.nm);
                    setEvidenceQuery(p.evidence);
                    runMsiAnalysis(p.nm, p.evidence);
                  }}
                  className={`p-3 rounded-xl border text-left w-full transition-all cursor-pointer ${
                    selectedWavelength === p.nm
                      ? "border-cyan-500/80 bg-cyan-500/20 text-cyan-300 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-0.5">
                    <span>{p.name}</span>
                    <span className="text-[10px] text-cyan-400">{p.nm} nm</span>
                  </div>
                  <div className="text-[10px] text-zinc-300 font-normal">{p.evidence}</div>
                  <div className="text-[9px] text-zinc-500 font-normal mt-0.5">{p.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Right: MSI Contrast Mechanism Details */}
          <div className="lg:col-span-2 space-y-4">
            {msiResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-cyan-500/40 bg-gradient-to-br from-cyan-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-cyan-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-widest block">
                        OPTICAL CONTRAST SIMULATION
                      </span>
                      <span className="text-xl sm:text-2xl font-black text-cyan-300 font-mono">
                        {msiResult.band_info.band_name}
                      </span>
                    </div>
                    <div className="flex flex-col items-start sm:items-end">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">Predicted Contrast</span>
                      <span className="text-xl sm:text-2xl font-black text-emerald-400 font-mono">
                        {(msiResult.predicted_contrast_index * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-0.5">
                      <span className="text-[10px] text-zinc-500 block">Optical Phenomenon</span>
                      <span className="font-bold text-zinc-200">{msiResult.band_info.phenomenon}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-0.5">
                      <span className="text-[10px] text-zinc-500 block">Recommended Barrier Filter</span>
                      <span className="font-bold text-amber-300 font-mono text-xs">
                        {msiResult.band_info.optimal_barrier_filter}
                      </span>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1">
                    <span className="text-[10px] text-zinc-500 block uppercase">Physical Contrast Mechanism:</span>
                    <p className="text-zinc-300 leading-relaxed">{msiResult.band_info.mechanism}</p>
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
