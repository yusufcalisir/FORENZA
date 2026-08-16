"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Pill, Activity, ShieldCheck, RefreshCw, AlertTriangle, CheckCircle2, Clock, Zap, ArrowRight, Info } from "lucide-react";

interface PmrResponse {
  compound_name: string;
  c_heart: number;
  c_femoral: number;
  unit: string;
  cp_observed: number;
  cp_literature_mean: number;
  vd_l_kg: number;
  pmr_risk_tier: string;
  is_cardiac_overestimated: boolean;
  overestimation_percentage: number;
  clinical_guideline: string;
  alert_message: string;
  prosecutors_fallacy_shield: string;
}

interface ExtrapolationResponse {
  compound_name: string;
  c_femoral_postmortem: number;
  elapsed_hours: number;
  c_antemortem_extrapolated: number;
  unit: string;
  elimination_type: string;
  elimination_rate_constant_ke_h: number | null;
  half_life_hours: number | null;
  beta_60_g_l_h: number | null;
  kinetic_formula: string;
  prosecutors_fallacy_shield: string;
}

const DRUG_PRESETS = [
  { name: "Fentanyl", cHeart: 14.0, cFem: 5.0, unit: "µg/L", vd: 5.0, tHalf: 7.0, risk: "High / Severe" },
  { name: "Ethanol", cHeart: 0.85, cFem: 0.80, unit: "g/L", vd: 0.6, tHalf: null, risk: "Low / Minimal" },
  { name: "Morphine", cHeart: 0.36, cFem: 0.20, unit: "mg/L", vd: 3.5, tHalf: 3.0, risk: "Moderate" },
  { name: "Methamphetamine", cHeart: 0.84, cFem: 0.40, unit: "mg/L", vd: 4.0, tHalf: 10.0, risk: "High" },
  { name: "Amitriptyline", cHeart: 4.50, cFem: 1.00, unit: "mg/L", vd: 20.0, tHalf: 21.0, risk: "Very High" },
  { name: "Acetaminophen", cHeart: 10.5, cFem: 10.0, unit: "mg/L", vd: 0.9, tHalf: 2.5, risk: "Low" },
];

export default function ToxicologyPmrPanel() {
  const [activeTab, setActiveTab] = useState<"pmr" | "extrap">("pmr");
  const [selectedDrug, setSelectedDrug] = useState<string>("Fentanyl");
  const [cHeart, setCHeart] = useState<number>(14.0);
  const [cFemoral, setCFemoral] = useState<number>(5.0);
  const [unit, setUnit] = useState<string>("µg/L");
  const [elapsedHours, setElapsedHours] = useState<number>(7.0);
  const [loading, setLoading] = useState<boolean>(false);

  const [pmrResult, setPmrResult] = useState<PmrResponse | null>({
    compound_name: "Fentanyl",
    c_heart: 14.0,
    c_femoral: 5.0,
    unit: "µg/L",
    cp_observed: 2.8,
    cp_literature_mean: 2.8,
    vd_l_kg: 5.0,
    pmr_risk_tier: "High / Severe",
    is_cardiac_overestimated: true,
    overestimation_percentage: 180.0,
    clinical_guideline: "Pronounced post-mortem lung-to-heart diffusion; femoral venous blood mandatory.",
    alert_message: "HIGH PMR OVERESTIMATION ALERT: Heart blood concentration (14.0 µg/L) is 180.0% higher than peripheral femoral blood (5.0 µg/L).",
    prosecutors_fallacy_shield: "Post-mortem cardiac blood concentrations cannot be directly translated to antemortem intoxication levels (SOFT / TIAFT Guidelines)."
  });

  const [extrapResult, setExtrapResult] = useState<ExtrapolationResponse | null>({
    compound_name: "Fentanyl",
    c_femoral_postmortem: 5.0,
    elapsed_hours: 7.0,
    c_antemortem_extrapolated: 10.0,
    unit: "µg/L",
    elimination_type: "First-Order",
    elimination_rate_constant_ke_h: 0.09902,
    half_life_hours: 7.0,
    beta_60_g_l_h: null,
    kinetic_formula: "First-Order: C_antemortem = C_femoral * exp(0.09902 * 7.0h)",
    prosecutors_fallacy_shield: "Antemortem back-extrapolation assumes linear or exponential clearance in an uncompromised circulatory system (SOFT / TIAFT)."
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const loadPreset = (preset: typeof DRUG_PRESETS[0]) => {
    setSelectedDrug(preset.name);
    setCHeart(preset.cHeart);
    setCFemoral(preset.cFem);
    setUnit(preset.unit);
    runPmrEvaluation(preset.name, preset.cHeart, preset.cFem, preset.unit);
    runExtrapolation(preset.name, preset.cFem, elapsedHours, preset.unit);
  };

  const runPmrEvaluation = async (drug: string, heart: number, fem: number, u: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/toxicology-pmr-evaluation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          compound_name: drug,
          c_heart: heart,
          c_femoral: fem,
          unit: u
        })
      });
      if (res.ok) {
        const data = await res.json();
        setPmrResult(data);
      }
    } catch (e) {
      console.error("PMR evaluation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const runExtrapolation = async (drug: string, fem: number, hours: number, u: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/toxicology-antemortem-extrapolation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          compound_name: drug,
          c_femoral: fem,
          elapsed_hours: hours,
          unit: u
        })
      });
      if (res.ok) {
        const data = await res.json();
        setExtrapResult(data);
      }
    } catch (e) {
      console.error("Antemortem extrapolation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-rose-500/30 bg-rose-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-300">
            <Pill className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold tracking-widest text-tactical-text uppercase">
                Post-Mortem Toxicokinetics &amp; PMR Engine (Pillar 5 §5)
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 whitespace-nowrap">
                SOFT • TIAFT • C_heart/C_femoral
              </span>
            </div>
            <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
              Post-Mortem Drug Redistribution (PMR) • Widmark Zero-Order &amp; First-Order Back-Extrapolation
            </p>
          </div>
        </div>

        {/* Inner Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/60 border border-tactical-border/60 overflow-x-auto max-w-full shrink-0">
          <button
            onClick={() => setActiveTab("pmr")}
            className={`px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "pmr"
                ? "bg-rose-500 text-white shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            PMR Redistribution (C/P)
          </button>
          <button
            onClick={() => setActiveTab("extrap")}
            className={`px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
              activeTab === "extrap"
                ? "bg-rose-500 text-white shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Antemortem Extrapolation
          </button>
        </div>
      </div>

      {/* ── SubTab 1: PMR Evaluation ── */}
      {activeTab === "pmr" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Presets & Concentrations */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                Xenobiotic Presets
              </span>
              <button
                onClick={() => runPmrEvaluation(selectedDrug, cHeart, cFemoral, unit)}
                disabled={loading}
                className="px-3 py-1 rounded-lg bg-rose-500 hover:bg-rose-400 text-white font-bold text-[10px] uppercase transition-all shadow-md flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                Evaluate PMR
              </button>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] text-zinc-400 uppercase font-bold block">Select Case Compound:</label>
              <div className="grid grid-cols-2 gap-1.5 text-xs">
                {DRUG_PRESETS.map((p) => (
                  <button
                    key={p.name}
                    onClick={() => loadPreset(p)}
                    className={`p-2 rounded-xl border text-left transition-all cursor-pointer ${
                      selectedDrug === p.name
                        ? "border-rose-500/80 bg-rose-500/20 text-rose-300 font-bold"
                        : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                    }`}
                  >
                    <div className="font-bold">{p.name}</div>
                    <div className="text-[9px] text-zinc-500">Vd: {p.vd} L/kg • {p.risk}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3 pt-2 border-t border-tactical-border/30">
              <div>
                <label className="text-[10px] text-zinc-400 uppercase font-bold block mb-1">
                  Heart / Central Blood (C_heart):
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    step="0.01"
                    value={cHeart}
                    onChange={(e) => {
                      const v = parseFloat(e.target.value) || 0;
                      setCHeart(v);
                      runPmrEvaluation(selectedDrug, v, cFemoral, unit);
                    }}
                    className="w-full bg-black/60 border border-tactical-border/60 rounded-xl px-3 py-2 text-xs font-mono text-tactical-text focus:border-rose-500/60 focus:outline-none"
                  />
                  <span className="text-xs text-zinc-400 font-bold">{unit}</span>
                </div>
              </div>

              <div>
                <label className="text-[10px] text-zinc-400 uppercase font-bold block mb-1">
                  Peripheral Femoral Blood (C_femoral):
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    step="0.01"
                    value={cFemoral}
                    onChange={(e) => {
                      const v = parseFloat(e.target.value) || 0.01;
                      setCFemoral(v);
                      runPmrEvaluation(selectedDrug, cHeart, v, unit);
                    }}
                    className="w-full bg-black/60 border border-tactical-border/60 rounded-xl px-3 py-2 text-xs font-mono text-tactical-text focus:border-rose-500/60 focus:outline-none"
                  />
                  <span className="text-xs text-zinc-400 font-bold">{unit}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: PMR Analysis Output */}
          <div className="lg:col-span-2 space-y-4">
            {pmrResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-rose-500/40 bg-gradient-to-br from-rose-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-rose-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-rose-300 uppercase tracking-widest block">
                        OBSERVED C_HEART / C_FEMORAL (C/P) RATIO
                      </span>
                      <span className="text-3xl font-black text-rose-300 font-mono">
                        {pmrResult.cp_observed.toFixed(2)}x
                      </span>
                      <span className="text-[10px] text-zinc-400 block mt-0.5">
                        Literature Expected: {pmrResult.cp_literature_mean.toFixed(2)}x (Vd = {pmrResult.vd_l_kg} L/kg)
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">PMR Risk Tier</span>
                      <span className={`text-xs font-bold px-2.5 py-1 rounded border font-mono ${
                        pmrResult.pmr_risk_tier.includes("High")
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                          : pmrResult.pmr_risk_tier.includes("Moderate")
                          ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                          : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                      }`}>
                        {pmrResult.pmr_risk_tier}
                      </span>
                    </div>
                  </div>

                  {pmrResult.is_cardiac_overestimated ? (
                    <div className="p-3.5 rounded-xl bg-rose-500/20 border border-rose-500/40 text-xs font-mono space-y-1">
                      <div className="flex items-center gap-1.5 text-rose-300 font-bold">
                        <AlertTriangle className="w-4 h-4" />
                        CARDIAC BLOOD OVERESTIMATION ALERT
                      </div>
                      <p className="text-zinc-300 leading-relaxed">{pmrResult.alert_message}</p>
                    </div>
                  ) : (
                    <div className="p-3.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-xs font-mono space-y-1">
                      <div className="flex items-center gap-1.5 text-emerald-300 font-bold">
                        <CheckCircle2 className="w-4 h-4" />
                        UNIFORM / MINIMAL REDISTRIBUTION
                      </div>
                      <p className="text-zinc-300 leading-relaxed">{pmrResult.alert_message}</p>
                    </div>
                  )}

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1">
                    <span className="text-[10px] text-zinc-500 block uppercase">Analytical Interpretation Guideline:</span>
                    <p className="text-zinc-300 leading-relaxed">{pmrResult.clinical_guideline}</p>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      SOFT / TIAFT Legal Evaluative Shield
                    </div>
                    {pmrResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ── SubTab 2: Antemortem Back-Extrapolation ── */}
      {activeTab === "extrap" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Extrapolation Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                Kinetic Parameters
              </span>
              <button
                onClick={() => runExtrapolation(selectedDrug, cFemoral, elapsedHours, unit)}
                disabled={loading}
                className="px-3 py-1 rounded-lg bg-rose-500 hover:bg-rose-400 text-white font-bold text-[10px] uppercase transition-all shadow-md flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                Extrapolate
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-[10px] text-zinc-400 uppercase font-bold block mb-1">
                  Elapsed Hours Prior to Death (Δt):
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="48.0"
                  step="0.5"
                  value={elapsedHours}
                  onChange={(e) => {
                    const v = parseFloat(e.target.value);
                    setElapsedHours(v);
                    runExtrapolation(selectedDrug, cFemoral, v, unit);
                  }}
                  className="w-full accent-rose-500"
                />
                <div className="flex justify-between text-[10px] text-zinc-400 font-mono mt-1">
                  <span>0.5 h</span>
                  <span className="text-rose-400 font-bold">{elapsedHours.toFixed(1)} Hours Elapsed</span>
                  <span>48.0 h</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-zinc-500">Compound:</span>
                  <span className="font-bold text-zinc-200">{selectedDrug}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">C_femoral (t_0):</span>
                  <span className="font-bold text-zinc-200">{cFemoral} {unit}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Elimination:</span>
                  <span className="font-bold text-rose-300">
                    {selectedDrug === "Ethanol" ? "Zero-Order Widmark" : "First-Order Half-Life"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Extrapolation Results */}
          <div className="lg:col-span-2 space-y-4">
            {extrapResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-rose-500/40 bg-gradient-to-br from-rose-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-rose-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-rose-300 uppercase tracking-widest block">
                        ANTEMORTEM EXTRAPOLATED CONCENTRATION (t - {extrapResult.elapsed_hours}h)
                      </span>
                      <span className="text-3xl font-black text-rose-300 font-mono">
                        {extrapResult.c_antemortem_extrapolated} {extrapResult.unit}
                      </span>
                      <span className="text-[10px] text-zinc-400 block mt-0.5">
                        Post-Mortem Femoral Baseline: {extrapResult.c_femoral_postmortem} {extrapResult.unit}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">Kinetic Formula</span>
                      <span className="text-xs font-bold px-2 py-1 rounded bg-black/60 border border-tactical-border/60 text-zinc-300 font-mono">
                        {extrapResult.elimination_type}
                      </span>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1">
                    <span className="text-[10px] text-zinc-500 block uppercase">Kinematic Back-Projection Formula:</span>
                    <p className="text-rose-300 font-bold">{extrapResult.kinetic_formula}</p>
                    {extrapResult.elimination_rate_constant_ke_h && (
                      <p className="text-[10px] text-zinc-400">
                        Elimination Rate Constant (k_e): {extrapResult.elimination_rate_constant_ke_h} h⁻¹ (t_1/2 = {extrapResult.half_life_hours}h)
                      </p>
                    )}
                    {extrapResult.beta_60_g_l_h && (
                      <p className="text-[10px] text-zinc-400">
                        Widmark Hourly Rate (β_60): {extrapResult.beta_60_g_l_h} g/L/h
                      </p>
                    )}
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      SOFT / TIAFT Legal Evaluative Shield
                    </div>
                    {extrapResult.prosecutors_fallacy_shield}
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
